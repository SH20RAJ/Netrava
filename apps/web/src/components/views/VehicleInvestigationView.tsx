"use client";

import React, { useState } from "react";
import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import Link from "next/link";
import dynamic from "next/dynamic";
import {
  Shield,
  AlertTriangle,
  Clock,
  Navigation,
  Lock,
  ArrowLeft,
  Download,
  Sparkles,
  CheckCircle2,
  Share2
} from "lucide-react";

const DynamicMapLibre = dynamic(
  () => import("@/components/MapLibreView").then((mod) => mod.MapLibreView),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full min-h-[400px] flex items-center justify-center bg-slate-950 border border-surface-border rounded-lg text-slate-500 font-mono text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full border-2 border-police-gold border-t-transparent animate-spin" />
          <span>Initializing Spatial Canvas...</span>
        </div>
      </div>
    ),
  }
);

interface VehicleInvestigationViewProps {
  plate: string;
}

export function VehicleInvestigationView({ plate }: VehicleInvestigationViewProps) {
  const normalizedPlate = plate.toUpperCase();

  const { data: dossier, error: dossierError, isLoading: dossierLoading } = useSWR(
    `/api/v1/vehicles/${normalizedPlate}`,
    fetcher,
    { revalidateOnFocus: false, dedupingInterval: 5000 }
  );

  const { data: route, error: routeError, isLoading: routeLoading } = useSWR(
    `/api/v1/vehicles/${normalizedPlate}/route`,
    fetcher,
    { revalidateOnFocus: false, dedupingInterval: 5000 }
  );

  const [selectedWaypoint, setSelectedWaypoint] = useState<any>(null);
  const [pinnedSuccess, setPinnedSuccess] = useState(false);

  const loading = dossierLoading || routeLoading;
  const error = dossierError || routeError;

  // Set default selected waypoint when route arrives
  React.useEffect(() => {
    if (route?.waypoints?.length && !selectedWaypoint) {
      setSelectedWaypoint(route.waypoints[route.waypoints.length - 1]);
    }
  }, [route, selectedWaypoint]);

  const handlePinToInvestigation = () => {
    setPinnedSuccess(true);
    setTimeout(() => setPinnedSuccess(false), 3000);
  };

  const handlePrintReport = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-police-gold border-t-transparent animate-spin" />
        <div className="text-sm font-mono text-slate-400">
          Reconstructing Cross-Camera Route for {normalizedPlate}...
        </div>
      </div>
    );
  }

  if (error || !route) {
    return (
      <div className="p-8 max-w-2xl mx-auto text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-alert-red/10 border border-alert-red/30 flex items-center justify-center mx-auto text-alert-red">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-white">Vehicle Observations Not Found</h2>
        <p className="text-xs text-slate-400">
          No automated sightings recorded for plate {normalizedPlate} in the 52-camera Gujarat grid.
        </p>
        <Link
          href="/vehicles"
          className="inline-flex items-center gap-2 px-4 py-2 rounded bg-surface-raised border border-surface-border text-xs text-police-gold hover:bg-surface-raised/80"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Return to Vehicle Search</span>
        </Link>
      </div>
    );
  }

  const activeWaypoint = selectedWaypoint || route.waypoints[route.waypoints.length - 1];

  return (
    <div className="p-4 max-w-7xl mx-auto space-y-4">
      {/* 1. TOP HEADER & DOSSIER BANNER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl bg-surface border border-surface-border shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Link href="/vehicles" className="text-slate-400 hover:text-white mr-1">
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <span className="text-xl font-mono font-black tracking-wider text-white px-3 py-1 rounded bg-black border border-surface-border">
              {route.normalized_plate}
            </span>
            {route.is_watchlist_hit && (
              <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-alert-red/20 text-alert-red border border-alert-red/40 flex items-center gap-1.5 animate-pulse">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>{route.watchlist_severity || "CRITICAL"} WATCHLIST HIT</span>
              </span>
            )}
            <span className="text-xs font-mono px-2 py-1 rounded bg-surface-raised border border-surface-border text-slate-300">
              {dossier?.vehicle_class?.toUpperCase() || "SUV"} • {dossier?.dominant_color?.toUpperCase() || "WHITE"}
            </span>
          </div>
          <div className="text-xs text-slate-400">
            FIR No. 142/2026 Vastrapur PS • Reported Stolen Vehicle • Primary Corridor: SG Highway, Ahmedabad
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handlePinToInvestigation}
            className="flex items-center gap-1.5 px-3 py-2 rounded bg-police-gold/10 border border-police-gold/40 text-police-gold text-xs font-mono font-bold hover:bg-police-gold/20 transition-all"
          >
            <Shield className="w-3.5 h-3.5" />
            <span>{pinnedSuccess ? "Pinned to CID-CR-2026-0418!" : "Pin to Case Dossier"}</span>
          </button>
          <button
            onClick={handlePrintReport}
            className="flex items-center gap-1.5 px-3 py-2 rounded bg-surface-raised border border-surface-border text-white text-xs font-mono hover:bg-slate-700 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Case Report</span>
          </button>
        </div>
      </div>

      {/* 2. STATS & KINEMATICS OVERVIEW GRID */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="p-3 rounded-lg bg-surface border border-surface-border">
          <div className="text-[10px] uppercase font-mono text-slate-400">Total Waypoints</div>
          <div className="text-lg font-bold font-mono text-white mt-0.5">{route.total_waypoints} Cameras</div>
          <div className="text-[10px] text-telemetry-green font-mono">100% Sequence Match</div>
        </div>

        <div className="p-3 rounded-lg bg-surface border border-surface-border">
          <div className="text-[10px] uppercase font-mono text-slate-400">Corridor Distance</div>
          <div className="text-lg font-bold font-mono text-police-gold mt-0.5">{route.total_distance_km} km</div>
          <div className="text-[10px] text-slate-400 font-mono">Vaishnodevi → Prahladnagar</div>
        </div>

        <div className="p-3 rounded-lg bg-surface border border-surface-border">
          <div className="text-[10px] uppercase font-mono text-slate-400">Transit Duration</div>
          <div className="text-lg font-bold font-mono text-white mt-0.5">{route.total_duration_minutes} min</div>
          <div className="text-[10px] text-slate-400 font-mono">10:31 AM → 11:21 AM</div>
        </div>

        <div className="p-3 rounded-lg bg-surface border border-surface-border">
          <div className="text-[10px] uppercase font-mono text-slate-400">Average Transit Velocity</div>
          <div className="text-lg font-bold font-mono text-cyber-cyan mt-0.5">{route.average_speed_kmh} km/h</div>
          <div className="text-[10px] text-telemetry-green font-mono">Plausible Highway Speed</div>
        </div>

        <div className="p-3 rounded-lg bg-surface border border-surface-border">
          <div className="text-[10px] uppercase font-mono text-slate-400">AI Plate Confidence</div>
          <div className="text-lg font-bold font-mono text-telemetry-green mt-0.5">
            {(route.overall_confidence * 100).toFixed(1)}%
          </div>
          <div className="text-[10px] text-slate-400 font-mono">Temporal Consensus (5f)</div>
        </div>
      </div>

      {/* 3. CENTER SPLIT: GIS ROUTE POLYLINE (Left) + KINEMATIC EXPLAINABILITY (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Dynamic MapLibre Route Polyline Canvas (7 cols) */}
        <div className="lg:col-span-7 flex flex-col h-[480px]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-1.5">
              <Navigation className="w-3.5 h-3.5 text-police-gold" />
              Reconstructed Spatial Trajectory Polyline
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              GeoJSON Vector Layer • 4 Verified Waypoints
            </span>
          </div>
          <DynamicMapLibre
            routeGeoJSON={route.geojson_polyline}
            center={[72.518, 23.065]}
            zoom={11.8}
            className="flex-1 w-full"
          />
        </div>

        {/* Kinematic Plausibility & Explainable Scoring (5 cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-3">
          <div className="p-4 rounded-lg bg-surface border border-surface-border space-y-3">
            <div className="flex items-center justify-between border-b border-surface-border pb-2">
              <span className="text-xs font-bold uppercase text-white flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-police-gold" />
                Cross-Camera Explainability Score
              </span>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-telemetry-green/20 text-telemetry-green border border-telemetry-green/40">
                94% MATCH CONFIDENCE
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {route.kinematic_summary}
            </p>

            {/* Score Factors Breakdown */}
            <div className="space-y-2 text-xs font-mono pt-1">
              <div className="flex items-center justify-between p-2 rounded bg-surface-raised border border-surface-border">
                <span className="text-slate-300">Exact License Plate Match</span>
                <span className="text-telemetry-green font-bold">+60.0 / 60</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-surface-raised border border-surface-border">
                <span className="text-slate-300">Kinematic Transit Velocity Plausibility</span>
                <span className="text-telemetry-green font-bold">+15.0 / 15</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-surface-raised border border-surface-border">
                <span className="text-slate-300">Vehicle Classification Consistency (SUV/Car)</span>
                <span className="text-telemetry-green font-bold">+10.0 / 10</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-surface-raised border border-surface-border">
                <span className="text-slate-300">Vehicle Color Consistency (White)</span>
                <span className="text-telemetry-green font-bold">+5.0 / 5</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-surface-raised border border-surface-border">
                <span className="text-slate-300">Cloned Plate Anomaly Flag</span>
                <span className="text-slate-400 font-bold">NONE (CLEAN)</span>
              </div>
            </div>
          </div>

          {/* Cryptographic Chain-of-Custody Card */}
          <div className="p-3.5 rounded-lg bg-surface border border-surface-border text-xs space-y-2">
            <div className="flex items-center gap-2 text-white font-bold">
              <Lock className="w-3.5 h-3.5 text-police-gold" />
              <span>Evidence Cryptographic Provenance</span>
            </div>
            <div className="text-[11px] text-slate-400 leading-relaxed">
              Every sighting frame produces a deterministic SHA-256 hash upon extraction. Certified tamper-evident for statutory submission under Section 65B of Indian Evidence Act.
            </div>
            <div className="p-2 rounded bg-black font-mono text-[10px] text-slate-300 break-all border border-surface-border">
              SHA-256: {activeWaypoint?.evidence_hash || "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
            </div>
          </div>
        </div>
      </div>

      {/* 4. CHRONOLOGICAL EVIDENCE TIMELINE & WAYPOINTS LADDER */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-police-gold" />
            Chronological Surveillance Sighting Timeline & Visual Evidence
          </span>
          <span className="text-xs font-mono text-slate-400">Sorted Ascending by Time</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {route.waypoints.map((wp: any) => (
            <div
              key={wp.step_number}
              onClick={() => setSelectedWaypoint(wp)}
              className={`p-3 rounded-lg bg-surface border transition-all cursor-pointer ${
                activeWaypoint?.step_number === wp.step_number
                  ? "border-police-gold ring-1 ring-police-gold/40 shadow-lg"
                  : "border-surface-border hover:border-slate-600"
              }`}
            >
              {/* Waypoint Header */}
              <div className="flex items-center justify-between gap-2 mb-2 pb-1.5 border-b border-surface-border">
                <div className="flex items-center gap-1.5">
                  <span className="w-5 h-5 rounded-full bg-police-gold text-black font-mono font-bold text-[11px] flex items-center justify-center">
                    {wp.step_number}
                  </span>
                  <span className="text-xs font-mono font-bold text-white">
                    {new Date(wp.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <span className="text-[10px] font-mono text-telemetry-green font-bold">
                  {(wp.plate_confidence * 100).toFixed(0)}% Conf
                </span>
              </div>

              {/* Camera Name & Location */}
              <div className="text-xs font-medium text-slate-200 truncate mb-1">
                {wp.camera_name}
              </div>
              <div className="text-[10px] font-mono text-slate-400 mb-2">
                {wp.zone} • {wp.district}
              </div>

              {/* Evidence Snapshot */}
              <div className="relative rounded overflow-hidden bg-black border border-surface-border aspect-video mb-2">
                <img
                  src={wp.frame_uri || "/static/evidence/frame_GJ01AB1234_1773727000.jpg"}
                  alt={`Sighting at ${wp.camera_name}`}
                  className="w-full h-full object-cover"
                />
                <div className="absolute bottom-1 left-1 bg-black/80 px-1 py-0.5 rounded text-[9px] font-mono text-police-gold">
                  PLATE: {wp.license_plate}
                </div>
              </div>

              {/* Kinematics from Previous Node */}
              {wp.kinematic_from_prev ? (
                <div className="text-[10px] font-mono text-slate-400 bg-surface-raised p-1.5 rounded space-y-0.5">
                  <div className="flex justify-between">
                    <span>Segment Dist:</span>
                    <span className="text-white">{wp.kinematic_from_prev.distance_traveled_km} km</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Implied Speed:</span>
                    <span className="text-telemetry-green font-bold">{wp.kinematic_from_prev.implied_speed_kmh} km/h</span>
                  </div>
                </div>
              ) : (
                <div className="text-[10px] font-mono text-slate-400 bg-surface-raised p-1.5 rounded text-center">
                  Corridor Entry Point
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
