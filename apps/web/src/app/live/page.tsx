"use client";

import React, { useState, useEffect } from "react";
import { Video, Maximize2, Radio, Activity, Eye, Shield } from "lucide-react";

export default function TacticalVideoWall() {
  const [cameras, setCameras] = useState<any[]>([]);
  const [gridMode, setGridMode] = useState<"2x2" | "3x3">("2x2");
  const [activeCam, setActiveCam] = useState<any>(null);

  useEffect(() => {
    fetch("/api/v1/cameras?limit=9")
      .then((r) => r.json())
      .then((data) => {
        setCameras(data);
        if (data.length > 0) setActiveCam(data[0]);
      });
  }, []);

  const displayCount = gridMode === "2x2" ? 4 : 9;
  const currentCameras = cameras.slice(0, displayCount);

  return (
    <div className="p-4 max-w-7xl mx-auto space-y-4">
      {/* Header & Matrix Control */}
      <div className="flex items-center justify-between p-3 rounded-lg bg-surface border border-surface-border">
        <div className="flex items-center gap-2">
          <Video className="w-5 h-5 text-police-gold" />
          <div>
            <h1 className="text-sm font-bold text-white uppercase tracking-wider">
              Tactical Video Relay Matrix (MediaMTX Edge Relay)
            </h1>
            <p className="text-[10px] text-slate-400 font-mono">
              Live Low-Latency WebRTC & HLS Ingestion • AI Bounding Box Overlays
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex rounded border border-surface-border bg-surface-raised p-0.5 text-xs font-mono">
            <button
              onClick={() => setGridMode("2x2")}
              className={`px-3 py-1 rounded ${
                gridMode === "2x2" ? "bg-police-gold text-black font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              2x2 Grid
            </button>
            <button
              onClick={() => setGridMode("3x3")}
              className={`px-3 py-1 rounded ${
                gridMode === "3x3" ? "bg-police-gold text-black font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              3x3 Grid
            </button>
          </div>
        </div>
      </div>

      {/* Video Matrix Grid */}
      <div
        className={`grid gap-3 ${
          gridMode === "2x2" ? "grid-cols-1 md:grid-cols-2" : "grid-cols-1 md:grid-cols-3"
        }`}
      >
        {currentCameras.map((cam, idx) => (
          <div
            key={cam.id}
            className="relative bg-black rounded-lg border border-surface-border overflow-hidden shadow-xl aspect-video flex flex-col justify-between group"
          >
            {/* Top Bar OSD */}
            <div className="absolute top-2 left-2 right-2 flex items-center justify-between text-[11px] font-mono z-20 bg-black/70 backdrop-blur px-2 py-1 rounded">
              <span className="text-white font-bold truncate">{cam.name}</span>
              <span className="text-telemetry-green flex items-center gap-1.5 font-bold">
                <span className="w-2 h-2 rounded-full bg-telemetry-green animate-pulse" />
                WEBRTC 25 FPS
              </span>
            </div>

            {/* Video Snapshot with AI Detection Bounding Boxes */}
            <div className="w-full h-full relative flex items-center justify-center bg-slate-950">
              <img
                src={`/static/evidence/frame_GJ01AB1234_1773727${idx % 4}00.jpg`}
                alt={cam.name}
                className="w-full h-full object-cover opacity-85 group-hover:opacity-100 transition-opacity"
              />

              {/* Real-time Simulated AI Bounding Box Box */}
              <div className="absolute inset-0 pointer-events-none p-4 flex items-center justify-center">
                <div className="w-48 h-32 border-2 border-police-gold/80 rounded relative flex items-start justify-start p-1 shadow-lg shadow-police-gold/10">
                  <span className="bg-police-gold text-black text-[9px] font-mono font-black px-1 rounded">
                    CAR: 0.96 | GJ01AB1234
                  </span>
                </div>
              </div>
            </div>

            {/* Bottom Stream Telemetry Bar */}
            <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between text-[10px] font-mono text-slate-300 z-20 bg-black/70 backdrop-blur px-2 py-1 rounded">
              <span>{cam.district} • {cam.protocol}</span>
              <span className="text-cyber-cyan">Bitrate: 2450 kbps</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
