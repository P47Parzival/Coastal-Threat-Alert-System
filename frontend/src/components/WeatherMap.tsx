import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline } from 'react-leaflet';
import { Icon, DivIcon } from 'leaflet';
import { Wind, Thermometer, AlertTriangle, MapPin, RefreshCw, Cloud, Droplets, Gauge } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

interface WeatherData {
  lat: number;
  lon: number;
  temp: number;
  feels_like: number;
  humidity: number;
  wind_speed: number;
  wind_deg: number;
  pressure: number;
  weather: Array<{
    main: string;
    description: string;
    icon: string;
  }>;
  cityName?: string;
}

interface StormData {
  id: string;
  name: string;
  lat: number;
  lon: number;
  wind_speed: number;
  pressure: number;
  category: string;
  direction: number;
  timestamp: number;
}

interface WeatherMapProps {
  center?: [number, number];
  zoom?: number;
  height?: string;
  showControls?: boolean;
}

const WeatherMap: React.FC<WeatherMapProps> = ({
  center = [19.0760, 72.8777], // Mumbai default
  zoom = 8,
  height = '400px',
  showControls = true
}) => {
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
  const [stormData, setStormData] = useState<StormData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeLayers, setActiveLayers] = useState({
    temperature: true,
    wind: true,
    storms: true,
    heat: false,
    precipitation: false,
    pressure: false
  });
  const [mapCenter, setMapCenter] = useState<[number, number]>(center);
  const mapRef = useRef<any>(null);

  // OpenWeatherMap API Key - you'll need to add this to your environment
  const API_KEY = import.meta.env.VITE_OPENWEATHER_API_KEY;
  const BASE_URL = 'https://api.openweathermap.org/data/2.5';

  // Custom wind icon - more authentic like news weather maps
  const createWindIcon = (speed: number, direction: number) => {
    const intensity = Math.min(speed / 50, 1); // Normalize wind speed
    const color = intensity > 0.7 ? '#ff0000' : intensity > 0.5 ? '#ff6600' : intensity > 0.3 ? '#ffaa00' : '#00aa00';
    
    // Create wind barbs like professional weather maps
    const barbCount = Math.floor(speed / 5); // 5 m/s per barb
    const barbs = '|'.repeat(Math.min(barbCount, 8)); // Max 8 barbs
    
    return new DivIcon({
      className: 'wind-icon',
      html: `
        <div style="
          transform: rotate(${direction}deg);
          color: ${color};
          font-size: 16px;
          font-weight: bold;
          text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
          background: rgba(255,255,255,0.9);
          border-radius: 4px;
          padding: 2px 4px;
          border: 2px solid ${color};
        ">
          ${barbs}
        </div>
      `,
      iconSize: [40, 40],
      iconAnchor: [20, 20]
    });
  };

  // Custom temperature icon
  const createTempIcon = (temp: number) => {
    const color = temp > 30 ? '#ff4444' : temp > 20 ? '#ffaa00' : '#44aa44';
    
    return new DivIcon({
      className: 'temp-icon',
      html: `
        <div style="
          background: ${color};
          color: white;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 12px;
          box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">
          ${Math.round(temp)}°
        </div>
      `,
      iconSize: [40, 40],
      iconAnchor: [20, 20]
    });
  };

  // Custom storm icon
  const createStormIcon = (category: string) => {
    const colors: Record<string, string> = {
      'TD': '#ffff00', // Tropical Depression
      'TS': '#ffaa00', // Tropical Storm
      'H1': '#ff6600', // Hurricane Category 1
      'H2': '#ff4400', // Hurricane Category 2
      'H3': '#ff2200', // Hurricane Category 3
      'H4': '#ff0000', // Hurricane Category 4
      'H5': '#cc0000'  // Hurricane Category 5
    };
    
    return new DivIcon({
      className: 'storm-icon',
      html: `
        <div style="
          background: ${colors[category] || '#ff0000'};
          color: white;
          border-radius: 50%;
          width: 50px;
          height: 50px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 14px;
          box-shadow: 0 0 10px ${colors[category] || '#ff0000'};
          animation: pulse 2s infinite;
        ">
          🌪️
        </div>
        <style>
          @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
          }
        </style>
      `,
      iconSize: [50, 50],
      iconAnchor: [25, 25]
    });
  };

  // Fetch weather data for multiple cities
  const fetchWeatherData = async () => {
    setLoading(true);
    setError(null);
    
    // Check if API key is available
    if (!API_KEY) {
      setError('OpenWeatherMap API key not configured. Please add VITE_OPENWEATHER_API_KEY to your .env file.');
      setLoading(false);
      return;
    }
    
    try {
      // Major cities in India for weather data
      const cities = [
        { name: 'Mumbai', lat: 19.0760, lon: 72.8777 },
        { name: 'Delhi', lat: 28.6139, lon: 77.2090 },
        { name: 'Chennai', lat: 13.0827, lon: 80.2707 },
        { name: 'Kolkata', lat: 22.5726, lon: 88.3639 },
        { name: 'Hyderabad', lat: 17.3850, lon: 78.4867 },
        { name: 'Bangalore', lat: 12.9716, lon: 77.5946 },
        { name: 'Ahmedabad', lat: 23.0225, lon: 72.5714 },
        { name: 'Pune', lat: 18.5204, lon: 73.8567 }
      ];

      const weatherPromises = cities.map(city =>
        fetch(`${BASE_URL}/weather?lat=${city.lat}&lon=${city.lon}&appid=${API_KEY}&units=metric`)
          .then(res => {
            if (!res.ok) {
              throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
          })
          .then(data => {
            // Validate the response data - OpenWeatherMap API structure
            if (data && data.coord && typeof data.coord.lat === 'number' && typeof data.coord.lon === 'number' && 
                data.main && typeof data.main.temp === 'number' && data.wind && typeof data.wind.speed === 'number') {
              // Transform OpenWeatherMap API response to our expected format
              return {
                lat: data.coord.lat,
                lon: data.coord.lon,
                temp: data.main.temp,
                feels_like: data.main.feels_like || data.main.temp,
                humidity: data.main.humidity || 0,
                wind_speed: data.wind.speed,
                wind_deg: data.wind.deg || 0,
                pressure: data.main.pressure || 1013,
                weather: data.weather || [],
                cityName: city.name
              };
            } else {
              console.warn(`Invalid weather data for ${city.name}:`, data);
              return null;
            }
          })
          .catch(err => {
            console.error(`Error fetching weather for ${city.name}:`, err);
            return null;
          })
      );

      const results = await Promise.all(weatherPromises);
      // Filter out null results and set valid weather data
      const validResults = results.filter(result => result !== null);
      setWeatherData(validResults);
      
      if (validResults.length === 0) {
        setError('No valid weather data received. Please check your API key and try again.');
      }
      
    } catch (err) {
      setError('Failed to fetch weather data');
      console.error('Weather fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch storm/cyclone data (enhanced simulation for authenticity)
  const fetchStormData = async () => {
    try {
      // Enhanced simulated storm data - more realistic positioning and movement
      const currentTime = Date.now();
      const simulatedStorms: StormData[] = [
        {
          id: 'storm1',
          name: 'Cyclone Biparjoy',
          lat: 20.5 + Math.sin(currentTime / 1000000) * 0.2, // Slight movement
          lon: 72.0 + Math.cos(currentTime / 1000000) * 0.2,
          wind_speed: 120 + Math.sin(currentTime / 500000) * 10, // Variable intensity
          pressure: 950 + Math.sin(currentTime / 1000000) * 20,
          category: 'H3',
          direction: 45 + Math.sin(currentTime / 2000000) * 5, // Slight direction change
          timestamp: currentTime
        },
        {
          id: 'storm2',
          name: 'Depression ARB01',
          lat: 15.2 + Math.sin(currentTime / 800000) * 0.15,
          lon: 73.5 + Math.cos(currentTime / 800000) * 0.15,
          wind_speed: 45 + Math.sin(currentTime / 400000) * 8,
          pressure: 1005 + Math.sin(currentTime / 800000) * 15,
          category: 'TS',
          direction: 30 + Math.sin(currentTime / 1500000) * 3,
          timestamp: currentTime
        },
        {
          id: 'storm3',
          name: 'Low Pressure Area',
          lat: 18.8 + Math.sin(currentTime / 1200000) * 0.1,
          lon: 75.2 + Math.cos(currentTime / 1200000) * 0.1,
          wind_speed: 25 + Math.sin(currentTime / 600000) * 5,
          pressure: 1010 + Math.sin(currentTime / 1200000) * 10,
          category: 'TD',
          direction: 60 + Math.sin(currentTime / 1800000) * 2,
          timestamp: currentTime
        }
      ];
      
      setStormData(simulatedStorms);
    } catch (err) {
      console.error('Storm data fetch error:', err);
    }
  };

  // Fetch all data
  const refreshData = async () => {
    await Promise.all([fetchWeatherData(), fetchStormData()]);
  };

  // Initial data fetch
  useEffect(() => {
    refreshData();
    
    // Refresh every 10 minutes
    const interval = setInterval(refreshData, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Handle map center change
  const handleMapMove = () => {
    if (mapRef.current) {
      const center = mapRef.current.getCenter();
      setMapCenter([center.lat, center.lng]);
    }
  };

  // Layer toggle handlers
  const toggleLayer = (layer: keyof typeof activeLayers) => {
    setActiveLayers(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };

  return (
    <div className="weather-map-container relative" style={{ height }}>
      {/* Map Controls */}
      {showControls && (
        <div className="absolute top-4 left-4 z-[1000] bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 space-y-2">
          <div className="flex items-center gap-2">
            <button
              onClick={refreshData}
              disabled={loading}
              className="btn btn-sm btn-primary"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
          
          <div className="space-y-1">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={activeLayers.temperature}
                onChange={() => toggleLayer('temperature')}
                className="checkbox checkbox-sm"
              />
              <Thermometer className="w-4 h-4 text-red-500" />
              Temperature
            </label>
            
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={activeLayers.wind}
                onChange={() => toggleLayer('wind')}
                className="checkbox checkbox-sm"
              />
              <Wind className="w-4 h-4 text-blue-500" />
              Wind
            </label>
            
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={activeLayers.storms}
                onChange={() => toggleLayer('storms')}
                className="checkbox checkbox-sm"
              />
              <AlertTriangle className="w-4 h-4 text-orange-500" />
              Storms
            </label>
            
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={activeLayers.heat}
                onChange={() => toggleLayer('heat')}
                className="checkbox checkbox-sm"
              />
              <Thermometer className="w-4 h-4 text-red-600" />
              Heat Map
            </label>
            
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={activeLayers.precipitation}
                onChange={() => toggleLayer('precipitation')}
                className="checkbox checkbox-sm"
              />
              <Droplets className="w-4 h-4 text-blue-600" />
              Precipitation
            </label>
            
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={activeLayers.pressure}
                onChange={() => toggleLayer('pressure')}
                className="checkbox checkbox-sm"
              />
              <Gauge className="w-4 h-4 text-purple-600" />
              Pressure
            </label>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="absolute top-4 right-4 z-[1000] bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded max-w-md">
          <div className="flex items-start gap-2">
            <div className="flex-shrink-0">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <h4 className="font-semibold text-red-800">Weather Map Error</h4>
              <p className="text-sm text-red-700 mt-1">{error}</p>
              {!API_KEY && (
                <div className="mt-2 text-xs text-red-600">
                  <p>To fix this:</p>
                  <ol className="list-decimal list-inside mt-1 space-y-1">
                    <li>Get API key from <a href="https://openweathermap.org/api" target="_blank" rel="noopener noreferrer" className="underline">OpenWeatherMap</a></li>
                    <li>Create <code>.env</code> file in frontend directory</li>
                    <li>Add: <code>VITE_OPENWEATHER_API_KEY=your_key_here</code></li>
                    <li>Restart the development server</li>
                  </ol>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Map */}
      <MapContainer
        center={mapCenter}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
      >
        {/* API Key Missing Message */}
        {!API_KEY && (
          <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-[999]">
            <div className="text-center p-6 bg-white rounded-lg shadow-lg max-w-md">
              <Cloud className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Weather Map Setup Required</h3>
              <p className="text-sm text-gray-600 mb-4">
                To display live weather data, you need to configure the OpenWeatherMap API key.
              </p>
              <div className="text-left text-xs text-gray-500 space-y-2">
                <p><strong>Steps to fix:</strong></p>
                <ol className="list-decimal list-inside space-y-1">
                  <li>Get free API key from <a href="https://openweathermap.org/api" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">OpenWeatherMap</a></li>
                  <li>Create <code>.env</code> file in frontend directory</li>
                  <li>Add: <code>VITE_OPENWEATHER_API_KEY=your_key_here</code></li>
                  <li>Restart development server</li>
                </ol>
              </div>
            </div>
          </div>
        )}
        
        {/* Loading Message */}
        {loading && (
          <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-[999]">
            <div className="text-center p-6 bg-white rounded-lg shadow-lg">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Loading Weather Data</h3>
              <p className="text-sm text-gray-600">Fetching real-time weather information...</p>
            </div>
          </div>
        )}
        {/* Base Tile Layer */}
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Weather Satellite Layers */}
        {API_KEY && (
          <>
            {/* Temperature Heat Map */}
            <TileLayer
              url={`https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${API_KEY}`}
              attribution='&copy; OpenWeatherMap'
              opacity={activeLayers.heat ? 0.7 : 0}
            />
            
            {/* Precipitation Layer */}
            <TileLayer
              url={`https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${API_KEY}`}
              attribution='&copy; OpenWeatherMap'
              opacity={activeLayers.precipitation ? 0.6 : 0}
            />
            
            {/* Pressure Layer */}
            <TileLayer
              url={`https://tile.openweathermap.org/map/pressure_new/{z}/{x}/{y}.png?appid=${API_KEY}`}
              attribution='&copy; OpenWeatherMap'
              opacity={activeLayers.pressure ? 0.6 : 0}
            />
          </>
        )}

        {/* Temperature Markers */}
        {activeLayers.temperature && !loading && weatherData.length > 0 && weatherData
          .filter(weather => weather && typeof weather.lat === 'number' && typeof weather.lon === 'number' && !isNaN(weather.lat) && !isNaN(weather.lon))
          .map((weather, index) => (
          <Marker
            key={`temp-${index}`}
            position={[weather.lat, weather.lon]}
            icon={createTempIcon(weather.temp)}
          >
            <Popup>
              <div className="weather-popup">
                <h3 className="font-bold text-lg">{weather.cityName}</h3>
                <p className="text-2xl font-bold text-red-600">
                  {Math.round(weather.temp)}°C
                </p>
                <p className="text-sm text-gray-600">
                  Feels like: {Math.round(weather.feels_like)}°C
                </p>
                <p className="text-sm text-gray-600">
                  Humidity: {weather.humidity}%
                </p>
                <p className="text-sm text-gray-600">
                  Pressure: {weather.pressure} hPa
                </p>
                <p className="text-sm text-gray-600">
                  {weather.weather[0]?.description}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Wind Markers */}
        {activeLayers.wind && !loading && weatherData.length > 0 && weatherData
          .filter(weather => weather && typeof weather.lat === 'number' && typeof weather.lon === 'number' && !isNaN(weather.lat) && !isNaN(weather.lon))
          .map((weather, index) => (
          <Marker
            key={`wind-${index}`}
            position={[weather.lat, weather.lon]}
            icon={createWindIcon(weather.wind_speed, weather.wind_deg)}
          >
            <Popup>
              <div className="weather-popup">
                <h3 className="font-bold text-lg">{weather.cityName}</h3>
                <p className="text-lg font-bold text-blue-600">
                  Wind: {weather.wind_speed} m/s
                </p>
                <p className="text-sm text-gray-600">
                  Direction: {weather.wind_deg}°
                </p>
                <p className="text-sm text-gray-600">
                  {weather.weather[0]?.description}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Storm Markers */}
        {activeLayers.storms && !loading && stormData.length > 0 && stormData
          .filter(storm => storm && typeof storm.lat === 'number' && typeof storm.lon === 'number' && !isNaN(storm.lat) && !isNaN(storm.lon))
          .map((storm) => (
          <Marker
            key={storm.id}
            position={[storm.lat, storm.lon]}
            icon={createStormIcon(storm.category)}
          >
            <Popup>
              <div className="storm-popup">
                <h3 className="font-bold text-lg text-red-600">{storm.name}</h3>
                <p className="text-sm">
                  <strong>Category:</strong> {storm.category}
                </p>
                <p className="text-sm">
                  <strong>Wind Speed:</strong> {storm.wind_speed} km/h
                </p>
                <p className="text-sm">
                  <strong>Pressure:</strong> {storm.pressure} hPa
                </p>
                <p className="text-sm">
                  <strong>Direction:</strong> {storm.direction}°
                </p>
                <p className="text-xs text-gray-500">
                  Updated: {new Date(storm.timestamp).toLocaleString()}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Wind Direction Lines - Enhanced for authenticity */}
        {activeLayers.wind && !loading && weatherData.length > 0 && weatherData
          .filter(weather => weather && typeof weather.lat === 'number' && typeof weather.lon === 'number' && !isNaN(weather.lat) && !isNaN(weather.lon))
          .map((weather, index) => {
          const windSpeed = weather.wind_speed;
          const windDeg = weather.wind_deg;
          
          // Calculate wind direction line length based on speed
          const lineLength = Math.min(windSpeed / 10, 0.15); // Longer lines for stronger winds
          const endLat = weather.lat + (Math.sin(windDeg * Math.PI / 180) * lineLength);
          const endLon = weather.lon + (Math.cos(windDeg * Math.PI / 180) * lineLength);
          
          // Color coding based on wind speed (like news weather maps)
          let lineColor = '#00aa00'; // Light green for calm
          if (windSpeed > 15) lineColor = '#ffaa00'; // Orange for moderate
          if (windSpeed > 25) lineColor = '#ff6600'; // Dark orange for strong
          if (windSpeed > 35) lineColor = '#ff0000'; // Red for very strong
          
          return (
            <Polyline
              key={`wind-line-${index}`}
              positions={[
                [weather.lat, weather.lon],
                [endLat, endLon]
              ]}
              color={lineColor}
              weight={Math.min(windSpeed / 3, 6)}
              opacity={0.8}
            />
          );
        })}

        {/* Storm Path Prediction */}
        {activeLayers.storms && !loading && stormData.length > 0 && stormData
          .filter(storm => storm && typeof storm.lat === 'number' && typeof storm.lon === 'number' && !isNaN(storm.lat) && !isNaN(storm.lon))
          .map((storm) => {
          const pathPoints: [number, number][] = [];
          let currentLat = storm.lat;
          let currentLon = storm.lon;
          
          // Simulate storm path for next 24 hours
          for (let i = 0; i < 24; i++) {
            currentLat += Math.sin(storm.direction * Math.PI / 180) * 0.01;
            currentLon += Math.cos(storm.direction * Math.PI / 180) * 0.01;
            pathPoints.push([currentLat, currentLon]);
          }
          
          return (
            <Polyline
              key={`storm-path-${storm.id}`}
              positions={pathPoints}
              color="#ff0000"
              weight={3}
              opacity={0.6}
              dashArray="10, 5"
            />
          );
        })}
      </MapContainer>

      {/* Enhanced Legend */}
      <div className="absolute bottom-4 right-4 z-[1000] bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 text-sm max-w-48">
        <h4 className="font-bold mb-2">Weather Legend</h4>
        <div className="space-y-2">
          {/* Temperature */}
          <div className="border-b border-gray-200 pb-2">
            <p className="font-semibold text-xs text-gray-600 mb-1">Temperature</p>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-xs">High (&gt;30°C)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                <span className="text-xs">Medium (20-30°C)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-xs">Low (&lt;20°C)</span>
              </div>
            </div>
          </div>
          
          {/* Wind */}
          <div className="border-b border-gray-200 pb-2">
            <p className="font-semibold text-xs text-gray-600 mb-1">Wind Speed</p>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-xs">Calm (&lt;15 m/s)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                <span className="text-xs">Moderate (15-25 m/s)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-xs">Strong (&gt;25 m/s)</span>
              </div>
            </div>
          </div>
          
          {/* Storms */}
          <div>
            <p className="font-semibold text-xs text-gray-600 mb-1">Storm Categories</p>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-lg">🌪️</span>
                <span className="text-xs">Cyclone/Hurricane</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg">💨</span>
                <span className="text-xs">Tropical Storm</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg">☁️</span>
                <span className="text-xs">Low Pressure</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WeatherMap;
