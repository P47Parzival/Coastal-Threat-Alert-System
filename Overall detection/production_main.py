"""
Updated main.py with Google Earth Engine real-time integration
Production-ready Clay v1.5 coastal monitoring system
"""

import os
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import the real-time GEE integration
try:
    from gee_realtime_integration import RealTimeClayMonitor
    GEE_AVAILABLE = True
    print("✅ Google Earth Engine integration available")
except ImportError as e:
    print(f"⚠️  Google Earth Engine not available: {e}")
    print("💡 Install with: pip install earthengine-api")
    GEE_AVAILABLE = False

# Import original Clay monitor as fallback
from main import ClayCoastalMonitor


class ProductionCoastalMonitor:
    """
    Production-ready coastal monitoring system that uses real satellite data
    when available, with fallback to demonstration mode
    """
    
    def __init__(self, use_real_data: bool = True):
        """
        Initialize production monitoring system
        
        Args:
            use_real_data: Whether to use real satellite data from Google Earth Engine
        """
        self.use_real_data = use_real_data and GEE_AVAILABLE
        
        if self.use_real_data:
            print("🌍 Initializing PRODUCTION MODE with real satellite data")
            self.realtime_monitor = RealTimeClayMonitor()
            self.mode = "production"
        else:
            print("🎯 Initializing DEMO MODE with simulated data")
            self.demo_monitor = ClayCoastalMonitor()
            self.demo_monitor.load_clay_model()
            self.mode = "demo"
        
        print(f"⚡ System ready in {self.mode.upper()} mode")
    
    def monitor_location(self, location: str, **kwargs) -> dict:
        """
        Monitor a coastal location using the best available data source
        
        Args:
            location: Location name to monitor
            **kwargs: Additional parameters
        """
        if self.mode == "production":
            print(f"🛰️  PRODUCTION MONITORING: {location}")
            print("📡 Using real satellite data from Google Earth Engine")
            
            result = self.realtime_monitor.monitor_location_realtime(
                location=location,
                days_back=kwargs.get('days_back', 30)
            )
            
            if result:
                return {
                    'success': True,
                    'mode': 'production',
                    'data_source': 'Google Earth Engine',
                    'real_data': True,
                    'result': result
                }
            else:
                print("⚠️  Real data unavailable, falling back to demo mode")
                return self._fallback_to_demo(location, **kwargs)
        
        else:
            return self._fallback_to_demo(location, **kwargs)
    
    def _fallback_to_demo(self, location: str, **kwargs) -> dict:
        """Fallback to demo mode with simulated data"""
        print(f"🎯 DEMO MONITORING: {location}")
        print("📊 Using simulated satellite data for demonstration")
        
        result = self.demo_monitor.monitor_location(
            location=location,
            generate_report=kwargs.get('generate_report', True),
            visualize=kwargs.get('visualize', True)
        )
        
        return {
            'success': True,
            'mode': 'demo', 
            'data_source': 'Simulated',
            'real_data': False,
            'result': result
        }
    
    def batch_monitor(self, locations: list, **kwargs) -> dict:
        """Monitor multiple locations"""
        if self.mode == "production":
            print(f"🌍 PRODUCTION BATCH MONITORING: {len(locations)} locations")
            return self.realtime_monitor.batch_monitor_realtime(
                locations=locations,
                days_back=kwargs.get('days_back', 30)
            )
        else:
            print(f"🎯 DEMO BATCH MONITORING: {len(locations)} locations")
            results = {}
            for location in locations:
                results[location] = self._fallback_to_demo(location, visualize=False)
            return {'batch_results': results, 'mode': 'demo'}
    
    def get_system_status(self) -> dict:
        """Get system status information"""
        status = {
            'mode': self.mode,
            'timestamp': datetime.now().isoformat(),
            'gee_available': GEE_AVAILABLE,
            'real_data_enabled': self.use_real_data,
            'clay_model_status': 'loaded'
        }
        
        if self.mode == "production":
            status['gee_authenticated'] = self.realtime_monitor.gee_manager.is_authenticated
            status['data_sources'] = ['Google Earth Engine', 'Sentinel-1', 'Sentinel-2']
        else:
            status['data_sources'] = ['Simulated satellite data']
        
        return status


def authenticate_google_earth_engine():
    """Helper function to authenticate Google Earth Engine"""
    try:
        import ee
        
        print("🔑 Authenticating Google Earth Engine...")
        print("📝 This will open a web browser for authentication")
        
        # Try to initialize first
        try:
            ee.Initialize()
            print("✅ Already authenticated!")
            return True
        except:
            # Need to authenticate
            ee.Authenticate()
            ee.Initialize()
            print("✅ Google Earth Engine authentication complete!")
            return True
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Please install Earth Engine: pip install earthengine-api")
        return False


def production_demo():
    """
    Production demo showcasing real satellite data integration
    """
    print("🌊 CLAY v1.5 PRODUCTION COASTAL MONITORING SYSTEM")
    print("🚀 Real-time satellite data integration for hackathons & production")
    print("=" * 70)
    
    # Check Google Earth Engine availability
    if GEE_AVAILABLE:
        print("✅ Google Earth Engine integration available")
        
        # Try to authenticate if not already done
        try:
            import ee
            ee.Initialize()
            print("✅ Google Earth Engine authenticated")
            use_real_data = True
        except:
            print("🔑 Google Earth Engine authentication required")
            print("💡 Run: earthengine authenticate")
            print("🎯 Continuing with demo mode...")
            use_real_data = False
    else:
        print("⚠️  Google Earth Engine not available")
        print("💡 Install with: pip install earthengine-api")
        print("🎯 Using demo mode with simulated data")
        use_real_data = False
    
    # Initialize production system
    monitor = ProductionCoastalMonitor(use_real_data=use_real_data)
    
    # Show system status
    status = monitor.get_system_status()
    print(f"\n📊 SYSTEM STATUS")
    print("-" * 30)
    print(f"🔧 Mode: {status['mode'].upper()}")
    print(f"🛰️  Data Sources: {', '.join(status['data_sources'])}")
    print(f"📡 Real Data: {'✅' if status['real_data_enabled'] else '❌'}")
    print(f"🤖 Clay v1.5: {status['clay_model_status']}")
    
    # Demo locations optimized for real satellite data availability
    demo_locations = [
        "Mumbai Coastal Area, India",      # High data availability
        "Miami Beach, Florida, USA",       # High data availability  
        "Chennai Coast, India",            # Good data availability
    ]
    
    print(f"\n🎯 DEMONSTRATION: {monitor.mode.upper()} MODE")
    print("=" * 50)
    
    # Primary location analysis
    primary_location = demo_locations[0]
    print(f"\n🔍 PRIMARY ANALYSIS: {primary_location}")
    print("-" * 40)
    
    result = monitor.monitor_location(
        location=primary_location,
        days_back=15,  # Look for recent data
        generate_report=True,
        visualize=True
    )
    
    if result['success']:
        analysis_result = result['result']
        
        print(f"\n📋 ANALYSIS RESULTS")
        print("-" * 25)
        print(f"📍 Location: {primary_location}")
        print(f"🔧 Mode: {result['mode'].upper()}")
        print(f"📊 Data Source: {result['data_source']}")
        print(f"🛰️  Real Data: {'✅' if result['real_data'] else '❌'}")
        
        if result['mode'] == 'production':
            # Production mode results
            clay_analysis = analysis_result['clay_analysis']
            threats = clay_analysis['threats']
            satellite_meta = analysis_result['satellite_metadata']
            
            print(f"📅 Data Freshness:")
            if satellite_meta['s2_date']:
                s2_age = (datetime.now() - datetime.fromisoformat(satellite_meta['s2_date'].replace('Z', ''))).days
                print(f"   Sentinel-2: {s2_age} days ago")
            if satellite_meta['s1_date']:
                s1_age = (datetime.now() - datetime.fromisoformat(satellite_meta['s1_date'].replace('Z', ''))).days
                print(f"   Sentinel-1: {s1_age} days ago")
            
            print(f"🎯 Confidence: {clay_analysis['embeddings']['confidence']:.1%}")
            print(f"⚠️  Threats: {len(threats)}")
            
            if threats:
                for threat_type, threat_data in threats.items():
                    severity_icon = "🚨" if threat_data['severity'] == 'high' else "⚠️"
                    print(f"   {severity_icon} {threat_type}: {threat_data['probability']:.1%}")
            
            if analysis_result['visualization']['map_file']:
                print(f"🗺️  Map: {analysis_result['visualization']['map_file']}")
        
        else:
            # Demo mode results
            threats = analysis_result['threats']
            print(f"⚠️  Simulated Threats: {len(threats)}")
            
            if threats:
                for threat_type, threat_data in threats.items():
                    print(f"   ⚠️  {threat_type}: {threat_data['probability']:.1%}")
    
    # Batch monitoring demo
    print(f"\n🌍 BATCH MONITORING DEMONSTRATION")
    print("-" * 40)
    
    batch_locations = demo_locations[:2]  # Monitor 2 locations for demo
    batch_result = monitor.batch_monitor(
        locations=batch_locations,
        days_back=20
    )
    
    if 'summary' in batch_result:
        summary = batch_result['summary']
        print(f"📊 Batch Results:")
        print(f"   Locations: {summary['total_locations']}")
        print(f"   Successful: {summary['successful_monitoring']}")
        print(f"   Total Threats: {summary['total_threats']}")
    
    # Final summary
    print(f"\n🏆 PRODUCTION DEMONSTRATION COMPLETE!")
    print("=" * 50)
    
    if monitor.mode == "production":
        print("✅ PRODUCTION-READY FEATURES DEMONSTRATED:")
        print("   🛰️  Real satellite data from Google Earth Engine")
        print("   🤖 Clay v1.5 geospatial foundation model")
        print("   ⚡ Real-time processing pipeline")
        print("   🌍 Global coastal monitoring capability")
        print("   📊 Production-grade data analysis")
        print("   🗺️  Interactive visualization maps")
        print("   📈 Scalable batch processing")
    else:
        print("🎯 DEMO MODE FEATURES DEMONSTRATED:")
        print("   🤖 Clay v1.5 foundation model integration")
        print("   📊 Coastal threat detection algorithms")
        print("   📈 Comprehensive analysis pipeline")
        print("   🎨 Professional visualizations")
        print("   🔄 Fallback system architecture")
    
    print(f"\n🚀 READY FOR HACKATHON PRESENTATION!")
    print("💡 To enable production mode:")
    print("   1. pip install earthengine-api")
    print("   2. earthengine authenticate")
    print("   3. Re-run this script")


if __name__ == "__main__":
    production_demo()
