import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Circle, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import type { FusedLocation } from '../types';

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const DEFAULT_CENTER: [number, number] = [13.0827, 80.2707];

function MapUpdater({ center, zoom }: { center: [number, number], zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, {
      animate: true,
      duration: 1.5,
      easeLinearity: 0.25
    });
  }, [center, zoom, map]);
  return null;
}

interface MapViewProps {
  fusedLocation: FusedLocation | null;
}

export default function MapView({ fusedLocation }: MapViewProps) {
  const center: [number, number] = fusedLocation 
    ? [fusedLocation.fused_lat, fusedLocation.fused_lon] 
    : DEFAULT_CENTER;
    
  const radius = fusedLocation ? fusedLocation.uncertainty_radius_m : 0;
  const zoomLevel = fusedLocation ? 16 : 12;

  return (
    <div className="w-full h-full rounded-[2rem] overflow-hidden relative z-0 bg-slate-900 border border-slate-800">
      <MapContainer 
        center={center} 
        zoom={zoomLevel} 
        style={{ height: '100%', width: '100%', backgroundColor: '#0f172a' }}
        scrollWheelZoom={true}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        <MapUpdater center={center} zoom={zoomLevel} />

        {fusedLocation && (
          <>
            <Marker position={center} />

            <Circle 
              center={center} 
              radius={radius} 
              pathOptions={{ fillColor: '#3b82f6', color: '#3b82f6', weight: 2, fillOpacity: 0.35 }} 
            />
            <Circle 
              center={center} 
              radius={radius * 2} 
              pathOptions={{ fillColor: '#60a5fa', color: '#60a5fa', weight: 1, fillOpacity: 0.15, dashArray: '4' }} 
            />
            <Circle 
              center={center} 
              radius={radius * 2.6} 
              pathOptions={{ fillColor: '#93c5fd', color: '#93c5fd', weight: 1, fillOpacity: 0.05, dashArray: '2 8' }} 
            />
          </>
        )}
      </MapContainer>

      {/* Internal vignette bounds targeting black shadow to blend cleanly with dark map */}
      <div className="absolute inset-0 pointer-events-none shadow-[inset_0_0_100px_rgba(0,0,0,0.8)] rounded-[2rem] z-[400] transition-all duration-500"></div>
    </div>
  );
}
