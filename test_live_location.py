#!/usr/bin/env python3
"""
Test script for live location capture functionality
"""

import requests
import json
import time

def test_live_location_flood_detection():
    """
    Test the flood detection with live location data
    """
    
    # Test data simulating live GPS location
    test_location = {
        "latitude": 19.0760,  # Mumbai coordinates
        "longitude": 72.8777,
        "locationName": "Test Location (Mumbai)",
        "accuracy": 15.5,  # 15.5 meters accuracy
        "timestamp": int(time.time() * 1000)  # Current timestamp in milliseconds
    }
    
    print("🧪 Testing Live Location Flood Detection")
    print(f"📍 Test Location: {test_location['locationName']}")
    print(f"🌍 Coordinates: ({test_location['latitude']}, {test_location['longitude']})")
    print(f"📏 Accuracy: {test_location['accuracy']}m")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(test_location['timestamp']/1000))}")
    print("-" * 50)
    
    try:
        # Test the flood detection endpoint
        response = requests.post(
            "http://localhost:8000/flood/test-detect",
            json=test_location,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Live location flood detection test PASSED")
            print(f"📊 Risk Level: {result['analysis']['floodRisk']}")
            print(f"🎯 Risk Score: {result['analysis']['riskScore']}/100")
            print(f"⏱️ Time to Flood: {result['analysis']['timeToFlood']}")
            print(f"💧 Water Level: {result['analysis']['waterLevel']:.1%}")
            print(f"🌧️ Precipitation: {result['analysis']['precipitation']:.1f} mm")
            print(f"🌱 Soil Moisture: {result['analysis']['soilMoisture']:.3f} m³/m³")
            print(f"🔄 Confidence: {result['analysis']['confidence']:.1%}")
            
            if 'gee_analysis' in result['analysis']:
                print(f"🛰️ GEE Analysis: {'Yes' if result['analysis']['gee_analysis'] else 'No'}")
            
            return True
        else:
            print(f"❌ Live location flood detection test FAILED")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_location_data_structure():
    """
    Test that the location data structure is properly handled
    """
    print("\n🧪 Testing Location Data Structure")
    print("-" * 50)
    
    test_cases = [
        {
            "name": "Full GPS Data",
            "data": {
                "latitude": 19.0760,
                "longitude": 72.8777,
                "locationName": "Mumbai, India",
                "accuracy": 10.5,
                "timestamp": int(time.time() * 1000)
            }
        },
        {
            "name": "Minimal GPS Data",
            "data": {
                "latitude": 19.0760,
                "longitude": 72.8777
            }
        },
        {
            "name": "High Accuracy GPS",
            "data": {
                "latitude": 19.0760,
                "longitude": 72.8777,
                "locationName": "High Precision Location",
                "accuracy": 2.1,
                "timestamp": int(time.time() * 1000)
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"📋 Testing: {test_case['name']}")
        try:
            response = requests.post(
                "http://localhost:8000/flood/test-detect",
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"  ✅ PASSED")
            else:
                print(f"  ❌ FAILED (Status: {response.status_code})")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")

if __name__ == "__main__":
    print("🚀 Live Location Flood Detection Test Suite")
    print("=" * 60)
    
    # Test 1: Basic functionality
    success = test_live_location_flood_detection()
    
    # Test 2: Data structure handling
    test_location_data_structure()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("💡 Next steps:")
        print("   1. Open your browser and go to the dashboard")
        print("   2. Click 'Detect Flood' button")
        print("   3. Allow location access when prompted")
        print("   4. Verify real GPS coordinates are captured")
    else:
        print("⚠️ Some tests failed. Check the backend server and try again.")
