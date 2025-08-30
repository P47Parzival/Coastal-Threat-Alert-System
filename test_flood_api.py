#!/usr/bin/env python3
"""
Simple test script for flood detection API
"""

import requests
import json

def test_flood_api():
    """Test the flood detection API endpoints"""
    print("🌊 Testing Flood Detection API...")
    print("=" * 50)
    
    # Test data
    test_location = {
        "latitude": 19.0760,  # Mumbai
        "longitude": 72.8777,
        "locationName": "Mumbai Test Location"
    }
    
    # Test 1: Test endpoint (no authentication required)
    print("📍 Testing flood detection test endpoint...")
    print(f"Request: POST http://localhost:8000/flood/test-detect")
    print(f"Data: {json.dumps(test_location, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/flood/test-detect",
            json=test_location,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nTest Endpoint Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Flood detection test successful!")
            print(f"   Location: {result['location']}")
            print(f"   Risk Level: {result['analysis']['floodRisk']}")
            print(f"   Risk Score: {result['analysis']['riskScore']:.1f}/100")
            print(f"   Time to Flood: {result['analysis']['timeToFlood']}")
        else:
            print(f"❌ Flood detection test failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing flood detection test endpoint: {e}")
        return False
    
    # Test 2: Main endpoint (requires authentication)
    print("\n📍 Testing main flood detection endpoint...")
    print(f"Request: POST http://localhost:8000/flood/detect")
    print(f"Data: {json.dumps(test_location, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/flood/detect",
            json=test_location,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nMain Endpoint Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Main flood detection successful!")
            print(f"   Location: {result['location']}")
            print(f"   Risk Level: {result['analysis']['floodRisk']}")
            print(f"   Risk Score: {result['analysis']['riskScore']:.1f}/100")
            print(f"   Time to Flood: {result['analysis']['timeToFlood']}")
            return True
        elif response.status_code == 401:
            print("⚠️ Main endpoint requires authentication (expected)")
            print("   This is normal - the endpoint is working but needs login")
            return True
        else:
            print(f"❌ Main flood detection failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error testing main flood detection: {e}")
        return False

def test_api_endpoints():
    """Test if the API endpoints are accessible"""
    print("\n🔍 Testing API Endpoints...")
    print("=" * 50)
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/docs", "API documentation"),
        ("GET", "/openapi.json", "OpenAPI schema"),
        ("GET", "/flood/test-connection", "Flood connection test"),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            response = requests.request(method, f"http://localhost:8000{endpoint}")
            print(f"✅ {method} {endpoint} - {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint} - {description}: {e}")

if __name__ == "__main__":
    print("🚀 Starting Flood Detection API Tests...")
    print("=" * 50)
    
    # Test basic API endpoints first
    test_api_endpoints()
    
    # Test flood detection
    success = test_flood_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Flood detection API test completed successfully!")
        print("✅ The API is working correctly")
    else:
        print("❌ Flood detection API test failed!")
        print("🔧 Please check the backend server and restart if necessary")
    print("=" * 50)
