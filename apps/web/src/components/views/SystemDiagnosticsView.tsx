"use client";

import React, { useState, useEffect } from "react";
import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import { Sliders, Cpu, HardDrive, Network, CheckCircle2, Shield, Layers, RefreshCw } from "lucide-react";

export function SystemDiagnosticsView() {
  const { data: health } = useSWR<any>("/api/v1/system/health", fetcher, {
    refreshInterval: 10000,
    dedupingInterval: 5000,
  });

  // Interactive Calculator State
  const [cameraCount, setCameraCount] = useState(80000);
  const [bitrateMbps, setBitrateMbps] = useState(2.5);
  const [analyticsFps, setAnalyticsFps] = useState(5.0);
  const [hotDays, setHotDays] = useState(7);
  const [regionalHubs, setRegionalHubs] = useState(34);
  const [calcResult, setCalcResult] = useState<any>(null);

  // SWR Keyed Calculation
  const calcPayload = React.useMemo(
    () => ({
      camera_count: cameraCount,
      average_bitrate_mbps: bitrateMbps,
      analytics_fps: analyticsFps,
      hot_storage_days: hotDays,
      regional_hubs_count: regionalHubs,
      gpu_inference_rate_fps: 350.0,
    }),
    [cameraCount, bitrateMbps, analyticsFps, hotDays, regionalHubs]
  );

  const calcFetcher = async (url: string, payload: typeof calcPayload) => {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Calculation failed");
    return res.json();
  };

  const { data: calculation } = useSWR(
    ["/api/v1/system/scalability-calculator", calcPayload],
    ([url, payload]) => calcFetcher(url, payload),
    { dedupingInterval: 1000, revalidateOnFocus: false }
  );

  const activeResult = calculation || calcResult;

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* 1. Header */}
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Sliders className="w-5 h-5 text-police-gold" />
          <span>Platform Health & 80,000-Camera Scalability Calculator</span>
        </h1>
        <p className="text-xs text-slate-400">
          Statewide infrastructure capacity model, tiered storage equations, and GPU inference sizing for Gujarat Police 2026.
        </p>
      </div>

      {/* 2. Live Component Health Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {health?.components?.map((c: any) => (
          <div key={c.name} className="p-3.5 rounded-lg bg-surface border border-surface-border space-y-1.5 shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white truncate">{c.name}</span>
              <span className="text-[10px] font-mono text-telemetry-green px-1.5 py-0.2 rounded bg-telemetry-green/10 border border-telemetry-green/30">
                {c.status}
              </span>
            </div>
            <div className="text-[11px] font-mono text-slate-400">
              Latency: <span className="text-white font-bold">{c.latency_ms} ms</span>
            </div>
          </div>
        ))}
      </div>

      {/* 3. INTERACTIVE 80,000 CAMERA CAPACITY CALCULATOR */}
      <div className="p-5 rounded-xl bg-surface border border-surface-border shadow-2xl space-y-5">
        <div className="border-b border-surface-border pb-3">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-police-gold" />
            <span>Interactive Capacity Sizing Engine</span>
          </h2>
          <p className="text-xs text-slate-400">
            Adjust deployment parameters below to compute network WAN bandwidth, GPU inference load, and tiered storage across Gujarat's 34 districts.
          </p>
        </div>

        {/* Sliders Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs font-mono">
          <div className="space-y-1 p-3 rounded bg-surface-raised border border-surface-border">
            <div className="flex justify-between text-slate-300">
              <span>CAMERA COUNT:</span>
              <span className="text-police-gold font-bold">{cameraCount.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min="1000"
              max="150000"
              step="1000"
              value={cameraCount}
              onChange={(e) => setCameraCount(Number(e.target.value))}
              className="w-full accent-police-gold cursor-pointer"
            />
          </div>

          <div className="space-y-1 p-3 rounded bg-surface-raised border border-surface-border">
            <div className="flex justify-between text-slate-300">
              <span>AVERAGE BITRATE:</span>
              <span className="text-cyber-cyan font-bold">{bitrateMbps} Mbps</span>
            </div>
            <input
              type="range"
              min="1.0"
              max="10.0"
              step="0.5"
              value={bitrateMbps}
              onChange={(e) => setBitrateMbps(Number(e.target.value))}
              className="w-full accent-cyber-cyan cursor-pointer"
            />
          </div>

          <div className="space-y-1 p-3 rounded bg-surface-raised border border-surface-border">
            <div className="flex justify-between text-slate-300">
              <span>ANALYTICS FPS:</span>
              <span className="text-telemetry-green font-bold">{analyticsFps} FPS</span>
            </div>
            <input
              type="range"
              min="1"
              max="15"
              step="1"
              value={analyticsFps}
              onChange={(e) => setAnalyticsFps(Number(e.target.value))}
              className="w-full accent-telemetry-green cursor-pointer"
            />
          </div>

          <div className="space-y-1 p-3 rounded bg-surface-raised border border-surface-border">
            <div className="flex justify-between text-slate-300">
              <span>HOT RETENTION (DAYS):</span>
              <span className="text-white font-bold">{hotDays} Days</span>
            </div>
            <input
              type="range"
              min="3"
              max="30"
              step="1"
              value={hotDays}
              onChange={(e) => setHotDays(Number(e.target.value))}
              className="w-full cursor-pointer"
            />
          </div>

          <div className="space-y-1 p-3 rounded bg-surface-raised border border-surface-border">
            <div className="flex justify-between text-slate-300">
              <span>REGIONAL DISTRICT HUBS:</span>
              <span className="text-white font-bold">{regionalHubs} Districts</span>
            </div>
            <input
              type="range"
              min="1"
              max="50"
              step="1"
              value={regionalHubs}
              onChange={(e) => setRegionalHubs(Number(e.target.value))}
              className="w-full cursor-pointer"
            />
          </div>
        </div>

        {/* Calculated Results Ribbon */}
        {activeResult && (
          <div className="space-y-4 pt-2">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="p-3 rounded-lg bg-surface-raised border border-surface-border">
                <div className="text-[10px] font-mono uppercase text-slate-400">Naive Central WAN Load</div>
                <div className="text-lg font-bold font-mono text-alert-red mt-0.5">
                  {activeResult.centralized_raw_video_bandwidth_gbps} Gbps
                </div>
                <div className="text-[10px] text-slate-400">If all raw feeds streamed centrally</div>
              </div>

              <div className="p-3 rounded-lg bg-surface-raised border border-police-gold/40">
                <div className="text-[10px] font-mono uppercase text-police-gold">Netrava Edge-to-Cloud WAN</div>
                <div className="text-lg font-bold font-mono text-white mt-0.5">
                  {activeResult.netrava_edge_to_cloud_bandwidth_mbps} Mbps
                </div>
                <div className="text-[10px] text-telemetry-green font-bold">
                  {activeResult.bandwidth_reduction_pct}% Bandwidth Saved!
                </div>
              </div>

              <div className="p-3 rounded-lg bg-surface-raised border border-surface-border">
                <div className="text-[10px] font-mono uppercase text-slate-400">Statewide Inference Load</div>
                <div className="text-lg font-bold font-mono text-cyber-cyan mt-0.5">
                  {activeResult.total_statewide_inferences_per_sec.toLocaleString()} inf/s
                </div>
                <div className="text-[10px] text-slate-400 font-mono">
                  {activeResult.cameras_per_regional_hub} cams / district
                </div>
              </div>

              <div className="p-3 rounded-lg bg-surface-raised border border-surface-border">
                <div className="text-[10px] font-mono uppercase text-slate-400">GPUs Required Per District</div>
                <div className="text-lg font-bold font-mono text-telemetry-green mt-0.5">
                  {activeResult.gpus_required_per_hub}x GPUs
                </div>
                <div className="text-[10px] text-slate-400 font-mono">
                  NVIDIA L4 INT8 (~4 Servers)
                </div>
              </div>
            </div>

            {/* Recommendations Narrative */}
            <div className="p-4 rounded-lg bg-black/40 border border-surface-border text-xs space-y-2">
              <div className="font-bold text-white">Hardware Sizing Recommendation:</div>
              <p className="text-slate-300 leading-relaxed">{activeResult.gpu_hardware_recommendation}</p>
              <p className="text-slate-300 leading-relaxed">{activeResult.storage_architecture_recommendation}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
