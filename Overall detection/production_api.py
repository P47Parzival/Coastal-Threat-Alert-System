"""
Updated FastAPI with Google Earth Engine real-time integration
Production-ready API endpoints for coastal monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
import json
import os

# Import production monitor
try:
    from production_main import ProductionCoastalMonitor
    PRODUCTION_AVAILABLE = True
except ImportError:
    from main import ClayCoastalMonitor
    PRODUCTION_AVAILABLE = False

app = FastAPI(
    title="Clay v1.5 Production Coastal Monitoring API",
    description="Real-time coastal threat detection using Google Earth Engine + Clay v1.5",
    version="2.0.0"
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
if PRODUCTION_AVAILABLE:
    monitor = ProductionCoastalMonitor(use_real_data=True)
else:
    monitor = ClayCoastalMonitor()
    monitor.load_clay_model()

# Enhanced data models
class ProductionMonitoringRequest(BaseModel):
    location: str
    days_back: int = 30
    use_real_data: bool = True
    generate_report: bool = True
    create_visualization: bool = False

class SatelliteMetadata(BaseModel):
    sensor: str
    date: str
    cloud_cover: Optional[float] = None
    data_age_days: Optional[int] = None

class ProductionMonitoringResponse(BaseModel):
    alert_id: str
    timestamp: str
    location: str
    mode: str  # 'production' or 'demo'
    data_source: str
    real_data: bool
    confidence: float
    threats: List[dict]
    recommendations: List[str]
    satellite_metadata: Optional[dict] = None
    visualization_available: bool = False
    status: str

class SystemStatus(BaseModel):
    mode: str
    gee_available: bool
    gee_authenticated: bool
    real_data_enabled: bool
    clay_model_status: str
    data_sources: List[str]
    timestamp: str

# Storage for production monitoring
monitoring_history = []
system_alerts = []

@app.on_event("startup")
async def startup_event():
    """Initialize the production monitoring system"""
    print("🚀 Starting Production Coastal Monitoring API...")
    
    if PRODUCTION_AVAILABLE:
        status = monitor.get_system_status()
        print(f"✅ Production system initialized in {status['mode']} mode")
        print(f"🛰️  Data sources: {', '.join(status['data_sources'])}")
    else:
        print("⚠️  Running in fallback demo mode")
    
    print("🌊 Clay v1.5 Production API ready!")

@app.get("/")
async def root():
    """API health check with production capabilities"""
    status = monitor.get_system_status() if hasattr(monitor, 'get_system_status') else {
        'mode': 'demo',
        'gee_available': False,
        'real_data_enabled': False
    }
    
    return {
        "message": "Clay v1.5 Production Coastal Monitoring API",
        "status": "operational",
        "version": "2.0.0",
        "mode": status['mode'],
        "features": [
            "Real-time satellite data (Google Earth Engine)",
            "Clay v1.5 foundation model",
            "Global coastal monitoring",
            "Production-ready deployment",
            "Zero-shot threat detection"
        ],
        "real_data_available": status.get('real_data_enabled', False)
    }

@app.get("/system/status", response_model=SystemStatus)
async def get_system_status():
    """Get detailed system status"""
    if hasattr(monitor, 'get_system_status'):
        status = monitor.get_system_status()
        return SystemStatus(
            mode=status['mode'],
            gee_available=status.get('gee_available', False),
            gee_authenticated=status.get('gee_authenticated', False),
            real_data_enabled=status['real_data_enabled'],
            clay_model_status=status['clay_model_status'],
            data_sources=status['data_sources'],
            timestamp=status['timestamp']
        )
    else:
        return SystemStatus(
            mode="demo",
            gee_available=False,
            gee_authenticated=False,
            real_data_enabled=False,
            clay_model_status="loaded",
            data_sources=["Simulated data"],
            timestamp=datetime.now().isoformat()
        )

@app.post("/monitor/production", response_model=ProductionMonitoringResponse)
async def monitor_location_production(request: ProductionMonitoringRequest):
    """Monitor location with production-grade real satellite data"""
    try:
        if hasattr(monitor, 'monitor_location'):
            # Production monitor
            result = monitor.monitor_location(
                location=request.location,
                days_back=request.days_back,
                generate_report=request.generate_report,
                visualize=request.create_visualization
            )
        else:
            # Fallback demo monitor
            result = {
                'success': True,
                'mode': 'demo',
                'data_source': 'Simulated',
                'real_data': False,
                'result': monitor.monitor_location(
                    location=request.location,
                    generate_report=request.generate_report,
                    visualize=request.create_visualization
                )
            }
        
        if not result['success']:
            raise HTTPException(status_code=500, detail="Monitoring failed")
        
        # Extract data based on mode
        if result['mode'] == 'production':
            analysis = result['result']['clay_analysis']
            threats = analysis['threats']
            report = analysis['report']
            satellite_meta = result['result']['satellite_metadata']
            
            # Convert threats to API format
            threat_list = []
            for threat_type, threat_data in threats.items():
                threat_list.append({
                    "threat_type": threat_type,
                    "probability": threat_data['probability'],
                    "severity": threat_data['severity'],
                    "description": f"Coastal {threat_type} detected"
                })
            
            response = ProductionMonitoringResponse(
                alert_id=report['alert_id'],
                timestamp=report['timestamp'],
                location=report['location'],
                mode=result['mode'],
                data_source=result['data_source'],
                real_data=result['real_data'],
                confidence=analysis['embeddings']['confidence'],
                threats=threat_list,
                recommendations=report['recommendations'],
                satellite_metadata=satellite_meta,
                visualization_available=result['result']['visualization']['interactive_map_available'],
                status="alert" if threats else "clear"
            )
        
        else:
            # Demo mode
            analysis_result = result['result']
            threats = analysis_result.get('threats', {})
            report = analysis_result.get('report', {})
            
            threat_list = []
            for threat_type, threat_data in threats.items():
                threat_list.append({
                    "threat_type": threat_type,
                    "probability": threat_data['probability'],
                    "severity": threat_data['severity'],
                    "description": f"Simulated {threat_type} threat"
                })
            
            response = ProductionMonitoringResponse(
                alert_id=report.get('alert_id', f"DEMO_{int(datetime.now().timestamp())}"),
                timestamp=datetime.now().isoformat(),
                location=request.location,
                mode=result['mode'],
                data_source=result['data_source'],
                real_data=result['real_data'],
                confidence=0.92,  # Demo confidence
                threats=threat_list,
                recommendations=report.get('recommendations', ['Continue monitoring']),
                satellite_metadata=None,
                visualization_available=False,
                status="alert" if threats else "clear"
            )
        
        # Store in history
        monitoring_history.append(response.dict())
        
        # Create alert if threats detected
        if response.threats:
            system_alerts.append({
                "timestamp": response.timestamp,
                "location": response.location,
                "threat_count": len(response.threats),
                "mode": response.mode,
                "real_data": response.real_data
            })
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring error: {str(e)}")

@app.post("/monitor/batch/production")
async def batch_monitor_production(
    locations: List[str],
    days_back: int = Query(30, description="Days to look back for satellite data"),
    background_tasks: BackgroundTasks = None
):
    """Batch monitor multiple locations with real satellite data"""
    
    async def process_batch():
        if hasattr(monitor, 'batch_monitor'):
            return monitor.batch_monitor(locations=locations, days_back=days_back)
        else:
            # Fallback batch processing
            results = {}
            for location in locations:
                try:
                    result = monitor.monitor_location(location, visualize=False)
                    results[location] = {
                        'success': True,
                        'mode': 'demo',
                        'data_source': 'Simulated',
                        'real_data': False,
                        'result': result
                    }
                except Exception as e:
                    print(f"Error processing {location}: {e}")
            
            return {'batch_results': results, 'mode': 'demo'}
    
    if background_tasks:
        background_tasks.add_task(process_batch)
        return {
            "message": f"Started batch monitoring of {len(locations)} locations",
            "locations": locations,
            "status": "processing",
            "real_time_data": True
        }
    else:
        result = await process_batch()
        return result

@app.get("/satellite/availability")
async def check_satellite_availability(
    location: str,
    days_back: int = Query(30, description="Days to check for data availability")
):
    """Check satellite data availability for a location"""
    try:
        if hasattr(monitor, 'realtime_monitor'):
            # Production mode - check real data availability
            gee_manager = monitor.realtime_monitor.gee_manager
            geometry = gee_manager.get_location_bounds(location)
            
            if not geometry:
                return {
                    "location": location,
                    "data_available": False,
                    "error": "Location not found"
                }
            
            s2_data = gee_manager.get_latest_sentinel2_data(geometry, days_back)
            s1_data = gee_manager.get_latest_sentinel1_data(geometry, days_back)
            
            return {
                "location": location,
                "data_available": s2_data is not None or s1_data is not None,
                "sentinel2_available": s2_data is not None,
                "sentinel1_available": s1_data is not None,
                "s2_date": s2_data['date'].isoformat() if s2_data else None,
                "s1_date": s1_data['date'].isoformat() if s1_data else None,
                "s2_cloud_cover": s2_data['cloud_cover'] if s2_data else None,
                "search_period_days": days_back
            }
        else:
            # Demo mode
            return {
                "location": location,
                "data_available": True,
                "mode": "demo",
                "simulated_data": True
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")

@app.get("/alerts/active")
async def get_active_alerts():
    """Get all active threat alerts"""
    recent_alerts = []
    
    # Get alerts from last 24 hours
    cutoff_time = datetime.now().timestamp() - (24 * 3600)
    
    for alert in system_alerts:
        alert_time = datetime.fromisoformat(alert['timestamp']).timestamp()
        if alert_time > cutoff_time:
            recent_alerts.append(alert)
    
    return {
        "active_alerts": recent_alerts,
        "count": len(recent_alerts),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/history/production")
async def get_production_history(limit: int = Query(50, description="Number of records to return")):
    """Get recent monitoring history with production data indicators"""
    recent_history = monitoring_history[-limit:]
    
    # Add statistics
    total_real_data = sum(1 for record in recent_history if record.get('real_data'))
    total_threats = sum(len(record.get('threats', [])) for record in recent_history)
    
    return {
        "history": recent_history,
        "statistics": {
            "total_records": len(recent_history),
            "real_data_records": total_real_data,
            "demo_records": len(recent_history) - total_real_data,
            "total_threats_detected": total_threats
        },
        "timestamp": datetime.now().isoformat()
    }

# Production-specific demo endpoints
@app.post("/demo/production/mumbai")
async def demo_mumbai_production():
    """Production demo for Mumbai using real satellite data"""
    request = ProductionMonitoringRequest(
        location="Mumbai Coastal Area, India",
        days_back=15,
        create_visualization=True
    )
    return await monitor_location_production(request)

@app.post("/demo/production/miami")
async def demo_miami_production():
    """Production demo for Miami using real satellite data"""
    request = ProductionMonitoringRequest(
        location="Miami Beach, Florida, USA",
        days_back=20,
        create_visualization=True
    )
    return await monitor_location_production(request)

@app.get("/gee/status")
async def google_earth_engine_status():
    """Check Google Earth Engine connection status"""
    try:
        if hasattr(monitor, 'realtime_monitor'):
            gee_manager = monitor.realtime_monitor.gee_manager
            return {
                "authenticated": gee_manager.is_authenticated,
                "service": "Google Earth Engine",
                "real_data_available": True,
                "supported_satellites": ["Sentinel-1", "Sentinel-2", "Landsat"],
                "global_coverage": True
            }
        else:
            return {
                "authenticated": False,
                "service": "Demo Mode",
                "real_data_available": False,
                "note": "Install earthengine-api for production features"
            }
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e),
            "real_data_available": False
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
