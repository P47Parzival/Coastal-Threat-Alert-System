// src/components/map/MapComponent.tsx
import React from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css'; // The only CSS import needed
import { LatLngExpression } from 'leaflet';

const MapComponent: React.FC = () => {
  // Set initial map state for Gandhinagar, Gujarat
  const position: LatLngExpression = [23.2156, 72.5714];
  const zoomLevel = 13;

  // For the satellite view, we'll use Esri's World Imagery layer, 
  // which is high-quality and free to use for projects like this.
  const satelliteTileUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
  const attribution = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community';

  return (
    // The MapContainer component initializes the map and takes up the full space of its parent.
    <MapContainer 
      center={position} 
      zoom={zoomLevel} 
      scrollWheelZoom={true} // Enable zooming with the mouse wheel
      style={{ height: '100%', width: '100%', zIndex: 0 }} // Ensure map is in the background
    >
      {/* The TileLayer component is responsible for the map's visual base layer. */}
      <TileLayer
        url={satelliteTileUrl}
        attribution={attribution}
      />
    </MapContainer>
  );
};

export default MapComponent;