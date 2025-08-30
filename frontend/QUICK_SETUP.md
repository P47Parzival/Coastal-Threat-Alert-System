# 🚀 Quick Weather Map Setup

## Fix the White Screen Issue

The white screen is caused by a missing OpenWeatherMap API key. Here's how to fix it:

### 1. Get Free API Key (2 minutes)
1. Go to [OpenWeatherMap API](https://openweathermap.org/api)
2. Click "Sign Up" (free account)
3. Go to "My API Keys" section
4. Copy your API key

### 2. Create Environment File (30 seconds)
Create a file named `.env` in the `frontend` directory:

```bash
# OpenWeatherMap API Configuration
VITE_OPENWEATHER_API_KEY=your_api_key_here

# Backend API URL  
VITE_API_URL=http://localhost:8000
```

### 3. Restart Development Server
```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd frontend
npm run dev
```

### 4. Verify It Works
- Open http://localhost:5173
- Go to Dashboard
- You should see the weather map with real data!

## What You'll See After Setup

✅ **Live Temperature Data** for 8 major Indian cities  
✅ **Wind Direction Indicators** with animated icons  
✅ **Storm Tracking** with path prediction  
✅ **Interactive Controls** to toggle layers  
✅ **Heat Map Overlay** option  

## Troubleshooting

**Still seeing white screen?**
- Make sure the `.env` file is in the `frontend` directory
- Restart the development server completely
- Check browser console for errors

**API key not working?**
- Wait 2 hours after creating the key (activation delay)
- Check if you copied the key correctly
- Verify the key is active in your OpenWeatherMap account

**Need help?**
- Check the full setup guide: `WEATHER_MAP_SETUP.md`
- OpenWeatherMap free tier: 1000 calls/day (plenty for testing)
