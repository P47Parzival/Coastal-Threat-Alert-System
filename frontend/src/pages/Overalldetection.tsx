import React, { useEffect, useRef } from 'react';

const OverallDetection: React.FC = () => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    // Optional: You can add any initialization logic here
    console.log('Overall Detection page loaded');
  }, []);

  return (
    <div className="h-full w-full">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          🌊 Overall Detection - Clay v1.5 System
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          AI-Powered Global Coastal Threat Detection using Geospatial Foundation Models
        </p>
      </div>
      
      {/* Embed the dashboard.html */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-full">
        <iframe
          ref={iframeRef}
          src="/dashboard.html"
          className="w-full h-full min-h-[800px] rounded-lg"
          title="Clay v1.5 Coastal Monitoring Dashboard"
          style={{ border: 'none' }}
        />
      </div>
    </div>
  );
};

export default OverallDetection;