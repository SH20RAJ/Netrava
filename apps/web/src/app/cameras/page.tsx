"use client";

import React, { useState, useEffect } from "react";
import {
  Database,
  Search,
  Filter,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Upload,
  RefreshCw,
  Video,
  Radio
} from "lucide-react";

export default function CamerasRegistryPage() {
  const [cameras, setCameras] = useState<any[]>([]);
  const [districtFilter, setDistrictFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedHealth, setSelectedHealth] = useState<any>(null);

  useEffect(() => {
    fetchCameras();
  }, [districtFilter, statusFilter]);

  async function fetchCameras() {
    setLoading(true);
    try {
      let url = "/api/v1/cameras?limit=100";
      if (districtFilter !== "ALL") url += `&district=${districtFilter}`;
      if (statusFilter !== "ALL") url += `&status=${statusFilter}`;
      const res = await fetch(url);
      if (res.ok) setCameras(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  const handleInspectHealth = async (camId: string) => {
    try {
      const res = await fetch(`/api/v1/cameras/${camId}/health`);
      if (res.ok) setSelectedHealth(await res.json());
    } catch (e) {}
  };

  const filtered = cameras.filter((cam) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (
      cam.name.toLowerCase().includes(s) ||
      cam.external_id.toLowerCase().includes(s) ||
      cam.district.toLowerCase().includes(s) ||
      cam.manufacturer.toLowerCase().includes(s)
    );
  });

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-police-gold" />
            <span>Central CCTV Camera Registry (Model 1 Foundation)</span>
          </h1>
          <p className="text-xs text-slate-400">
            Unified inventory of heterogeneous cameras across 26 government departments and 34 Gujarat districts.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchCameras}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-raised border border-surface-border text-xs text-slate-300 hover:text-white"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Telemetry</span>
          </button>
        </div>
      </div>

      {/* Filter Ribbon */}
      <div className="p-3 rounded-lg bg-surface border border-surface-border flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Camera Name, Node ID, Vendor, or District..."
            className="w-full bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-3">
          {/* District Filter */}
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <span>District:</span>
            <select
              value={districtFilter}
              onChange={(e) => setDistrictFilter(e.target.value)}
              className="bg-surface-raised border border-surface-border text-xs text-white rounded px-2 py-1 focus:outline-none"
            >
              <option value="ALL">All Districts (52)</option>
              <option value="Ahmedabad">Ahmedabad</option>
              <option value="Gandhinagar">Gandhinagar</option>
              <option value="Surat">Surat</option>
              <option value="Vadodara">Vadodara</option>
              <option value="Rajkot">Rajkot</option>
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <span>Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-surface-raised border border-surface-border text-xs text-white rounded px-2 py-1 focus:outline-none"
            >
              <option value="ALL">All States</option>
              <option value="ONLINE">Online (100%)</option>
              <option value="OFFLINE">Offline</option>
              <option value="DEGRADED">Degraded</option>
            </select>
          </div>
        </div>
      </div>

      {/* Cameras DataTable */}
      <div className="rounded-lg border border-surface-border bg-surface overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-raised/70 border-b border-surface-border text-[11px] font-mono uppercase text-slate-400">
              <tr>
                <th className="px-4 py-2.5">Camera / Identifier</th>
                <th className="px-4 py-2.5">District / Corridor</th>
                <th className="px-4 py-2.5">Coordinates</th>
                <th className="px-4 py-2.5">Manufacturer</th>
                <th className="px-4 py-2.5">Protocol</th>
                <th className="px-4 py-2.5">Status</th>
                <th className="px-4 py-2.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border/60">
              {filtered.map((cam) => (
                <tr key={cam.id} className="hover:bg-surface-raised/40 transition-colors">
                  <td className="px-4 py-2.5 font-medium">
                    <div className="text-white font-bold">{cam.name}</div>
                    <div className="text-[10px] font-mono text-slate-400">{cam.external_id}</div>
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="text-slate-200">{cam.district}</div>
                    <div className="text-[10px] text-slate-400">{cam.zone}</div>
                  </td>
                  <td className="px-4 py-2.5 font-mono text-[11px] text-slate-300">
                    {cam.latitude.toFixed(4)}, {cam.longitude.toFixed(4)}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className="px-1.5 py-0.5 rounded bg-surface-raised border border-surface-border text-[10px] font-mono text-slate-300">
                      {cam.manufacturer}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 font-mono text-[10px] text-slate-400">
                    {cam.protocol}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-telemetry-green/10 text-telemetry-green border border-telemetry-green/30">
                      <span className="w-1.5 h-1.5 rounded-full bg-telemetry-green" />
                      {cam.status}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    <button
                      onClick={() => handleInspectHealth(cam.id)}
                      className="px-2 py-1 rounded bg-surface-raised border border-surface-border text-police-gold hover:bg-slate-700 font-mono text-[10px]"
                    >
                      Ping Telemetry
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Health Telemetry Modal */}
      {selectedHealth && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
          <div className="bg-surface border border-surface-border rounded-xl max-w-md w-full p-4 space-y-3 shadow-2xl">
            <div className="flex items-center justify-between border-b border-surface-border pb-2">
              <span className="text-xs font-bold text-white uppercase font-mono">Stream Diagnostic: {selectedHealth.external_id}</span>
              <button onClick={() => setSelectedHealth(null)} className="text-xs text-slate-400 hover:text-white">
                ✕
              </button>
            </div>
            <div className="text-sm font-bold text-white">{selectedHealth.name}</div>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="p-2 rounded bg-surface-raised">
                <span className="text-slate-400 block text-[10px]">PING LATENCY</span>
                <span className="text-telemetry-green font-bold">{selectedHealth.last_ping_latency_ms} ms</span>
              </div>
              <div className="p-2 rounded bg-surface-raised">
                <span className="text-slate-400 block text-[10px]">MEASURED FPS</span>
                <span className="text-white font-bold">{selectedHealth.fps_measured} FPS</span>
              </div>
              <div className="p-2 rounded bg-surface-raised">
                <span className="text-slate-400 block text-[10px]">BITRATE</span>
                <span className="text-cyber-cyan font-bold">{selectedHealth.bitrate_kbps} kbps</span>
              </div>
              <div className="p-2 rounded bg-surface-raised">
                <span className="text-slate-400 block text-[10px]">PACKET LOSS</span>
                <span className="text-telemetry-green font-bold">{selectedHealth.packet_loss_pct}%</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
