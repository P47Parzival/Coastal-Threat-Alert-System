@echo off
REM Production Setup Script for Clay v1.5 Coastal Monitoring (Windows)
REM Automated setup for hackathon demonstrations and production deployment

echo 🌊 CLAY v1.5 COASTAL MONITORING - PRODUCTION SETUP
echo ==================================================

REM Check Python version
python --version
echo.

REM Install Google Earth Engine
echo 📡 Installing Google Earth Engine...
"C:/hackout mofel 8/.venv/Scripts/pip.exe" install earthengine-api geemap pyproj shapely

echo.
echo 🔑 Setting up Google Earth Engine authentication...
echo 📝 This will open a browser window for authentication...
echo 💡 Please complete the authentication process in your browser
echo.

REM Authenticate Google Earth Engine
earthengine authenticate

echo.
echo ✅ Testing Google Earth Engine connection...

REM Test authentication
"C:/hackout mofel 8/.venv/Scripts/python.exe" -c "
import ee
try:
    ee.Initialize()
    print('✅ Google Earth Engine authenticated successfully!')
    print('🛰️  Satellite data access confirmed')
    print('🌍 Ready for global coastal monitoring!')
except Exception as e:
    print(f'❌ Authentication issue: {e}')
    print('💡 Please run: earthengine authenticate')
"

echo.
echo 🚀 PRODUCTION SYSTEM READY!
echo ==========================
echo.
echo 📋 Available Commands:
echo   • python production_main.py     - Run production demo
echo   • python production_api.py      - Start production API  
echo   • python gee_realtime_integration.py - GEE integration test
echo.
echo 🌐 API Endpoints (after starting production_api.py):
echo   • http://localhost:8000/docs     - API documentation
echo   • http://localhost:8000/system/status - System status
echo   • http://localhost:8000/monitor/production - Real-time monitoring
echo.
echo 🏆 HACKATHON READY WITH REAL SATELLITE DATA!

pause
