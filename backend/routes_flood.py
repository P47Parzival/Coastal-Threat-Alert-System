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
            except Exception as email_error:
                print(f"⚠️ Email notification failed: {email_error}")
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
    Simplified flood risk analysis for testing
    """
    try:
        # Generate synthetic risk based on location and time
        base_risk = (latitude + longitude + datetime.now().hour) % 100
        
        if base_risk < 20:
            flood_risk = "MINIMAL"
            risk_score = 15
            time_to_flood = "No immediate risk"
        elif base_risk < 40:
            flood_risk = "LOW"
            risk_score = 35
            time_to_flood = "3-7 days"
        elif base_risk < 60:
            flood_risk = "MEDIUM"
            risk_score = 55
            time_to_flood = "1-3 days"
        elif base_risk < 80:
            flood_risk = "HIGH"
            risk_score = 75
            time_to_flood = "6-24 hours"
        else:
            flood_risk = "CRITICAL"
            risk_score = 90
            time_to_flood = "0-6 hours"
        
        # Simulate environmental factors
        precip_value = 30.0 + (base_risk * 0.5)  # Higher risk = more precipitation
        soil_moisture_value = 0.5 + (base_risk * 0.005)  # Higher risk = more soil moisture
        water_coverage_value = 0.1 + (base_risk * 0.002)  # Higher risk = more water coverage
        elevation_value = max(5, 50 - (base_risk * 0.5))  # Higher risk = lower elevation
        slope_value = max(1, 10 - (base_risk * 0.1))  # Higher risk = lower slope
        
        # Calculate risk factors
        water_level = min(1.0, (base_risk / 100.0) * 1.2)
        drainage_capacity = max(0.0, 1.0 - (base_risk / 100.0))
        
        return {
            "floodRisk": flood_risk,
            "riskScore": risk_score,
            "waterLevel": water_level,
            "precipitation": precip_value,
            "soilMoisture": soil_moisture_value,
            "drainageCapacity": drainage_capacity,
            "timeToFlood": time_to_flood,
            "confidence": 0.75,
            "factors": {
                "water_level": water_level,
                "drainage_capacity": drainage_capacity,
                "confidence": 0.75,
                "precip_factor": precip_value / 100.0,
                "soil_factor": soil_moisture_value,
                "water_factor": water_coverage_value,
                "elevation_factor": max(0, 1 - (elevation_value / 100.0)),
                "slope_factor": max(0, 1 - (slope_value / 45.0))
            },
            "analysisDate": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error in flood analysis: {e}")
        # Return minimal risk as fallback
        return {
            "floodRisk": "MINIMAL",
            "riskScore": 10,
            "waterLevel": 0.1,
            "precipitation": 20.0,
            "soilMoisture": 0.4,
            "drainageCapacity": 0.9,
            "timeToFlood": "No immediate risk",
            "confidence": 0.5,
            "factors": {
                "water_level": 0.1,
                "drainage_capacity": 0.9,
                "confidence": 0.5
            },
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
