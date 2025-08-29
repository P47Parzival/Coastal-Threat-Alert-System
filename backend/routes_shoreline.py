from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from models import ShorelineAnalysisRequest
from database import shoreline_collection
from routes_auth import get_current_user
from datetime import datetime, timedelta
from bson import ObjectId
import numpy as np
import sys
import os

# Add the Model directory to Python path to import coastal detection
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Model'))

router = APIRouter(prefix="/shoreline")

@router.post("/analyze")
async def analyze_shoreline(
    request: ShorelineAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze shoreline for erosion risk using the coastal detection model
    """
    try:
        # Import the coastal detection functions
        from coastal_detection import (
            analyze_coastal_threats,
            generate_threat_alert,
            create_coastal_monitoring_dashboard
        )
        
        # Extract shoreline path coordinates from GeoJSON
        shoreline_coords = request.shorelinePath['geometry']['coordinates']
        
        # Convert coordinates to shoreline positions (simplified for demo)
        # In a real implementation, you'd use actual satellite data or historical measurements
        shoreline_positions = []
        timestamps = []
        
        # Generate synthetic shoreline change data based on the drawn path
        # This simulates what would come from actual satellite imagery analysis
        base_position = 100.0  # meters from reference point
        start_date = datetime(2020, 1, 1)
        
        for i in range(12):  # 12 months of data
            # Add trend (gradual erosion)
            trend = -0.3 * i  # 0.3m erosion per month
            
            # Add seasonal variation
            seasonal = 1.5 * np.sin(2 * np.pi * i / 12)  # Annual cycle
            
            # Add random noise
            noise = np.random.normal(0, 0.8)
            
            position = base_position + trend + seasonal + noise
            shoreline_positions.append(position)
            
            # Add timestamp
            timestamp = start_date + timedelta(days=30*i)
            timestamps.append(timestamp)
        
        # Analyze coastal threats using the coastal detection model
        threat_analysis = analyze_coastal_threats(shoreline_positions, timestamps)
        alerts = generate_threat_alert(threat_analysis)
        
        # Calculate additional metrics
        total_change = shoreline_positions[-1] - shoreline_positions[0]
        avg_erosion_rate = np.mean(threat_analysis['erosion_rate']) if threat_analysis['erosion_rate'] else 0
        
        # Determine threat level
        if avg_erosion_rate < -0.08:
            threat_level = 'HIGH'
            flood_risk = 'HIGH'
        elif avg_erosion_rate < -0.04:
            threat_level = 'MEDIUM'
            flood_risk = 'MEDIUM'
        elif avg_erosion_rate < 0:
            threat_level = 'LOW'
            flood_risk = 'LOW'
        else:
            threat_level = 'STABLE'
            flood_risk = 'LOW'
        
        # Calculate risk score (0-10)
        risk_score = min(10, abs(avg_erosion_rate) * 100)
        
        # Generate recommendations based on threat level
        recommendations = []
        if threat_level == 'HIGH':
            recommendations = [
                "Immediate deployment of emergency coastal protection measures",
                "Increase monitoring frequency to daily",
                "Conduct detailed bathymetric and topographic surveys",
                "Implement hard engineering solutions (seawalls, groynes)",
                "Evacuation planning for high-risk areas"
            ]
        elif threat_level == 'MEDIUM':
            recommendations = [
                "Enhanced monitoring with weekly assessments",
                "Consider soft engineering solutions (beach nourishment)",
                "Monitor weather patterns and storm events",
                "Develop coastal protection strategy",
                "Community awareness and preparedness programs"
            ]
        elif threat_level == 'LOW':
            recommendations = [
                "Continue monthly monitoring schedule",
                "Document baseline conditions for future reference",
                "Monitor for any acceleration in erosion rates",
                "Maintain existing coastal vegetation",
                "Regular assessment of protection measures"
            ]
        else:  # STABLE
            recommendations = [
                "Maintain current monitoring frequency",
                "Continue data collection for trend analysis",
                "Monitor for any changes in coastal dynamics",
                "Preserve existing coastal ecosystems",
                "Regular review of coastal management policies"
            ]
        
        # Create analysis result
        analysis_result = {
            "threatLevel": threat_level,
            "erosionRate": avg_erosion_rate,
            "riskScore": risk_score,
            "recommendations": recommendations,
            "shorelineChange": total_change,
            "floodRisk": flood_risk,
            "analysisDate": datetime.now().isoformat(),
            "monitoringPeriod": f"{timestamps[0].strftime('%Y-%m-%d')} to {timestamps[-1].strftime('%Y-%m-%d')}",
            "dataPoints": len(shoreline_positions)
        }
        
        # Save to database
        shoreline_doc = {
            "userId": ObjectId(current_user["_id"]),
            "name": request.name,
            "description": request.description,
            "shorelinePath": request.shorelinePath,
            "monitoringFrequency": request.monitoringFrequency,
            "confidenceThreshold": request.confidenceThreshold,
            "emailAlerts": request.emailAlerts,
            "inAppNotifications": request.inAppNotifications,
            "analysisResult": analysis_result,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = shoreline_collection.insert_one(shoreline_doc)
        shoreline_doc["_id"] = str(result.inserted_id)
        
        return analysis_result
        
    except ImportError as e:
        print(f"Error importing coastal detection module: {e}")
        # Fallback to simplified analysis if coastal detection module not available
        return await analyze_shoreline_fallback(request, current_user)
    except Exception as e:
        print(f"Error in shoreline analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Shoreline analysis failed: {str(e)}")


async def analyze_shoreline_fallback(request: ShorelineAnalysisRequest, current_user: dict):
    """
    Fallback analysis method if coastal detection module is not available
    """
    # Simplified analysis using basic geometric calculations
    shoreline_coords = request.shorelinePath['geometry']['coordinates']
    
    # Calculate basic metrics from the drawn path
    path_length = len(shoreline_coords)
    
    # Generate synthetic analysis based on path characteristics
    if path_length < 10:
        threat_level = 'LOW'
        erosion_rate = -0.02
    elif path_length < 20:
        threat_level = 'MEDIUM'
        erosion_rate = -0.05
    else:
        threat_level = 'HIGH'
        erosion_rate = -0.08
    
    # Determine flood risk
    if threat_level == 'HIGH':
        flood_risk = 'HIGH'
        recommendations = [
            "High erosion detected - immediate action required",
            "Increase monitoring frequency",
            "Consider protective measures"
        ]
    elif threat_level == 'MEDIUM':
        flood_risk = 'MEDIUM'
        recommendations = [
            "Moderate erosion - enhanced monitoring recommended",
            "Monitor for changes",
            "Consider soft protection measures"
        ]
    else:
        flood_risk = 'LOW'
        recommendations = [
            "Low erosion - continue monitoring",
            "Maintain current conditions",
            "Document baseline for future reference"
        ]
    
    risk_score = min(10, abs(erosion_rate) * 100)
    total_change = erosion_rate * 365  # Annual change
    
    return {
        "threatLevel": threat_level,
        "erosionRate": erosion_rate,
        "riskScore": risk_score,
        "recommendations": recommendations,
        "shorelineChange": total_change,
        "floodRisk": flood_risk,
        "analysisDate": datetime.now().isoformat(),
        "monitoringPeriod": "Fallback analysis",
        "dataPoints": path_length,
        "note": "Analysis performed using fallback method - coastal detection module not available"
    }


@router.get("/")
async def get_shoreline_analyses(current_user: dict = Depends(get_current_user)):
    """
    Get all shoreline analyses for the current user
    """
    try:
        cursor = shoreline_collection.find({"userId": ObjectId(current_user["_id"])})
        shorelines = await cursor.to_list(length=100)
        
        # Convert ObjectIds to strings
        for shoreline in shorelines:
            shoreline["_id"] = str(shoreline["_id"])
            shoreline["userId"] = str(shoreline["userId"])
        
        return shorelines
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch shoreline analyses: {str(e)}")


@router.get("/{shoreline_id}")
async def get_shoreline_analysis(
    shoreline_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific shoreline analysis by ID
    """
    try:
        shoreline = await shoreline_collection.find_one({
            "_id": ObjectId(shoreline_id),
            "userId": ObjectId(current_user["_id"])
        })
        
        if not shoreline:
            raise HTTPException(status_code=404, detail="Shoreline analysis not found")
        
        shoreline["_id"] = str(shoreline["_id"])
        shoreline["userId"] = str(shoreline["userId"])
        
        return shoreline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch shoreline analysis: {str(e)}")


@router.delete("/{shoreline_id}")
async def delete_shoreline_analysis(
    shoreline_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a shoreline analysis
    """
    try:
        result = await shoreline_collection.delete_one({
            "_id": ObjectId(shoreline_id),
            "userId": ObjectId(current_user["_id"])
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Shoreline analysis not found")
        
        return {"message": "Shoreline analysis deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete shoreline analysis: {str(e)}")
