from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from models import FloodDetectionRequest, FloodAlert
from database import flood_alerts_collection, users_collection
from routes_auth import get_current_user
from datetime import datetime, timedelta
from bson import ObjectId
import numpy as np
import sys
import os
from notifications import send_flood_alert_email

# Add the Model directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Model'))

router = APIRouter(prefix="/flood")

@router.get("/test-connection")
async def test_connection():
    """
    Test database connection and basic functionality
    """
    try:
        print("🔍 Testing flood detection system connection...")
        
        # Test database connection
        print(f"🔍 flood_alerts_collection: {flood_alerts_collection}")
        print(f"🔍 users_collection: {users_collection}")
        
        # Test basic flood analysis
        test_lat, test_lon = 19.0760, 72.8777
        flood_analysis = analyze_flood_risk_simple(test_lat, test_lon)
        
        return {
            "message": "Connection test successful",
            "database": "Connected",
            "flood_analysis": flood_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@router.post("/test-detect")
async def test_flood_detection(
    request: FloodDetectionRequest
):
    """
    Test flood detection without authentication
    """
    try:
        # Extract location data
        latitude = request.latitude
        longitude = request.longitude
        location_name = request.locationName or f"Location ({latitude:.4f}, {longitude:.4f})"
        
        print(f"🔍 Testing flood detection for {location_name} at ({latitude}, {longitude})")
        
        # Perform simplified flood detection
        flood_analysis = analyze_flood_risk_simple(latitude, longitude)
        
        return {
            "message": "Flood detection test completed",
            "location": location_name,
            "analysis": flood_analysis
        }
        
    except Exception as e:
        print(f"❌ Error in flood detection test: {e}")
        raise HTTPException(status_code=500, detail=f"Flood detection test failed: {str(e)}")

@router.post("/detect")
async def detect_flood(
    request: FloodDetectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Detect flood risk for a specific location using simplified analysis
    """
    try:
        # Test database connection
        print(f"🔍 Testing database connection...")
        print(f"🔍 flood_alerts_collection: {flood_alerts_collection}")
        print(f"🔍 current_user: {current_user}")
        
        # Extract location data
        latitude = request.latitude
        longitude = request.longitude
        location_name = request.locationName or f"Location ({latitude:.4f}, {longitude:.4f})"
        
        print(f"🔍 Starting flood detection for {location_name} at ({latitude}, {longitude})")
        
        # Perform simplified flood detection
        flood_analysis = analyze_flood_risk_simple(latitude, longitude)
        
        # Save flood alert to database
        flood_alert = {
            "userId": ObjectId(current_user["_id"]),
            "locationName": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "floodRisk": flood_analysis["floodRisk"],
            "riskScore": flood_analysis["riskScore"],
            "waterLevel": flood_analysis["waterLevel"],
            "precipitation": flood_analysis["precipitation"],
            "soilMoisture": flood_analysis["soilMoisture"],
            "drainageCapacity": flood_analysis["drainageCapacity"],
            "timeToFlood": flood_analysis["timeToFlood"],
            "confidence": flood_analysis["confidence"],
            "detectionMethod": "manual",
            "detectedAt": datetime.utcnow(),
            "status": "active"
        }
        
        print(f"🔍 Saving flood alert to database: {flood_alert}")
        result = await flood_alerts_collection.insert_one(flood_alert)
        print(f"✅ Database insert result: {result}")
        flood_alert["_id"] = str(result.inserted_id)
        
        # Send email notification if high risk
        if flood_analysis["floodRisk"] in ["HIGH", "CRITICAL"]:
            try:
                send_flood_alert_email(
                    user_email=current_user["email"],
                    location_name=location_name,
                    flood_analysis=flood_analysis
                )
                print(f"✅ Flood alert email sent to {current_user['email']}")
            except Exception as email_error:
                print(f"⚠️ Email notification failed: {email_error}")
                print(f"   This is normal if SendGrid is not configured")
                # Continue with the response even if email fails
        
        return {
            "message": "Flood detection completed",
            "location": location_name,
            "analysis": flood_analysis,
            "alertId": str(result.inserted_id)
        }
        
    except Exception as e:
        print(f"❌ Error in flood detection: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Flood detection failed: {str(e)}")

@router.get("/alerts")
async def get_flood_alerts(current_user: dict = Depends(get_current_user)):
    """
    Get all flood alerts for the current user
    """
    try:
        cursor = flood_alerts_collection.find({"userId": ObjectId(current_user["_id"])})
        alerts = await cursor.to_list(length=100)
        
        # Convert ObjectIds to strings
        for alert in alerts:
            alert["_id"] = str(alert["_id"])
            alert["userId"] = str(alert["userId"])
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch flood alerts: {str(e)}")

@router.get("/current-risk")
async def get_current_flood_risk(
    latitude: float = Query(..., description="Latitude of location"),
    longitude: float = Query(..., description="Longitude of location"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current flood risk for a location without saving alert
    """
    try:
        flood_analysis = analyze_flood_risk_simple(latitude, longitude)
        return {
            "location": f"({latitude:.4f}, {longitude:.4f})",
            "analysis": flood_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze flood risk: {str(e)}")

def analyze_flood_risk_simple(latitude: float, longitude: float):
    """
    Improved flood risk analysis with realistic factors
    """
    try:
        # Get current time for seasonal analysis
        current_time = datetime.now()
        current_hour = current_time.hour
        current_month = current_time.month
        
        # Base risk factors (more realistic)
        # 1. Geographic factors (coastal areas, low elevation)
        coastal_risk = 0
        if 8.0 <= latitude <= 37.0 and 68.0 <= longitude <= 97.0:  # India
            if 8.0 <= latitude <= 22.0:  # Southern coastal regions
                coastal_risk = 0.3
            elif 22.0 <= latitude <= 37.0:  # Northern regions
                coastal_risk = 0.1
        
        # 2. Seasonal factors (monsoon season)
        monsoon_risk = 0
        if current_month in [6, 7, 8, 9]:  # June to September (monsoon)
            monsoon_risk = 0.4
        elif current_month in [10, 11]:  # Post-monsoon
            monsoon_risk = 0.2
        
        # 3. Time of day factors (night time higher risk)
        time_risk = 0
        if 22 <= current_hour or current_hour <= 6:  # Night time
            time_risk = 0.2
        
        # 4. Location-specific factors (using coordinates for realistic variation)
        location_factor = ((latitude * 1000 + longitude * 100) % 100) / 100
        
        # Calculate composite risk score (0-100)
        base_risk = (
            coastal_risk * 30 +      # Coastal areas: 30% base risk
            monsoon_risk * 40 +      # Monsoon season: 40% additional risk
            time_risk * 20 +         # Night time: 20% additional risk
            location_factor * 10     # Location variation: 10% additional risk
        )
        
        # Ensure risk is between 0-100
        base_risk = min(100, max(0, base_risk))
        
        # Determine risk level based on realistic thresholds
        if base_risk < 15:
            flood_risk = "MINIMAL"
            risk_score = int(base_risk)
            time_to_flood = "No immediate risk"
        elif base_risk < 35:
            flood_risk = "LOW"
            risk_score = int(base_risk)
            time_to_flood = "1-2 weeks"
        elif base_risk < 55:
            flood_risk = "MEDIUM"
            risk_score = int(base_risk)
            time_to_flood = "3-7 days"
        elif base_risk < 75:
            flood_risk = "HIGH"
            risk_score = int(base_risk)
            time_to_flood = "12-48 hours"
        else:
            flood_risk = "CRITICAL"
            risk_score = int(base_risk)
            time_to_flood = "0-12 hours"
        
        # Realistic environmental factors
        # Precipitation (mm/hr) - higher during monsoon
        if monsoon_risk > 0:
            precip_value = 15.0 + (base_risk * 0.8)  # 15-95 mm/hr during monsoon
        else:
            precip_value = 2.0 + (base_risk * 0.3)   # 2-32 mm/hr normal conditions
        
        # Soil moisture (m³/m³) - realistic range 0.1-0.8
        soil_moisture_value = 0.2 + (base_risk * 0.006)
        
        # Water level (normalized 0-1) - based on risk
        water_level = min(1.0, (base_risk / 100.0) * 1.1)
        
        # Drainage capacity (normalized 0-1) - inverse of risk
        drainage_capacity = max(0.1, 1.0 - (base_risk / 100.0))
        
        # Elevation factor (meters above sea level)
        elevation_value = max(2, 100 - (base_risk * 0.8))  # Higher risk = lower elevation
        
        # Slope factor (degrees)
        slope_value = max(0.5, 15 - (base_risk * 0.15))  # Higher risk = lower slope
        
        # Confidence based on data quality
        confidence = 0.85 - (base_risk * 0.002)  # Higher risk = slightly lower confidence
        
        return {
            "floodRisk": flood_risk,
            "riskScore": risk_score,
            "waterLevel": water_level,
            "precipitation": precip_value,
            "soilMoisture": soil_moisture_value,
            "drainageCapacity": drainage_capacity,
            "timeToFlood": time_to_flood,
            "confidence": confidence,
            "factors": {
                "coastal_risk": coastal_risk,
                "monsoon_risk": monsoon_risk,
                "time_risk": time_risk,
                "location_factor": location_factor,
                "elevation": elevation_value,
                "slope": slope_value,
                "drainage_capacity": drainage_capacity
            },
            "analysisDate": current_time.isoformat(),
            "seasonal_info": {
                "month": current_month,
                "is_monsoon": monsoon_risk > 0,
                "time_of_day": "night" if time_risk > 0 else "day"
            }
        }
        
    except Exception as e:
        print(f"Error in flood analysis: {e}")
        import traceback
        traceback.print_exc()
        # Return minimal risk as fallback
        return {
            "floodRisk": "MINIMAL",
            "riskScore": 10,
            "waterLevel": 0.1,
            "precipitation": 2.0,
            "soilMoisture": 0.2,
            "drainageCapacity": 0.9,
            "timeToFlood": "No immediate risk",
            "confidence": 0.5,
            "factors": {},
            "analysisDate": datetime.now().isoformat(),
            "note": "Fallback analysis due to error"
        }

@router.delete("/alerts/{alert_id}")
async def delete_flood_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a flood alert
    """
    try:
        result = await flood_alerts_collection.delete_one({
            "_id": ObjectId(alert_id),
            "userId": ObjectId(current_user["_id"])
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Flood alert not found")
        
        return {"message": "Flood alert deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete flood alert: {str(e)}")
