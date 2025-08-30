# Weather Map Setup Guide

## 🌤️ OpenWeatherMap API Configuration

The weather map component uses OpenWeatherMap API to display live weather data, storm tracking, and heat overlays.

### 1. Get OpenWeatherMap API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Navigate to "My API Keys" section
4. Copy your API key

### 2. Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
# OpenWeatherMap API Configuration
VITE_OPENWEATHER_API_KEY=your_api_key_here

# Backend API URL
VITE_API_URL=http://localhost:8000
```

### 3. Features Included

#### 🌡️ Temperature Overlay
- Real-time temperature data for major Indian cities
- Color-coded temperature indicators
- Heat map overlay option

#### 💨 Wind Data
- Wind speed and direction indicators
- Animated wind icons
- Wind direction lines

#### 🌪️ Storm/Cyclone Tracking
- Simulated storm data (can be replaced with real storm APIs)
- Storm path prediction
- Category-based storm icons
- Real-time storm alerts

#### 🎛️ Interactive Controls
- Layer toggles (Temperature, Wind, Storms, Heat Map)
- Refresh button for real-time updates
- Legend with color coding
- Popup information on markers

### 4. API Endpoints Used

- **Current Weather**: `https://api.openweathermap.org/data/2.5/weather`
- **Weather Maps**: `https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png`

### 5. Customization Options

You can customize the weather map by modifying the `WeatherMap` component props:

```tsx
<WeatherMap 
  center={[19.0760, 72.8777]}  // Map center coordinates
  zoom={6}                     // Initial zoom level
  height="500px"              // Map height
  showControls={true}         // Show/hide control panel
/>
```

### 6. Adding Real Storm Data

To replace simulated storm data with real storm tracking:

1. Subscribe to a storm tracking API (e.g., NOAA, JTWC)
2. Update the `fetchStormData` function in `WeatherMap.tsx`
3. Replace simulated data with real API calls

### 7. Troubleshooting

#### API Key Issues
- Ensure your API key is valid and active
- Check API usage limits (free tier: 1000 calls/day)
- Verify the key is correctly set in `.env`

#### Map Not Loading
- Check if Leaflet CSS is imported
- Verify internet connection
- Check browser console for errors

#### Weather Data Not Updating
- Check API rate limits
- Verify network connectivity
- Check browser console for fetch errors

### 8. Free Tier Limits

OpenWeatherMap free tier includes:
- 1000 API calls per day
- Current weather data
- Basic weather maps
- 5-day forecast (limited)

For production use, consider upgrading to a paid plan.

### 9. Alternative APIs

If you need different weather data sources:

- **NOAA Weather API**: Free, US-focused
- **WeatherAPI.com**: Global coverage, good free tier
- **AccuWeather API**: Comprehensive data
- **Dark Sky API**: High accuracy (now Apple Weather)

### 10. Security Notes

- Never commit your API key to version control
- Use environment variables for all API keys
- Consider API key rotation for production
- Monitor API usage to avoid rate limiting
