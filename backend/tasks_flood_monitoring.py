# backend/tasks_flood_monitoring.py

from celery_config import celery_app
from celery.schedules import crontab
from notifications import send_flood_alert_email
from database import sync_users_collection, sync_flood_alerts_collection
from bson import ObjectId
from datetime import datetime, timedelta
import numpy as np
import sys
import os

# Add the Model directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Model'))

@celery_app.task
def monitor_all_users_for_flood():
    """
    Automatically monitor all users for flood risks every 3 hours
    """
    print("🌊 Starting automatic flood monitoring for all users...")
    
    try:
        # Get all active users
        users = list(sync_users_collection.find({}))
        print(f"📊 Found {len(users)} users to monitor")
        
        flood_alerts_created = 0
        
        for user in users:
            try:
                # Get user's last known location or use default
                user_location = get_user_location(user)
                
                if user_location:
                    # Analyze flood risk for user's location using GEE
                    try:
                        from routes_flood import analyze_flood_risk_gee_simple
                        flood_analysis = analyze_flood_risk_gee_simple(
                            user_location['latitude'], 
                            user_location['longitude']
                        )
                        print(f"🌍 GEE analysis completed for {user.get('email', 'Unknown')}")
                    except Exception as gee_error:
                        print(f"⚠️ GEE analysis failed, falling back to synthetic: {gee_error}")
                        flood_analysis = analyze_flood_risk_simple(
                            user_location['latitude'], 
                            user_location['longitude']
                        )
                    
                    # Check if flood risk is significant enough to create alert
                    if flood_analysis['floodRisk'] in ['HIGH', 'CRITICAL']:
                        # Check if we already have a recent alert for this user
                        existing_alert = sync_flood_alerts_collection.find_one({
                            "userId": user["_id"],
                            "floodRisk": {"$in": ["HIGH", "CRITICAL"]},
                            "detectedAt": {"$gte": datetime.utcnow() - timedelta(hours=6)}
                        })
                        
                        if not existing_alert:
                            # Create new flood alert
                            flood_alert = {
                                "userId": user["_id"],
                                "locationName": user_location.get('name', 'User Location'),
                                "latitude": user_location['latitude'],
                                "longitude": user_location['longitude'],
                                "floodRisk": flood_analysis["floodRisk"],
                                "riskScore": flood_analysis["riskScore"],
                                "waterLevel": flood_analysis["waterLevel"],
                                "precipitation": flood_analysis["precipitation"],
                                "soilMoisture": flood_analysis["soilMoisture"],
                                "drainageCapacity": flood_analysis["drainageCapacity"],
                                "timeToFlood": flood_analysis["timeToFlood"],
                                "confidence": flood_analysis["confidence"],
                                "detectionMethod": "automatic",
                                "detectedAt": datetime.utcnow(),
                                "status": "active"
                            }
                            
                            result = sync_flood_alerts_collection.insert_one(flood_alert)
                            flood_alerts_created += 1
                            
                            print(f"🚨 Flood alert created for user {user.get('email', 'Unknown')}: {flood_analysis['floodRisk']} risk")
                            
                            # Send email notification
                            send_flood_alert_email(
                                user_email=user['email'],
                                location_name=user_location.get('name', 'Your Location'),
                                flood_analysis=flood_analysis
                            )
                        else:
                            print(f"⚠️ Recent flood alert already exists for user {user.get('email', 'Unknown')}")
                    else:
                        print(f"✅ No significant flood risk for user {user.get('email', 'Unknown')}: {flood_analysis['floodRisk']}")
                
            except Exception as e:
                print(f"❌ Error monitoring user {user.get('email', 'Unknown')}: {e}")
                continue
        
        print(f"🎯 Automatic flood monitoring completed. Created {flood_alerts_created} new alerts.")
        return f"Flood monitoring completed. {flood_alerts_created} alerts created."
        
    except Exception as e:
        print(f"❌ Error in automatic flood monitoring: {e}")
        return f"Flood monitoring failed: {str(e)}"

def get_user_location(user):
    """
    Get user's location for flood monitoring
    In a real implementation, this would come from:
    - User's saved location preferences
    - GPS coordinates from mobile app
    - Last known location
    - Default location based on user profile
    """
    try:
        # For demo purposes, use a default location for each user
        # In production, you'd get this from user preferences or device location
        
        # Generate a consistent location based on user ID
        user_id_hash = hash(str(user["_id"]))
        
        # Use hash to generate coordinates within India
        latitude = 20.0 + (user_id_hash % 10)  # 20-30°N
        longitude = 70.0 + (user_id_hash % 20)  # 70-90°E
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "name": f"Location for {user.get('name', user.get('email', 'User'))}"
        }
        
    except Exception as e:
        print(f"Error getting user location: {e}")
        # Return a default location (Mumbai)
        return {
            "latitude": 19.0760,
            "longitude": 72.8777,
            "name": "Default Location (Mumbai)"
        }

def analyze_flood_risk_simple(latitude: float, longitude: float):
    """
    Improved flood risk analysis for Celery tasks
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

@celery_app.task
def cleanup_old_flood_alerts():
    """
    Clean up old flood alerts (older than 7 days)
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        result = sync_flood_alerts_collection.delete_many({
            "detectedAt": {"$lt": cutoff_date}
        })
        
        print(f"🧹 Cleaned up {result.deleted_count} old flood alerts")
        return f"Cleanup completed. {result.deleted_count} alerts removed."
        
    except Exception as e:
        print(f"Error cleaning up old flood alerts: {e}")
        return f"Cleanup failed: {str(e)}"
