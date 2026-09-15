"use client";

import React, { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";

interface MapLibreViewProps {
  cameras?: any[];
  routeGeoJSON?: any;
  selectedCameraId?: string;
  onCameraSelect?: (camera: any) => void;
  center?: [number, number];
  zoom?: number;
  className?: string;
}

export function MapLibreView({
  cameras = [],
  routeGeoJSON,
  selectedCameraId,
  onCameraSelect,
  center = [72.53, 23.06], // Centered around SG Highway, Ahmedabad
  zoom = 11.5,
  className = "w-full h-full min-h-[450px]"
}: MapLibreViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (!mapContainer.current) return;

    // Free OpenStreetMap vector/raster dark tile style
    const darkStyle: maplibregl.StyleSpecification = {
      version: 8,
      sources: {
        "osm-tiles": {
          type: "raster",
          tiles: [
            "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
            "https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
            "https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
          ],
          tileSize: 256,
          attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org">OSM</a>'
        },
      },
      layers: [
        {
          id: "osm-layer",
          type: "raster",
          source: "osm-tiles",
          minzoom: 0,
          maxzoom: 19,
        },
      ],
    };

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: darkStyle,
      center: center,
      zoom: zoom,
      attributionControl: false,
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");

    map.on("load", () => {
      mapInstance.current = map;
      renderRoute(map, routeGeoJSON);
    });

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      map.remove();
    };
  }, []);

  // Update Route Polyline when routeGeoJSON changes
  useEffect(() => {
    if (!mapInstance.current || !mapInstance.current.isStyleLoaded()) return;
    renderRoute(mapInstance.current, routeGeoJSON);
  }, [routeGeoJSON]);

  // Update Camera Markers
  useEffect(() => {
    if (!mapInstance.current) return;

    // Clear existing markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    cameras.forEach((cam) => {
      const isSelected = cam.id === selectedCameraId;
      const isOnline = cam.status === "ONLINE";

      // Create custom DOM element for camera marker
      const el = document.createElement("div");
      el.className = "cursor-pointer group relative";
      el.innerHTML = `
        <div class="relative flex items-center justify-center">
          <div class="w-3.5 h-3.5 rounded-full ${
            isSelected
              ? "bg-police-gold ring-4 ring-police-gold/40 scale-125"
              : isOnline
              ? "bg-telemetry-green ring-2 ring-black"
              : "bg-alert-red ring-2 ring-black"
          } transition-all duration-200 group-hover:scale-150"></div>
          ${
            isSelected
              ? '<div class="absolute -inset-1 rounded-full bg-police-gold animate-ping opacity-75"></div>'
              : ""
          }
        </div>
      `;

      // Popup
      const popup = new maplibregl.Popup({ offset: 12, closeButton: false }).setHTML(`
        <div class="text-xs">
          <div class="font-bold text-white mb-0.5">${cam.name}</div>
          <div class="text-[10px] font-mono text-slate-400 mb-1">${cam.external_id} • ${cam.district}</div>
          <div class="flex items-center gap-1.5 text-[10px]">
            <span class="w-1.5 h-1.5 rounded-full ${isOnline ? "bg-telemetry-green" : "bg-alert-red"}"></span>
            <span class="text-slate-300 font-mono">${cam.status}</span>
            <span class="text-slate-400 font-mono ml-auto">${cam.manufacturer || "CCTV"}</span>
          </div>
        </div>
      `);

      el.addEventListener("click", () => {
        if (onCameraSelect) onCameraSelect(cam);
      });

      if (mapInstance.current) {
        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([cam.longitude, cam.latitude])
          .setPopup(popup)
          .addTo(mapInstance.current);

        markersRef.current.push(marker);
      }
    });
  }, [cameras, selectedCameraId]);

  function renderRoute(map: maplibregl.Map, geojson: any) {
    if (!geojson) return;

    if (map.getSource("route-source")) {
      (map.getSource("route-source") as maplibregl.GeoJSONSource).setData(geojson);
    } else {
      map.addSource("route-source", {
        type: "geojson",
        data: geojson,
      });

      // Route Glow Layer
      map.addLayer({
        id: "route-glow",
        type: "line",
        source: "route-source",
        filter: ["==", "$type", "LineString"],
        layout: {
          "line-join": "round",
          "line-cap": "round",
        },
        paint: {
          "line-color": "#F59E0B",
          "line-width": 8,
          "line-opacity": 0.4,
          "line-blur": 3,
        },
      });

      // Route Main Line
      map.addLayer({
        id: "route-line",
        type: "line",
        source: "route-source",
        filter: ["==", "$type", "LineString"],
        layout: {
          "line-join": "round",
          "line-cap": "round",
        },
        paint: {
          "line-color": "#FBBF24",
          "line-width": 4,
          "line-dasharray": [1, 1.5],
        },
      });

      // Waypoint Point Circles
      map.addLayer({
        id: "route-points",
        type: "circle",
        source: "route-source",
        filter: ["==", "$type", "Point"],
        paint: {
          "circle-radius": 7,
          "circle-color": "#EF4444",
          "circle-stroke-width": 2,
          "circle-stroke-color": "#FFFFFF",
        },
      });
    }

    // Fit bounds to route
    const lineFeature = geojson.features?.find((f: any) => f.geometry.type === "LineString");
    if (lineFeature && lineFeature.geometry.coordinates.length > 0) {
      const bounds = new maplibregl.LngLatBounds();
      lineFeature.geometry.coordinates.forEach((coord: [number, number]) => {
        bounds.extend(coord);
      });
      map.fitBounds(bounds, { padding: 80, maxZoom: 14 });
    }
  }

  return (
    <div className={`relative overflow-hidden rounded-lg border border-surface-border bg-surface ${className}`}>
      <div ref={mapContainer} className="w-full h-full" />
      {/* Tactical Map Overlay Legend */}
      <div className="absolute bottom-3 left-3 bg-surface/90 backdrop-blur border border-surface-border rounded-md px-3 py-2 text-[10px] font-mono text-slate-300 flex items-center gap-4 pointer-events-none z-10">
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-telemetry-green" />
          <span>Online Node ({cameras.filter((c) => c.status === "ONLINE").length})</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-alert-red" />
          <span>Offline Node ({cameras.filter((c) => c.status === "OFFLINE").length})</span>
        </div>
        {routeGeoJSON && (
          <div className="flex items-center gap-1.5 text-police-gold">
            <div className="w-3 h-0.5 bg-police-gold" />
            <span>Target Route (GJ01AB1234)</span>
          </div>
        )}
      </div>
    </div>
  );
}
