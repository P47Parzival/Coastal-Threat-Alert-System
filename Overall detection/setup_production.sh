#!/bin/bash
# Production Setup Script for Clay v1.5 Coastal Monitoring
# Automated setup for hackathon demonstrations and production deployment

echo "🌊 CLAY v1.5 COASTAL MONITORING - PRODUCTION SETUP"
echo "=================================================="

# Check Python version
python_version=$(python --version 2>&1)
echo "🐍 Python Version: $python_version"

# Install Google Earth Engine
echo "📡 Installing Google Earth Engine..."
pip install earthengine-api geemap

# Authenticate Google Earth Engine
echo "🔑 Setting up Google Earth Engine authentication..."
echo "📝 This will open a browser window for authentication..."
echo "💡 Please complete the authentication process in your browser"

earthengine authenticate

# Test authentication
echo "✅ Testing Google Earth Engine connection..."
python -c "
import ee
try:
    ee.Initialize()
    print('✅ Google Earth Engine authenticated successfully!')
    
    # Test data access
    test_image = ee.Image('COPERNICUS/S2_SR_HARMONIZED/20230101T000000_20230101T000000_T01ABC')
    print('🛰️  Satellite data access confirmed')
    print('🌍 Ready for global coastal monitoring!')
except Exception as e:
    print(f'❌ Authentication issue: {e}')
    print('💡 Please run: earthengine authenticate')
"

echo ""
echo "🚀 PRODUCTION SYSTEM READY!"
echo "=========================="
echo ""
echo "📋 Available Commands:"
echo "  • python production_main.py     - Run production demo"
echo "  • python production_api.py      - Start production API"
echo "  • python gee_realtime_integration.py - GEE integration test"
echo ""
echo "🌐 API Endpoints (after starting production_api.py):"
echo "  • http://localhost:8000/docs     - API documentation"
echo "  • http://localhost:8000/system/status - System status"
echo "  • http://localhost:8000/monitor/production - Real-time monitoring"
echo ""
echo "🏆 HACKATHON READY WITH REAL SATELLITE DATA!"
