// src/components/layout/Sidebar.tsx
import React from 'react';

const Sidebar: React.FC = () => {
  return (
    <aside className="absolute top-20 left-4 z-10 w-80 bg-black/50 backdrop-blur-sm text-white p-4 rounded-lg shadow-xl">
      <h2 className="text-xl font-semibold mb-4 border-b border-gray-600 pb-2">Controls</h2>
      
      {/* Placeholder for Day 1 / Day 2 tasks */}
      <div className="space-y-4">
        <div>
          <label htmlFor="satellite-toggle" className="flex items-center justify-between cursor-pointer">
            <span>Satellite Overlay</span>
            {/* A basic switch toggle */}
            <div className="relative">
              <input type="checkbox" id="satellite-toggle" className="sr-only" />
              <div className="block bg-gray-600 w-14 h-8 rounded-full"></div>
              <div className="dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition"></div>
            </div>
          </label>
        </div>
        <div>
          <label htmlFor="time-slider" className="block mb-2 text-sm font-medium">Time Slider</label>
          <input type="range" id="time-slider" className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer" />
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;