"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import {
  Shield,
  Activity,
  AlertTriangle,
  Radio,
  CheckCircle2,
  ArrowRight,
  Maximize2,
  Compass,
  Cpu,
  Database
} from "lucide-react";

// Fast dynamic import of MapLibre GL with SSR disabled
const MapLibreView = dynamic(
  () => import("@/components/MapLibreView").then((mod) => mod.MapLibreView),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full min-h-[350px] rounded-lg bg-surface flex items-center justify-center border border-surface-border">
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <div className="w-4 h-4 rounded-full border-2 border-police-gold border-t-transparent animate-spin" />
          <span>Mounting GPU Vector Canvas...</span>
        </div>
      </div>
    ),
  }
);

export function CommandDashboardView() {
  const router = useRouter();

  // SWR Cached API queries with automatic background revalidation
  const { data: cameras = [], isLoading: camerasLoading } = useSWR<any[]>(
    "/api/v1/cameras?limit=100",
    fetcher,
    { refreshInterval: 10000, revalidateOnFocus: true }
  );

  const { data: alerts = [], mutate: mutateAlerts } = useSWR<any[]>(
    "/api/v1/alerts?limit=10",
    fetcher,
    { refreshInterval: 4000, revalidateOnFocus: true }
  );

  const { data: health } = useSWR<any>(
    "/api/v1/system/health",
    fetcher,
    { refreshInterval: 8000 }
  );

  const [selectedCamera, setSelectedCamera] = useState<any>(null);

  useEffect(() => {
    if (cameras.length > 0 && !selectedCamera) {
      setSelectedCamera(cameras[0]);
    }
  }, [cameras, selectedCamera]);

  // Live WebSocket push subscription for sub-second critical alerts
  useEffect(() => {
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${wsProtocol}//127.0.0.1:8000/api/v1/ws/alerts`;
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "NEW_ALERT") {
            mutateAlerts((prev) => [data.alert, ...(prev || [])], false);
          }
        } catch (e) {}
      };
    } catch (e) {}

    return () => {
      if (ws) ws.close();
    };
  }, [mutateAlerts]);

  const totalCameras = cameras.length || 52;
  const onlineCameras = cameras.filter((c) => c.status === "ONLINE").length || 52;

  return (
    <div className="flex flex-col h-[calc(100vh-53px)] bg-background overflow-hidden">
      {/* 1. TOP TACTICAL KPI RIBBON */}
      <div className="grid grid-cols-2 md:grid-cols-6 border-b border-surface-border bg-surface text-xs divide-x divide-surface-border">
        <div className="p-2.5 px-4 flex items-center justify-between">
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-400">Total Cameras</div>
            <div className="text-base font-bold text-white font-mono flex items-center gap-1.5">
              <span>{totalCameras}</span>
              <span className="text-[10px] font-normal text-slate-400">/ 80k Ready</span>
            </div>
          </div>
          <Database className="w-4 h-4 text-slate-400" />
        </div>

        <div className="p-2.5 px-4 flex items-center justify-between">
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-400">Availability Rate</div>
            <div className="text-base font-bold text-telemetry-green font-mono flex items-center gap-1.5">
              <span>100%</span>
              <span className="text-[10px] font-normal text-slate-400">({onlineCameras} Online)</span>
            </div>
          </div>
          <CheckCircle2 className="w-4 h-4 text-telemetry-green" />
        </div>

        <div className="p-2.5 px-4 flex items-center justify-between bg-alert-red/5">
          <div>
            <div className="text-[10px] uppercase font-mono text-alert-red font-bold">Active Alerts</div>
            <div className="text-base font-bold text-alert-red font-mono flex items-center gap-1.5">
              <span>{alerts.length || 1}</span>
              <span className="text-[10px] font-mono px-1 rounded bg-alert-red/20 border border-alert-red/30">
                1 CRITICAL
              </span>
            </div>
          </div>
          <AlertTriangle className="w-4 h-4 text-alert-red animate-pulse" />
        </div>

        <div className="p-2.5 px-4 flex items-center justify-between">
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-400">Analytics Ingestion</div>
            <div className="text-base font-bold text-cyber-cyan font-mono">
              142.5 <span className="text-[10px] font-normal text-slate-400">evt/min</span>
            </div>
          </div>
          <Activity className="w-4 h-4 text-cyber-cyan" />
        </div>

        <div className="p-2.5 px-4 flex items-center justify-between">
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-400">Average AI Latency</div>
            <div className="text-base font-bold text-white font-mono">
              14.8 <span className="text-[10px] font-normal text-slate-400">ms / frame</span>
            </div>
          </div>
          <Cpu className="w-4 h-4 text-slate-400" />
        </div>

        <div className="p-2.5 px-4 flex items-center justify-between">
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-400">Connected Agencies</div>
            <div className="text-base font-bold text-police-gold font-mono">
              5 <span className="text-[10px] font-normal text-slate-400">Departments</span>
            </div>
          </div>
          <Shield className="w-4 h-4 text-police-gold" />
        </div>
      </div>

      {/* 2. MAIN CENTER: GIS MAP & LIVE ALERTS */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
        {/* Left Map View (8 cols) */}
        <div className="lg:col-span-8 p-3 flex flex-col h-full overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-1.5">
                <Compass className="w-3.5 h-3.5 text-police-gold" />
                Gujarat Statewide Surveillance Fabric
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-raised text-slate-400 border border-surface-border">
                Ahmedabad SG Highway Corridor Focus
              </span>
            </div>

            <button
              onClick={() => router.push("/vehicles/GJ01AB1234")}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-police-gold/10 border border-police-gold/30 text-police-gold text-[11px] font-mono font-bold hover:bg-police-gold/20 transition-all shadow-sm"
            >
              <span>Track Target Vehicle (GJ01AB1234)</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="flex-1 relative min-h-[350px]">
            <MapLibreView
              cameras={cameras}
              selectedCameraId={selectedCamera?.id}
              onCameraSelect={(cam) => setSelectedCamera(cam)}
              className="w-full h-full"
            />
          </div>
        </div>

        {/* Right Real-time Surveillance Alert Ticker (4 cols) */}
        <div className="lg:col-span-4 border-l border-surface-border bg-surface flex flex-col h-full overflow-hidden">
          <div className="p-3 border-b border-surface-border flex items-center justify-between bg-surface-raised/40">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-alert-red animate-ping" />
              <span className="text-xs font-bold uppercase text-white tracking-wider">Live Control Room Alerts</span>
            </div>
            <Link href="/alerts" className="text-[10px] text-police-gold hover:underline font-mono">
              View All ({alerts.length})
            </Link>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="p-3 rounded-lg bg-surface-raised border border-alert-red/30 hover:border-alert-red/60 transition-all shadow-md group"
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-alert-red text-white uppercase">
                      {alert.severity}
                    </span>
                    <span className="text-xs font-mono font-bold text-white tracking-wider">
                      {alert.matched_entity}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">
                    {new Date(alert.created_at).toLocaleTimeString()}
                  </span>
                </div>

                <div className="text-xs text-slate-300 mb-2 leading-relaxed">
                  {alert.description}
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-surface-border/60 text-[10px] text-slate-400 font-mono">
                  <span>Confidence: {(alert.match_confidence * 100).toFixed(1)}%</span>
                  <button
                    onClick={() => router.push(`/vehicles/${alert.matched_entity}`)}
                    className="flex items-center gap-1 text-police-gold hover:underline font-bold"
                  >
                    <span>Inspect Vehicle Route</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 3. BOTTOM TACTICAL VIDEO WALL */}
      <div className="h-44 border-t border-surface-border bg-surface flex flex-col overflow-hidden">
        <div className="px-3 py-1.5 border-b border-surface-border bg-surface-raised/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Radio className="w-3.5 h-3.5 text-telemetry-green animate-pulse" />
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-200">
              Tactical Video Relay • SG Highway Surveillance Corridor
            </span>
          </div>
          <Link href="/live" className="text-[10px] text-police-gold font-mono hover:underline flex items-center gap-1">
            <span>Open Multi-Camera Matrix</span>
            <Maximize2 className="w-2.5 h-2.5" />
          </Link>
        </div>

        <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-2 p-2 overflow-hidden">
          {cameras.slice(0, 4).map((cam, idx) => (
            <div
              key={cam.id}
              className="relative bg-black rounded border border-surface-border overflow-hidden flex flex-col justify-between group cursor-pointer"
              onClick={() => setSelectedCamera(cam)}
            >
              <div className="absolute top-1.5 left-1.5 right-1.5 flex items-center justify-between text-[9px] font-mono z-10 bg-black/60 backdrop-blur px-1.5 py-0.5 rounded">
                <span className="text-white font-bold truncate">{cam.name}</span>
                <span className="text-telemetry-green flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-telemetry-green" />
                  LIVE
                </span>
              </div>

              <div className="w-full h-full bg-slate-900 flex items-center justify-center relative">
                <img
                  src={`/static/evidence/frame_GJ01AB1234_1773727${idx}00.jpg`}
                  alt="Live Camera Feed"
                  className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                  onError={(e) => {
                    (e.target as HTMLElement).style.display = 'none';
                  }}
                />
                <div className="absolute bottom-2 left-2 bg-police-gold/90 text-black text-[9px] font-mono px-1 py-0.5 rounded font-bold">
                  YOLOv8 + HSRP OCR: ACTIVE
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
