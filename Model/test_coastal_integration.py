#!/usr/bin/env python3
"""
Test script for coastal detection integration
Tests if the coastal detection functions can be imported and used by the backend
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_coastal_detection_import():
    """Test if coastal detection functions can be imported"""
    try:
        print("🔍 Testing coastal detection module import...")
        
        # Try to import the main functions
        from coastal_detection import (
            analyze_coastal_threats,
            generate_threat_alert,
            create_coastal_monitoring_dashboard
        )
        
        print("✅ Successfully imported coastal detection functions!")
        
        # Test the functions with sample data
        print("\n🧪 Testing function calls...")
        
        # Sample shoreline data
        shoreline_positions = [100, 99.5, 99.0, 98.5, 98.0, 97.5, 97.0, 96.5, 96.0, 95.5, 95.0, 94.5]
        from datetime import datetime, timedelta
        start_date = datetime(2020, 1, 1)
        timestamps = [start_date + timedelta(days=30*i) for i in range(12)]
        
        # Test analyze_coastal_threats
        print("Testing analyze_coastal_threats...")
        threat_analysis = analyze_coastal_threats(shoreline_positions, timestamps)
        print(f"✅ Threat analysis completed: {len(threat_analysis['threat_level'])} threat levels calculated")
        
        # Test generate_threat_alert
        print("Testing generate_threat_alert...")
        alerts = generate_threat_alert(threat_analysis)
        print(f"✅ Alerts generated: {len(alerts)} alerts created")
        
        # Test create_coastal_monitoring_dashboard
        print("Testing create_coastal_monitoring_dashboard...")
        monitoring_data = create_coastal_monitoring_dashboard()
        print(f"✅ Monitoring dashboard created: {len(monitoring_data)} monitoring points")
        
        print("\n🎉 All tests passed! Coastal detection module is ready for integration.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Please ensure coastal_detection.py is in the same directory")
        return False
    except Exception as e:
        print(f"❌ Function test error: {e}")
        print("🔧 Please check the coastal detection functions")
        return False

def test_shoreline_analysis_simulation():
    """Test shoreline analysis simulation"""
    try:
        print("\n🌊 Testing shoreline analysis simulation...")
        
        # Simulate the analysis that would happen in the backend
        shoreline_positions = [100, 99.5, 99.0, 98.5, 98.0, 97.5, 97.0, 96.5, 96.0, 95.5, 95.0, 94.5]
        from datetime import datetime, timedelta
        start_date = datetime(2020, 1, 1)
        timestamps = [start_date + timedelta(days=30*i) for i in range(12)]
        
        # Calculate metrics
        total_change = shoreline_positions[-1] - shoreline_positions[0]
        erosion_rates = []
        
        for i in range(1, len(shoreline_positions)):
            change = shoreline_positions[i] - shoreline_positions[i-1]
            time_diff = (timestamps[i] - timestamps[i-1]).days
            if time_diff > 0:
                erosion_rate = change / time_diff
                erosion_rates.append(erosion_rate)
        
        avg_erosion_rate = sum(erosion_rates) / len(erosion_rates) if erosion_rates else 0
        
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
        
        print(f"✅ Shoreline analysis simulation completed:")
        print(f"   - Total change: {total_change:.2f} meters")
        print(f"   - Average erosion rate: {avg_erosion_rate:.4f} m/day")
        print(f"   - Threat level: {threat_level}")
        print(f"   - Flood risk: {flood_risk}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting coastal detection integration tests...")
    print("=" * 60)
    
    # Test 1: Import test
    import_success = test_coastal_detection_import()
    
    # Test 2: Simulation test
    simulation_success = test_shoreline_analysis_simulation()
    
    print("\n" + "=" * 60)
    if import_success and simulation_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Coastal detection module is ready for backend integration")
        print("✅ Shoreline analysis simulation works correctly")
        print("\n📋 Next steps:")
        print("   1. Ensure the backend can import from the Model directory")
        print("   2. Test the /shoreline/analyze endpoint")
        print("   3. Verify the frontend can send shoreline data")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Please fix the issues before proceeding with integration")
    
    print("=" * 60)
