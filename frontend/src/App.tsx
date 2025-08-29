// src/App.tsx
import React from 'react';
import MapComponent from './components/map/MapComponent';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';

const App: React.FC = () => {
  return (
    <div className="relative h-screen w-screen overflow-hidden">
      {/* The Map will be the background layer */}
      <MapComponent />

      {/* UI elements are layered on top */}
      <Header />
      <Sidebar />
    </div>
  );
}

export default App;