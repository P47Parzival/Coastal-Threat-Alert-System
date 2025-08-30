import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, MapPin, Calendar, AlertTriangle, TrendingUp, Droplets, Navigation } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

interface AOI {
  _id: string;
  name: string;
  changeType: string;
  monitoringFrequency: string;
  status: string;
  createdAt: string;
  lastMonitored?: string;
}

interface LocationData {
  latitude: number;
  longitude: number;
  accuracy?: number | null;
  timestamp: number;
}

export default function Dashboard() {
  const { user } = useAuth();
  const [aois, setAois] = useState<AOI[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalAOIs: 0,
    activeMonitoring: 0,
    recentAlerts: 0,
    coverageArea: '0 km²'
  });
  const [floodDetecting, setFloodDetecting] = useState(false);
  const [floodResult, setFloodResult] = useState<any>(null);
  const [locationStatus, setLocationStatus] = useState<'idle' | 'requesting' | 'success' | 'error'>('idle');
  const [userLocation, setUserLocation] = useState<LocationData | null>(null);
  const [locationError, setLocationError] = useState<string>('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/aois/');
      setAois(response.data);
      
      // Calculate stats
      const totalAOIs = response.data.length;
      const activeMonitoring = response.data.filter((aoi: AOI) => aoi.status === 'active').length;
      const recentAlerts = Math.floor(Math.random() * 5); // Mock data
      
      setStats({
        totalAOIs,
        activeMonitoring,
        recentAlerts,
        coverageArea: `${(totalAOIs * 2.5).toFixed(1)} km²` // Mock calculation
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentLocation = (): Promise<LocationData> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser'));
        return;
      }

      const options = {
        enableHighAccuracy: true,
        timeout: 10000, // 10 seconds
        maximumAge: 60000 // 1 minute
      };

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const locationData: LocationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: position.timestamp
          };
          resolve(locationData);
        },
        (error) => {
          let errorMessage = 'Unknown error occurred';
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Location permission denied. Please enable location access in your browser settings.';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Location information is unavailable.';
              break;
            case error.TIMEOUT:
              errorMessage = 'Location request timed out. Please try again.';
              break;
          }
          reject(new Error(errorMessage));
        },
        options
      );
    });
  };

  const detectFlood = async () => {
    // Check if user is logged in
    if (!user) {
      toast.error('Please log in to use flood detection');
      return;
    }
    
    setFloodDetecting(true);
    setFloodResult(null);
    setLocationStatus('requesting');
    setLocationError('');
    
    try {
      // Get user's current GPS location
      toast.loading('Getting your current location...', { id: 'location' });
      
      const locationData = await getCurrentLocation();
      setUserLocation(locationData);
      setLocationStatus('success');
      
      toast.success(`Location captured! Accuracy: ${locationData.accuracy ? Math.round(locationData.accuracy) : 'Unknown'}m`, { id: 'location' });
      
      // Get location name using reverse geocoding (optional)
      let locationName = "Your Current Location";
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${locationData.latitude}&lon=${locationData.longitude}&zoom=10`
        );
        const data = await response.json();
        if (data.display_name) {
          locationName = data.display_name.split(',')[0]; // Get first part of address
        }
      } catch (error) {
        console.log('Could not get location name, using default');
      }
      
      // Prepare location data for flood detection
      const locationPayload = {
        latitude: locationData.latitude,
        longitude: locationData.longitude,
        locationName: locationName,
        accuracy: locationData.accuracy,
        timestamp: locationData.timestamp
      };
      
      toast.loading('Analyzing flood risk with real-time data...', { id: 'flood' });
      
      const response = await axios.post('http://localhost:8000/flood/detect', locationPayload);
      
      setFloodResult(response.data);
      toast.success('Flood detection completed!', { id: 'flood' });
      
    } catch (error: any) {
      console.error('Error detecting flood:', error);
      
      if (error.message && error.message.includes('Location')) {
        // Location-related error
        setLocationStatus('error');
        setLocationError(error.message);
        toast.error(error.message, { id: 'location' });
        
        // Ask user if they want to use default location
        if (confirm('Would you like to use a default location (Mumbai) for flood detection?')) {
          const defaultLocation = {
            latitude: 19.0760,
            longitude: 72.8777,
            locationName: "Default Location (Mumbai)",
            accuracy: null,
            timestamp: Date.now()
          };
          
          setUserLocation(defaultLocation);
          setLocationStatus('success');
          
          toast.loading('Analyzing flood risk with default location...', { id: 'flood' });
          
          const response = await axios.post('http://localhost:8000/flood/detect', defaultLocation);
          setFloodResult(response.data);
          toast.success('Flood detection completed!', { id: 'flood' });
        }
      } else if (error.response?.status === 401) {
        toast.error('Please log in to use flood detection', { id: 'flood' });
      } else {
        toast.error(error.response?.data?.detail || 'Flood detection failed', { id: 'flood' });
      }
    } finally {
      setFloodDetecting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getLocationStatusIcon = () => {
    switch (locationStatus) {
      case 'requesting':
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>;
      case 'success':
        return <Navigation className="inline-block w-4 h-4 text-green-600" />;
      case 'error':
        return <Navigation className="inline-block w-4 h-4 text-red-600" />;
      default:
        return <Navigation className="inline-block w-4 h-4 text-gray-400" />;
    }
  };

  const getLocationStatusText = () => {
    switch (locationStatus) {
      case 'requesting':
        return 'Getting location...';
      case 'success':
        return userLocation ? 
          `${userLocation.latitude.toFixed(4)}, ${userLocation.longitude.toFixed(4)}` : 
          'Location captured';
      case 'error':
        return 'Location error';
      default:
        return 'Click to detect flood';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Welcome back, {user?.name}! Here's an overview of your monitoring activities.
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/create-aoi"
            className="btn btn-primary flex items-center gap-2 shadow-lg"
          >
            <Plus className="inline-block w-5 h-5" />
            Create AOI
          </Link>
          
          <button
            onClick={detectFlood}
            disabled={floodDetecting || !user}
            className={`btn flex items-center gap-2 shadow-lg ${
              !user ? 'btn-disabled opacity-50 cursor-not-allowed' : 'btn-secondary'
            }`}
            title={!user ? 'Please log in to use flood detection' : 'Detect flood risk for your current location'}
          >
            {floodDetecting ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
            ) : (
              <Droplets className="inline-block w-5 h-5" />
            )}
            {floodDetecting ? 'Detecting...' : 'Detect Flood'}
          </button>
        </div>
      </div>

      {/* Location Status */}
      {locationStatus !== 'idle' && (
        <div className={`card bg-white dark:bg-[var(--color-card-dark)] ${
          locationStatus === 'error' ? 'border-red-200 dark:border-red-800' : 
          locationStatus === 'success' ? 'border-green-200 dark:border-green-800' : 
          'border-blue-200 dark:border-blue-800'
        }`}>
          <div className="flex items-center gap-3">
            {getLocationStatusIcon()}
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {getLocationStatusText()}
              </p>
              {locationStatus === 'success' && userLocation && (
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Accuracy: {userLocation.accuracy ? `${Math.round(userLocation.accuracy)}m` : 'Unknown'} • 
                  Captured: {new Date(userLocation.timestamp).toLocaleTimeString()}
                </p>
              )}
              {locationStatus === 'error' && locationError && (
                <p className="text-xs text-red-600 dark:text-red-400">
                  {locationError}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card flex items-center gap-4 bg-white dark:bg-[var(--color-card-dark)]">
          <MapPin className="h-8 w-8 text-blue-500" />
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Total AOIs</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalAOIs}</p>
          </div>
        </div>
        <div className="card flex items-center gap-4 bg-white dark:bg-[var(--color-card-dark)]">
          <TrendingUp className="h-8 w-8 text-green-500" />
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Active Monitoring</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.activeMonitoring}</p>
          </div>
        </div>
        <div className="card flex items-center gap-4 bg-white dark:bg-[var(--color-card-dark)]">
          <AlertTriangle className="h-8 w-8 text-orange-500" />
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Recent Alerts</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.recentAlerts}</p>
          </div>
        </div>
        <div className="card flex items-center gap-4 bg-white dark:bg-[var(--color-card-dark)]">
          <Calendar className="h-8 w-8 text-purple-500" />
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Coverage Area</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.coverageArea}</p>
          </div>
        </div>
      </div>

      {/* Recent AOIs */}
      <div className="card bg-white dark:bg-[var(--color-card-dark)]">
        <div className="flex items-center justify-between mb-4 border-b border-gray-200 dark:border-gray-800 pb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Recent AOIs</h2>
          <Link
            to="/aois"
            className="btn btn-secondary"
          >
            View all
          </Link>
        </div>
        {aois.length > 0 ? (
          <div className="divide-y divide-gray-200 dark:divide-gray-800">
            {aois.slice(0, 5).map((aoi) => (
              <div key={aoi._id} className="py-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">{aoi.name}</h3>
                  <div className="mt-1 flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span>Type: {aoi.changeType}</span>
                    <span>Frequency: {aoi.monitoringFrequency}</span>
                    <span>Created: {formatDate(aoi.createdAt)}</span>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(aoi.status)}`}>{aoi.status}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 dark:text-gray-400 py-8 text-center">No AOIs found.</div>
        )}
      </div>

      {/* Flood Detection Results */}
      {floodResult && (
        <div className="card bg-white dark:bg-gray-800">
          <div className="flex items-center justify-between mb-4 border-b border-gray-200 dark:border-gray-800 pb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Flood Detection Results</h2>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              floodResult.analysis.floodRisk === 'CRITICAL' ? 'bg-red-100 text-red-800' :
              floodResult.analysis.floodRisk === 'HIGH' ? 'bg-orange-100 text-orange-800' :
              floodResult.analysis.floodRisk === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {floodResult.analysis.floodRisk} Risk
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Risk Score</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {floodResult.analysis.riskScore.toFixed(0)}/100
              </p>
            </div>
            
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Time to Flood</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {floodResult.analysis.timeToFlood}
              </p>
            </div>
            
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Water Level</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {(floodResult.analysis.waterLevel * 100).toFixed(1)}%
              </p>
            </div>
            
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Confidence</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {(floodResult.analysis.confidence * 100).toFixed(0)}%
              </p>
            </div>
          </div>
          
          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
              Location: {floodResult.location}
            </h4>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              Analysis completed at {new Date(floodResult.analysis.analysisDate).toLocaleString()}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}