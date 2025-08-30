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
                    # Analyze flood risk for user's location
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
    Simplified flood risk analysis for Celery tasks
    """
    try:
        # Simulate environmental data based on location and time
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
        print(f"Error in GEE flood analysis: {e}")
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
            "note": "Fallback analysis due to GEE error"
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
