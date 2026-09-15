"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, Shield, CheckCircle2, ArrowRight, Clock, MapPin } from "lucide-react";

export default function AlertsManagementPage() {
  const router = useRouter();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  async function fetchAlerts() {
    try {
      const res = await fetch("/api/v1/alerts?limit=50");
      if (res.ok) setAlerts(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  const handleAcknowledge = async (alertId: string) => {
    try {
      const res = await fetch(`/api/v1/alerts/${alertId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "ACKNOWLEDGED" })
      });
      if (res.ok) fetchAlerts();
    } catch (e) {}
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-4">
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-alert-red" />
          <span>Real-Time Surveillance Alert Triage</span>
        </h1>
        <p className="text-xs text-slate-400">
          Sub-second automated threat and watchlist detection events dispatched from edge and regional AI inference workers.
        </p>
      </div>

      <div className="space-y-3">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className="p-4 rounded-xl bg-surface border border-surface-border hover:border-alert-red/40 transition-all shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
          >
            <div className="space-y-1.5 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-alert-red text-white uppercase">
                  {alert.severity}
                </span>
                <span className="font-mono font-bold text-base text-white">
                  {alert.matched_entity}
                </span>
                <span className="text-[11px] font-mono text-slate-400">
                  Confidence: {(alert.match_confidence * 100).toFixed(1)}%
                </span>
              </div>

              <div className="text-sm font-medium text-slate-200">
                {alert.title}
              </div>

              <div className="text-xs text-slate-400 leading-relaxed">
                {alert.description}
              </div>

              <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 pt-1">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-police-gold" />
                  {alert.camera_name || "Surveillance Point"} ({alert.district || "Gujarat"})
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  {new Date(alert.created_at).toLocaleString()}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 w-full md:w-auto">
              <button
                onClick={() => router.push(`/vehicles/${alert.matched_entity}`)}
                className="flex-1 md:flex-initial px-4 py-2 rounded bg-police-gold text-black font-bold text-xs hover:bg-yellow-400 transition-all flex items-center justify-center gap-1.5 shadow"
              >
                <span>Reconstruct Route</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>

              {alert.status === "NEW" ? (
                <button
                  onClick={() => handleAcknowledge(alert.id)}
                  className="px-3 py-2 rounded bg-surface-raised border border-surface-border text-xs text-slate-300 hover:text-white"
                >
                  Acknowledge
                </button>
              ) : (
                <span className="text-[11px] font-mono text-telemetry-green px-2 py-1 bg-telemetry-green/10 rounded border border-telemetry-green/30">
                  ACKNOWLEDGED
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
