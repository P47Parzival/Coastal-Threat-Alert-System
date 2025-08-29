import React, { useState, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, FeatureGroup, useMap } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import { Save, X, Maximize2, Minimize2, AlertTriangle, TrendingDown, Shield } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import axios from 'axios';
import toast from 'react-hot-toast';

// Fix for default markers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface ShorelineData {
  name: string;
  description: string;
  shorelinePath: any;
  monitoringFrequency: string;
  confidenceThreshold: number;
  emailAlerts: boolean;
  inAppNotifications: boolean;
}

interface ErosionAnalysis {
  threatLevel: 'HIGH' | 'MEDIUM' | 'LOW' | 'STABLE';
  erosionRate: number;
  riskScore: number;
  recommendations: string[];
  shorelineChange: number;
  floodRisk: 'HIGH' | 'MEDIUM' | 'LOW';
}

export default function ShorelineMonitoring() {
  const mapRef = useRef<L.Map | null>(null);
  const [drawnShoreline, setDrawnShoreline] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<ErosionAnalysis | null>(null);
  const [mapFullScreen, setMapFullScreen] = useState(false);
  const [formData, setFormData] = useState<ShorelineData>({
    name: '',
    description: '',
    shorelinePath: null,
    monitoringFrequency: 'weekly',
    confidenceThreshold: 70,
    emailAlerts: true,
    inAppNotifications: true,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({
        ...prev,
        [name]: checked
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const onCreated = (e: any) => {
    const { layer } = e;
    const geojson = layer.toGeoJSON();
    setDrawnShoreline(geojson);
    setFormData(prev => ({
      ...prev,
      shorelinePath: geojson
    }));
  };

  const onEdited = (e: any) => {
    const layers = e.layers;
    layers.eachLayer((layer: any) => {
      const geojson = layer.toGeoJSON();
      setDrawnShoreline(geojson);
      setFormData(prev => ({
        ...prev,
        shorelinePath: geojson
      }));
    });
  };

  const onDeleted = () => {
    setDrawnShoreline(null);
    setFormData(prev => ({
      ...prev,
      shorelinePath: null
    }));
  };

  const analyzeShoreline = async () => {
    if (!drawnShoreline) {
      toast.error('Please draw a shoreline path on the map');
      return;
    }

    if (!formData.name.trim()) {
      toast.error('Please enter a shoreline name');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/shoreline/analyze', {
        name: formData.name,
        description: formData.description,
        shorelinePath: drawnShoreline,
        monitoringFrequency: formData.monitoringFrequency,
        confidenceThreshold: formData.confidenceThreshold,
        emailAlerts: formData.emailAlerts,
        inAppNotifications: formData.inAppNotifications,
      });

      setAnalysisResult(response.data);
      toast.success('Shoreline analysis completed!');
    } catch (error: any) {
      console.error('Error analyzing shoreline:', error);
      toast.error(error.response?.data?.detail || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case 'HIGH':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'MEDIUM':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'LOW':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'STABLE':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getFloodRiskColor = (risk: string) => {
    switch (risk) {
      case 'HIGH':
        return 'bg-red-500 text-white';
      case 'MEDIUM':
        return 'bg-orange-500 text-white';
      case 'LOW':
        return 'bg-green-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Shoreline Monitoring
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Draw shoreline paths and analyze coastal erosion risks
          </p>
        </div>
        <button
          onClick={() => setMapFullScreen(!mapFullScreen)}
          className="btn btn-secondary flex items-center gap-2"
        >
          {mapFullScreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          {mapFullScreen ? 'Exit Fullscreen' : 'Fullscreen'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Map Section */}
        <div className={`${mapFullScreen ? 'fixed inset-0 z-50 bg-white dark:bg-gray-900' : ''}`}>
          <div className="relative">
            <MapContainer
              center={[20.5937, 78.9629]} // Center of India
              zoom={6}
              className={`h-96 lg:h-[600px] w-full rounded-lg shadow-lg ${
                mapFullScreen ? 'h-screen' : ''
              }`}
              ref={mapRef}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              
              <FeatureGroup>
                <EditControl
                  position="topright"
                  onCreated={onCreated}
                  onEdited={onEdited}
                  onDeleted={onDeleted}
                  draw={{
                    rectangle: false,
                    circle: false,
                    circlemark: false,
                    marker: false,
                    polygon: false,
                    polyline: {
                      shapeOptions: {
                        color: '#3B82F6',
                        weight: 3,
                        opacity: 0.8
                      }
                    }
                  }}
                />
              </FeatureGroup>
            </MapContainer>

            {mapFullScreen && (
              <button
                onClick={() => setMapFullScreen(false)}
                className="absolute top-4 right-4 z-10 bg-white dark:bg-gray-800 p-2 rounded-lg shadow-lg"
              >
                <X className="w-6 h-6" />
              </button>
            )}
          </div>

          {/* Map Instructions */}
          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
              📍 How to Draw Shoreline
            </h3>
            <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
              <li>• Use the <strong>Draw a polyline</strong> tool (line icon)</li>
              <li>• Click along the coastline to create points</li>
              <li>• Double-click to finish drawing</li>
              <li>• You can edit or delete the line after drawing</li>
            </ul>
          </div>
        </div>

        {/* Form and Analysis Section */}
        <div className="space-y-6">
          {/* Shoreline Information Form */}
          <div className="card bg-white dark:bg-gray-800">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Shoreline Information
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Shoreline Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="input w-full"
                  placeholder="e.g., Mumbai Coastline, Goa Beach"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={3}
                  className="input w-full"
                  placeholder="Describe the shoreline characteristics, location, or any specific concerns..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Monitoring Frequency
                  </label>
                  <select
                    name="monitoringFrequency"
                    value={formData.monitoringFrequency}
                    onChange={handleInputChange}
                    className="input w-full"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Confidence Threshold
                  </label>
                  <input
                    type="number"
                    name="confidenceThreshold"
                    value={formData.confidenceThreshold}
                    onChange={handleInputChange}
                    min="50"
                    max="95"
                    className="input w-full"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="emailAlerts"
                    checked={formData.emailAlerts}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Email Alerts</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="inAppNotifications"
                    checked={formData.inAppNotifications}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">In-App Notifications</span>
                </label>
              </div>
            </div>

            <button
              onClick={analyzeShoreline}
              disabled={!drawnShoreline || loading}
              className="btn btn-primary w-full mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Analyzing Shoreline...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <TrendingDown className="w-4 h-4" />
                  Analyze Erosion Risk
                </div>
              )}
            </button>
          </div>

          {/* Analysis Results */}
          {analysisResult && (
            <div className="card bg-white dark:bg-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Erosion Risk Analysis
              </h3>

              <div className="space-y-4">
                {/* Threat Level */}
                <div className={`p-4 rounded-lg border-2 ${getThreatLevelColor(analysisResult.threatLevel)}`}>
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="w-6 h-6" />
                    <div>
                      <h4 className="font-semibold">Threat Level: {analysisResult.threatLevel}</h4>
                      <p className="text-sm opacity-80">
                        {analysisResult.threatLevel === 'HIGH' && 'Severe erosion detected - Immediate action required'}
                        {analysisResult.threatLevel === 'MEDIUM' && 'Moderate erosion - Enhanced monitoring recommended'}
                        {analysisResult.threatLevel === 'LOW' && 'Minor erosion - Continue monitoring'}
                        {analysisResult.threatLevel === 'STABLE' && 'Shoreline appears stable'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Erosion Rate</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {analysisResult.erosionRate.toFixed(2)} m/day
                    </p>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Risk Score</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {analysisResult.riskScore.toFixed(1)}/10
                    </p>
                  </div>
                </div>

                {/* Flood Risk */}
                <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Future Flood Risk</p>
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getFloodRiskColor(analysisResult.floodRisk)}`}>
                      {analysisResult.floodRisk}
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {analysisResult.floodRisk === 'HIGH' && 'Severe erosion indicates high future flood risk'}
                      {analysisResult.floodRisk === 'MEDIUM' && 'Moderate erosion suggests increased flood vulnerability'}
                      {analysisResult.floodRisk === 'LOW' && 'Low erosion means minimal flood risk increase'}
                    </span>
                  </div>
                </div>

                {/* Shoreline Change */}
                <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Shoreline Change</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {analysisResult.shorelineChange.toFixed(2)} meters
                  </p>
                </div>

                {/* Recommendations */}
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                    Recommendations
                  </h4>
                  <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                    {analysisResult.recommendations.map((rec, index) => (
                      <li key={index}>• {rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
