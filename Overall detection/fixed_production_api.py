"""
Fixed Production API - Robust handling of Earth Engine issues
Works with or without authentication, provides graceful fallbacks
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
from datetime import datetime

# Import fixed monitor
try:
    from fixed_production_main import FixedClayMonitor
    MONITOR_AVAILABLE = True
except ImportError:
    MONITOR_AVAILABLE = False

app = FastAPI(
    title="Clay v1.5 Fixed Coastal Monitoring API",
    description="Robust coastal monitoring with graceful fallbacks for authentication issues",
    version="2.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global monitor instance
if MONITOR_AVAILABLE:
    monitor = FixedClayMonitor()
else:
    monitor = None

# Data models
class RobustMonitoringRequest(BaseModel):
    location: str
    prefer_real_data: bool = True
    generate_report: bool = True
    create_visualization: bool = False

class SystemStatusResponse(BaseModel):
    status: str
    mode: str
    earth_engine_available: bool
    clay_model_available: bool
    api_version: str
    timestamp: str
    features_available: List[str]

class MonitoringResponse(BaseModel):
    success: bool
    alert_id: str
    timestamp: str
    location: str
    mode: str
    data_source: str
    real_data_used: bool
    threats_detected: int
    recommendations: List[str]
    status: str
    error_message: Optional[str] = None

# Storage
monitoring_results = []
system_logs = []

@app.on_event("startup")
async def startup_event():
    """Initialize the fixed monitoring system"""
    print("🚀 Starting Fixed Clay v1.5 Coastal Monitoring API...")
    
    if MONITOR_AVAILABLE and monitor:
        status = monitor.get_system_status()
        print(f"✅ Monitor initialized in {status['mode']} mode")
        
        system_logs.append({
            "timestamp": datetime.now().isoformat(),
            "event": "startup",
            "mode": status['mode'],
            "ee_available": status['ee_available']
        })
    else:
        print("⚠️  Monitor not available, running in minimal mode")
        
        system_logs.append({
            "timestamp": datetime.now().isoformat(),
            "event": "startup",
            "mode": "minimal",
            "issue": "Monitor import failed"
        })
    
    print("🌊 Fixed Clay API ready!")

@app.get("/")
async def root():
    """API health check"""
    if monitor:
        status = monitor.get_system_status()
        features = []
        
        if status['clay_available']:
            features.append("Clay v1.5 foundation model")
        if status['ee_available']:
            features.append("Real satellite data (Google Earth Engine)")
        features.append("Simulated data demonstration")
        features.append("Robust error handling")
        features.append("Graceful fallbacks")
        
        return {
            "message": "Clay v1.5 Fixed Coastal Monitoring API",
            "status": "operational",
            "version": "2.1.0",
            "mode": status['mode'],
            "features": features,
            "robust_deployment": True
        }
    else:
        return {
            "message": "Clay v1.5 Minimal API",
            "status": "limited",
            "version": "2.1.0",
            "mode": "minimal",
            "features": ["Basic health check"],
            "note": "Full features require proper setup"
        }

@app.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get detailed system status"""
    if monitor:
        status = monitor.get_system_status()
        
        features = []
        if status['clay_available']:
            features.append("Clay v1.5 AI model")
        if status['ee_available']:
            features.append("Real satellite data")
        features.extend(["Threat detection", "Report generation", "Error handling"])
        
        return SystemStatusResponse(
            status="operational",
            mode=status['mode'],
            earth_engine_available=status['ee_available'],
            clay_model_available=status['clay_available'],
            api_version="2.1.0",
            timestamp=status['timestamp'],
            features_available=features
        )
    else:
        return SystemStatusResponse(
            status="minimal",
            mode="minimal",
            earth_engine_available=False,
            clay_model_available=False,
            api_version="2.1.0",
            timestamp=datetime.now().isoformat(),
            features_available=["Basic API functionality"]
        )

@app.post("/monitor/robust", response_model=MonitoringResponse)
async def monitor_location_robust(request: RobustMonitoringRequest):
    """Robust monitoring endpoint with graceful error handling"""
    try:
        if not monitor:
            # Minimal fallback response
            return MonitoringResponse(
                success=True,
                alert_id=f"MINIMAL_{int(datetime.now().timestamp())}",
                timestamp=datetime.now().isoformat(),
                location=request.location,
                mode="minimal",
                data_source="API fallback",
                real_data_used=False,
                threats_detected=0,
                recommendations=[
                    "System running in minimal mode",
                    "Install dependencies for full functionality",
                    "Ready for proper deployment"
                ],
                status="demo",
                error_message="Full monitoring system not available"
            )
        
        # Run monitoring
        result = monitor.monitor_location(
            location=request.location,
            generate_report=request.generate_report,
            visualize=request.create_visualization
        )
        
        if result['success']:
            analysis = result['result']
            
            # Extract threats
            threats = analysis.get('threats', {})
            threat_count = len(threats)
            
            # Extract recommendations
            recommendations = []
            if 'report' in analysis and 'recommendations' in analysis['report']:
                recommendations = analysis['report']['recommendations']
            else:
                recommendations = ["Continue monitoring", "System operational"]
            
            # Create response
            response = MonitoringResponse(
                success=True,
                alert_id=analysis.get('report', {}).get('alert_id', f"ROBUST_{int(datetime.now().timestamp())}"),
                timestamp=datetime.now().isoformat(),
                location=request.location,
                mode=result['mode'],
                data_source=result['data_source'],
                real_data_used=result['real_data'],
                threats_detected=threat_count,
                recommendations=recommendations[:5],  # Limit to 5 recommendations
                status="alert" if threat_count > 0 else "clear"
            )
            
            # Store result
            monitoring_results.append(response.dict())
            
            # Log successful monitoring
            system_logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": "monitoring_success",
                "location": request.location,
                "mode": result['mode'],
                "threats": threat_count
            })
            
            return response
        
        else:
            # Handle monitoring failure
            return MonitoringResponse(
                success=False,
                alert_id=f"ERROR_{int(datetime.now().timestamp())}",
                timestamp=datetime.now().isoformat(),
                location=request.location,
                mode="error",
                data_source="none",
                real_data_used=False,
                threats_detected=0,
                recommendations=["System error occurred", "Check system logs", "Retry monitoring"],
                status="error",
                error_message="Monitoring process failed"
            )
            
    except Exception as e:
        # Ultimate fallback
        error_response = MonitoringResponse(
            success=False,
            alert_id=f"EXCEPTION_{int(datetime.now().timestamp())}",
            timestamp=datetime.now().isoformat(),
            location=request.location,
            mode="exception",
            data_source="none",
            real_data_used=False,
            threats_detected=0,
            recommendations=["API exception occurred", "Check system configuration"],
            status="error",
            error_message=str(e)
        )
        
        # Log exception
        system_logs.append({
            "timestamp": datetime.now().isoformat(),
            "event": "api_exception",
            "location": request.location,
            "error": str(e)
        })
        
        return error_response

@app.get("/monitor/history")
async def get_monitoring_history(limit: int = Query(20, description="Number of records")):
    """Get monitoring history"""
    recent_results = monitoring_results[-limit:] if monitoring_results else []
    
    # Calculate statistics
    total_locations = len(set(r['location'] for r in recent_results))
    total_threats = sum(r['threats_detected'] for r in recent_results)
    real_data_count = sum(1 for r in recent_results if r['real_data_used'])
    
    return {
        "history": recent_results,
        "statistics": {
            "total_requests": len(recent_results),
            "unique_locations": total_locations,
            "total_threats_detected": total_threats,
            "real_data_requests": real_data_count,
            "demo_requests": len(recent_results) - real_data_count
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/system/logs")
async def get_system_logs(limit: int = Query(10, description="Number of log entries")):
    """Get system logs for debugging"""
    recent_logs = system_logs[-limit:] if system_logs else []
    
    return {
        "logs": recent_logs,
        "total_logs": len(system_logs),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/test/locations")
async def test_multiple_locations():
    """Test monitoring multiple locations"""
    test_locations = [
        "Mumbai Coastal Area, India",
        "Miami Beach, Florida, USA", 
        "Chennai Coast, India"
    ]
    
    results = []
    
    for location in test_locations:
        try:
            request = RobustMonitoringRequest(location=location, create_visualization=False)
            result = await monitor_location_robust(request)
            results.append({
                "location": location,
                "success": result.success,
                "mode": result.mode,
                "threats": result.threats_detected,
                "status": result.status
            })
        except Exception as e:
            results.append({
                "location": location,
                "success": False,
                "error": str(e)
            })
    
    return {
        "test_results": results,
        "total_locations": len(test_locations),
        "successful_tests": sum(1 for r in results if r.get('success')),
        "timestamp": datetime.now().isoformat()
    }

# Demo endpoints that always work
@app.post("/demo/mumbai")
async def demo_mumbai():
    """Guaranteed working demo for Mumbai"""
    request = RobustMonitoringRequest(location="Mumbai Coastal Area, India")
    return await monitor_location_robust(request)

@app.post("/demo/miami")
async def demo_miami():
    """Guaranteed working demo for Miami"""
    request = RobustMonitoringRequest(location="Miami Beach, Florida, USA")
    return await monitor_location_robust(request)

@app.get("/health")
async def health_check():
    """Simple health check that always works"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_version": "2.1.0",
        "message": "Clay v1.5 Fixed API is operational"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Fixed Clay v1.5 API...")
    print("🔧 Handles all authentication and setup issues")
    print("🌐 Server will start at: http://localhost:8002")
    print("📖 API docs available at: http://localhost:8002/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
