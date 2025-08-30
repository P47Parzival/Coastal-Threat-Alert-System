"""
Real-time Coastal Monitoring API using Clay v1.5
FastAPI backend for the coastal threat detection system
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
import json

from main import ClayCoastalMonitor

app = FastAPI(
    title="Clay v1.5 Coastal Monitoring API",
    description="Real-time coastal threat detection using geospatial foundation models",
    version="1.0.0"
)

# Enable CORS for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global monitor instance
monitor = ClayCoastalMonitor()

# Data models
class MonitoringRequest(BaseModel):
    location: str
    generate_report: bool = True
    visualize: bool = False

class ThreatAlert(BaseModel):
    threat_type: str
    probability: float
    severity: str
    description: str

class MonitoringResponse(BaseModel):
    alert_id: str
    timestamp: str
    location: str
    confidence: float
    threats: List[ThreatAlert]
    recommendations: List[str]
    status: str

class LocationStatus(BaseModel):
    location: str
    last_check: str
    status: str
    threat_count: int

# In-memory storage for demo (use database in production)
monitoring_history = []
active_locations = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the Clay model on startup"""
    print("🚀 Starting Clay v1.5 Coastal Monitoring API...")
    success = monitor.load_clay_model()
    if not success:
        raise Exception("Failed to load Clay v1.5 model")
    print("✅ Clay v1.5 model loaded successfully!")

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Clay v1.5 Coastal Monitoring API",
        "status": "operational",
        "model": "Clay v1.5 Foundation Model",
        "capabilities": [
            "Real-time threat detection",
            "Global coastal monitoring", 
            "Zero-shot analysis",
            "Multi-spectral processing"
        ]
    }

@app.post("/monitor", response_model=MonitoringResponse)
async def monitor_location(request: MonitoringRequest):
    """Monitor a specific coastal location"""
    try:
        # Run monitoring analysis
        result = monitor.monitor_location(
            location=request.location,
            generate_report=request.generate_report,
            visualize=request.visualize
        )
        
        # Convert threats to API format
        threats = []
        for threat_type, threat_data in result['threats'].items():
            threats.append(ThreatAlert(
                threat_type=threat_type,
                probability=threat_data['probability'],
                severity=threat_data['severity'],
                description=monitor.threat_categories[threat_type]
            ))
        
        # Create response
        report = result['report']
        response = MonitoringResponse(
            alert_id=report['alert_id'],
            timestamp=report['timestamp'],
            location=report['location'],
            confidence=report['analysis_confidence'],
            threats=threats,
            recommendations=report['recommendations'],
            status="alert" if threats else "clear"
        )
        
        # Store in history
        monitoring_history.append(response.dict())
        active_locations[request.location] = {
            "last_check": response.timestamp,
            "status": response.status,
            "threat_count": len(threats)
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/locations", response_model=List[LocationStatus])
async def get_monitored_locations():
    """Get status of all monitored locations"""
    locations = []
    for location, data in active_locations.items():
        locations.append(LocationStatus(
            location=location,
            last_check=data["last_check"],
            status=data["status"],
            threat_count=data["threat_count"]
        ))
    return locations

@app.get("/history")
async def get_monitoring_history(limit: int = 50):
    """Get recent monitoring history"""
    return monitoring_history[-limit:]

@app.get("/threats")
async def get_active_threats():
    """Get all currently active threats"""
    active_threats = []
    for record in monitoring_history[-20:]:  # Check last 20 records
        if record["status"] == "alert":
            active_threats.append({
                "location": record["location"],
                "timestamp": record["timestamp"],
                "threats": record["threats"]
            })
    return active_threats

@app.post("/batch-monitor")
async def batch_monitor_locations(locations: List[str], background_tasks: BackgroundTasks):
    """Monitor multiple locations in batch"""
    
    async def process_locations():
        results = []
        for location in locations:
            try:
                result = monitor.monitor_location(location, generate_report=True, visualize=False)
                
                # Convert to API format
                threats = []
                for threat_type, threat_data in result['threats'].items():
                    threats.append({
                        "threat_type": threat_type,
                        "probability": threat_data['probability'],
                        "severity": threat_data['severity'],
                        "description": monitor.threat_categories[threat_type]
                    })
                
                report = result['report']
                response_data = {
                    "alert_id": report['alert_id'],
                    "timestamp": report['timestamp'],
                    "location": report['location'],
                    "confidence": report['analysis_confidence'],
                    "threats": threats,
                    "recommendations": report['recommendations'],
                    "status": "alert" if threats else "clear"
                }
                
                results.append(response_data)
                monitoring_history.append(response_data)
                
                # Update active locations
                active_locations[location] = {
                    "last_check": response_data["timestamp"],
                    "status": response_data["status"],
                    "threat_count": len(threats)
                }
                
            except Exception as e:
                print(f"Error monitoring {location}: {e}")
                
        return results
    
    # Start background processing
    background_tasks.add_task(process_locations)
    
    return {
        "message": f"Started monitoring {len(locations)} locations",
        "locations": locations,
        "status": "processing"
    }

@app.get("/model-info")
async def get_model_info():
    """Get information about the Clay v1.5 model"""
    return {
        "model_name": "Clay v1.5",
        "model_type": "Geospatial Foundation Model",
        "embedding_dimension": 768,
        "spatial_resolution": "10m",
        "supported_sensors": ["Sentinel-1", "Sentinel-2", "DEM"],
        "capabilities": {
            "global_coverage": True,
            "zero_shot_learning": True,
            "multi_spectral": True,
            "temporal_analysis": True,
            "real_time_processing": True
        },
        "training_data": {
            "image_count": "1.2M",
            "date_range": "2017-2023",
            "global_coverage": True,
            "sensors": ["Sentinel-1 SAR", "Sentinel-2 Optical"]
        }
    }

@app.get("/threat-categories")
async def get_threat_categories():
    """Get available threat categories"""
    return monitor.threat_categories

# Example usage endpoints for demonstration
@app.post("/demo/mumbai")
async def demo_mumbai():
    """Demo endpoint for Mumbai coastal monitoring"""
    request = MonitoringRequest(location="Mumbai Coastal Area, India")
    return await monitor_location(request)

@app.post("/demo/miami")
async def demo_miami():
    """Demo endpoint for Miami Beach monitoring"""
    request = MonitoringRequest(location="Miami Beach, Florida, USA")
    return await monitor_location(request)

@app.post("/demo/barrier-reef")
async def demo_barrier_reef():
    """Demo endpoint for Great Barrier Reef monitoring"""
    request = MonitoringRequest(location="Great Barrier Reef, Australia")
    return await monitor_location(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
