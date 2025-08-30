"""
Fixed Google Earth Engine Setup and Authentication for Windows
Resolves curses module issues and provides proper authentication flow
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def check_python_environment():
    """Check if we're in the correct Python environment"""
    print("🐍 Python Environment Check")
    print("-" * 30)
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Check if we're in virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"✅ Virtual Environment: {venv_path}")
    else:
        print("⚠️  Not in virtual environment")
    
    return True

def install_earthengine_packages():
    """Install Earth Engine packages with Windows compatibility"""
    print("\n📦 Installing Earth Engine Packages")
    print("-" * 40)
    
    # Use the correct pip from virtual environment
    pip_exe = os.path.join(sys.prefix, "Scripts", "pip.exe")
    python_exe = sys.executable
    
    packages = [
        "earthengine-api",
        "google-auth",
        "google-auth-oauthlib", 
        "google-auth-httplib2",
        "geemap",
        "folium"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            result = subprocess.run([
                python_exe, "-m", "pip", "install", package
            ], capture_output=True, text=True, check=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def setup_earthengine_credentials():
    """Setup Earth Engine credentials without using the CLI"""
    print("\n🔑 Setting up Earth Engine Authentication")
    print("-" * 45)
    
    try:
        import ee
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        import google.auth
        
        print("📝 Starting manual authentication process...")
        
        # Try to initialize with existing credentials
        try:
            ee.Initialize()
            print("✅ Already authenticated with Earth Engine!")
            return True
        except Exception:
            print("🔐 Need to authenticate...")
        
        # Manual authentication flow
        print("\n🌐 Opening browser for authentication...")
        print("💡 Please complete the following steps:")
        print("   1. Go to: https://code.earthengine.google.com/")
        print("   2. Sign in with your Google account")
        print("   3. Generate a token")
        print("   4. Copy the token when prompted")
        
        # Alternative authentication method
        token = input("\n🔑 Paste your Earth Engine token here (or press Enter to try automatic): ").strip()
        
        if token:
            # Save token manually
            ee_config_dir = Path.home() / ".config" / "earthengine"
            ee_config_dir.mkdir(parents=True, exist_ok=True)
            
            credentials_file = ee_config_dir / "credentials"
            with open(credentials_file, 'w') as f:
                f.write(token)
            
            print("💾 Token saved to credentials file")
        
        # Try to initialize again
        try:
            ee.Initialize()
            print("✅ Earth Engine authentication successful!")
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_earthengine_connection():
    """Test Earth Engine connection and data access"""
    print("\n🧪 Testing Earth Engine Connection")
    print("-" * 35)
    
    try:
        import ee
        
        # Initialize
        ee.Initialize()
        print("✅ Earth Engine initialized successfully")
        
        # Test basic functionality
        print("🌍 Testing basic Earth Engine operations...")
        
        # Create a simple geometry
        point = ee.Geometry.Point([0, 0])
        print("✅ Geometry creation: OK")
        
        # Test image collection access
        try:
            collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').limit(1)
            size = collection.size().getInfo()
            print(f"✅ Sentinel-2 collection access: {size} images found")
        except Exception as e:
            print(f"⚠️  Sentinel-2 access issue: {e}")
        
        # Test SAR data access
        try:
            sar_collection = ee.ImageCollection('COPERNICUS/S1_GRD').limit(1)
            sar_size = sar_collection.size().getInfo()
            print(f"✅ Sentinel-1 SAR access: {sar_size} images found")
        except Exception as e:
            print(f"⚠️  Sentinel-1 access issue: {e}")
        
        print("🎯 Earth Engine connection test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Earth Engine test failed: {e}")
        return False

def create_demo_without_auth():
    """Create a demo that works without Earth Engine authentication"""
    print("\n🎯 Creating Demo Mode Configuration")
    print("-" * 38)
    
    demo_config = {
        "mode": "demo",
        "earthengine_available": False,
        "use_simulated_data": True,
        "reason": "Earth Engine authentication not available"
    }
    
    config_file = "system_config.json"
    with open(config_file, 'w') as f:
        json.dump(demo_config, f, indent=2)
    
    print(f"💾 Demo configuration saved to {config_file}")
    print("🎯 System will run in demo mode with simulated data")
    
    return True

def main():
    """Main setup function"""
    print("🌊 CLAY v1.5 COASTAL MONITORING - FIXED SETUP")
    print("=" * 50)
    
    # Step 1: Check environment
    if not check_python_environment():
        print("❌ Environment check failed")
        return False
    
    # Step 2: Install packages
    if not install_earthengine_packages():
        print("❌ Package installation failed")
        return False
    
    # Step 3: Try to setup Earth Engine
    ee_success = setup_earthengine_credentials()
    
    if ee_success:
        # Step 4: Test connection
        if test_earthengine_connection():
            print("\n🚀 PRODUCTION SETUP COMPLETE!")
            print("=" * 35)
            print("✅ Earth Engine authenticated and tested")
            print("🛰️  Real satellite data available")
            print("🌍 Global coastal monitoring ready")
            
            # Create production config
            prod_config = {
                "mode": "production",
                "earthengine_available": True,
                "use_real_data": True
            }
            
            with open("system_config.json", 'w') as f:
                json.dump(prod_config, f, indent=2)
        else:
            print("⚠️  Earth Engine test failed, creating demo config")
            create_demo_without_auth()
    else:
        print("\n🎯 DEMO SETUP COMPLETE!")
        print("=" * 25)
        print("⚠️  Earth Engine authentication not available")
        print("🎯 System will run in demo mode")
        print("📊 Using simulated data for demonstration")
        create_demo_without_auth()
    
    print("\n📋 Next Steps:")
    print("-" * 15)
    print("• python fixed_production_main.py  - Run the system")
    print("• python fixed_production_api.py   - Start API server")
    print("\n🏆 Ready for hackathon demonstration!")
    
    return True

if __name__ == "__main__":
    main()
