import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, MapPin, Calendar, AlertTriangle, TrendingUp, Droplets } from 'lucide-react';
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

  const detectFlood = async () => {
    // Check if user is logged in
    if (!user) {
      toast.error('Please log in to use flood detection');
      return;
    }
    
    setFloodDetecting(true);
    setFloodResult(null);
    
    try {
      // Get user's current location (in a real app, this would come from GPS)
      // For demo purposes, we'll use a default location
      const defaultLocation = {
        latitude: 19.0760,  // Mumbai coordinates
        longitude: 72.8777,
        locationName: "Your Current Location"
      };
      
      const response = await axios.post('http://localhost:8000/flood/detect', defaultLocation);
      
      setFloodResult(response.data);
      toast.success('Flood detection completed!');
    } catch (error: any) {
      console.error('Error detecting flood:', error);
      if (error.response?.status === 401) {
        toast.error('Please log in to use flood detection');
      } else {
        toast.error(error.response?.data?.detail || 'Flood detection failed');
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
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white p-6 rounded-xl shadow-sm">
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="h-8 bg-gray-200 rounded w-1/3"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      {/* Welcome Section */}
      <div className="card bg-gradient-to-r from-blue-900 to-gray-900 dark:from-blue-900 dark:to-gray-950 text-white mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2 tracking-tight">
            Welcome back, {user?.name || user?.email?.split('@')[0]}!
          </h1>
          <p className="text-blue-200 text-lg">
            Monitor your areas of interest with real-time satellite data
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
            title={!user ? 'Please log in to use flood detection' : 'Detect flood risk for your location'}
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