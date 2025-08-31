# 🌊 Coastal Threat Detection System : CodeYatra

A comprehensive AI-powered coastal monitoring and threat detection system that combines satellite imagery analysis, real-time weather monitoring, and flood risk assessment to protect coastal communities.

![Coastal Monitoring](image1.png)

## 🚀 Features

### 🔍 **Area of Interest (AOI) Monitoring**
- Interactive map drawing for monitoring areas
- AI-powered satellite imagery change detection
- Real-time alerts for coastal changes
- Historical tracking and analysis

### 🌤️ **Live Weather & Storm Monitoring**
- Real-time weather data from OpenWeatherMap
- Professional wind visualization with barbs
- Storm tracking and path prediction
- Multiple weather layer overlays

### 💧 **Flood Detection & Risk Assessment**
- GPS-based flood risk analysis
- Google Earth Engine integration
- Automated 3-hour monitoring
- Email alerts for high-risk areas

### 🤖 **Overall Detection System (Clay v1.5 Integration)**
- Advanced AI-powered coastal monitoring using Clay v1.5 foundation model
- Real-time satellite data processing with Google Earth Engine
- Multi-location analysis (Mumbai, Kerala, Chennai, Punjab, Bihar, Uttarakhand)
- 768-dimensional embeddings for accurate threat detection
- Progressive scaling (10m-1000m resolution) for comprehensive coverage
- Production-ready API with robust error handling

## 🏗️ System Architecture

### **Backend (FastAPI + Python)**
- FastAPI for high-performance API
- MongoDB for data storage
- Celery for background tasks
- Google Earth Engine integration
- Clay v1.5 foundation model for AI analysis
- Redis for task queuing

### **Frontend (React + TypeScript)**
- React 18 with modern hooks
- TypeScript for type safety
- Leaflet for interactive mapping
- Tailwind CSS for styling
- Real-time data updates

## 📸 System Screenshots
### **Flood Alert Email**
![notification](notification.jpg)
*Coastal area before change detection analysis*

### **HeatMap**
![heatmap](heatmap.png)
*Cyclone map*

### **Before Analysis - Coastal Area**
![Before Analysis](image_before.png)
*Flood Prediction*

### **After Analysis - Detected Changes**
![After Analysis](image_after.png)
*Coastal area after change detection with highlighted modifications*

## 🔮 Future Implementations
- Custom DL pipeline for anomaly and algal blooms detection
- Enhanced Clay v1.5 model fine-tuning for coastal-specific features
- Multi-temporal analysis for long-term coastal change trends
- Advanced early warning system with predictive modeling
- Current custom pipeline for Shoreline detection and monitoring which can be viewed at ./Models/fetch_noaa_data.py and test_flood_detection
- Data API From https://www.noaa.gov/ocean-coasts


## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+, Node.js 16+, MongoDB, Redis
- Google Earth Engine account
- OpenWeatherMap API key

### **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **Frontend Setup**
```bash
cd frontend
npm install
echo "VITE_OPENWEATHER_API_KEY=your_api_key" > .env
npm run dev
```

## 🔧 Configuration

### **Required API Keys**
- OpenWeatherMap: Weather data and maps
- SendGrid: Email notifications
- Google Earth Engine: Satellite imagery and Clay v1.5 model access
- MongoDB: Database connection

## 📊 API Endpoints

- **Authentication**: `/auth/register`, `/auth/login`
- **AOI Management**: `/aois/` (CRUD operations)
- **Shoreline Analysis**: `/shoreline/analyze`
- **Flood Detection**: `/flood/detect`
- **Overall Detection**: `/monitor/robust` (Clay v1.5 AI analysis)

## 🎯 Use Cases

- **Government**: Coastal management and disaster preparedness
- **Research**: Climate studies and environmental monitoring
- **Private Sector**: Risk assessment and planning

## 🔒 Security Features

- JWT authentication with bcrypt hashing
- API rate limiting and input validation
- CORS protection and secure endpoints

## 🚧 Development Status

- ✅ Core AOI monitoring system
- ✅ Weather integration and mapping
- ✅ Flood detection and alerts
- ✅ Overall Detection with Clay v1.5 AI model
- ✅ Google Earth Engine real-time integration
- 🚧 Advanced AI model training
- 📋 Production deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request


---

**Built with ❤️ for coastal communities worldwide**

*Protecting our coasts, one pixel at a time* 🌊🛡️
