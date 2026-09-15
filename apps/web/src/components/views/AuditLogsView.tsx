"use client";

import React from "react";
import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import { Lock } from "lucide-react";

export function AuditLogsView() {
  const { data: logs = [], isLoading } = useSWR<any[]>(
    "/api/v1/audit/logs?limit=50",
    fetcher,
    { dedupingInterval: 5000, refreshInterval: 10000 }
  );

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Lock className="w-5 h-5 text-police-gold" />
          <span>Immutable Security Audit Logs</span>
        </h1>
        <p className="text-xs text-slate-400">
          Cryptographic audit trail tracking all operator queries, vehicle searches, live stream views, and evidence access events.
        </p>
      </div>

      {isLoading && logs.length === 0 ? (
        <div className="flex flex-col items-center justify-center min-h-[300px] gap-2">
          <div className="w-6 h-6 border-2 border-police-gold border-t-transparent rounded-full animate-spin" />
          <span className="text-xs font-mono text-slate-400">Loading Audit Trail...</span>
        </div>
      ) : (
        <div className="rounded-xl border border-surface-border bg-surface overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-raised/80 border-b border-surface-border text-[11px] font-mono uppercase text-slate-400">
              <tr>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">Officer / Actor</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Action</th>
                <th className="px-4 py-3">Target Entity</th>
                <th className="px-4 py-3">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border/60">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-surface-raised/40 transition-colors font-mono">
                  <td className="px-4 py-2.5 text-slate-400 text-[11px]">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-4 py-2.5 text-white font-bold">
                    {log.user_name}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-surface-raised border border-surface-border text-slate-300">
                      {log.user_role}
                    </span>
                  </td>
                  <td className="px-4 py-2.5">
                    <span className="text-[10px] px-2 py-0.5 rounded bg-police-gold/10 text-police-gold border border-police-gold/30 font-bold">
                      {log.action}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-cyber-cyan font-bold">
                    {log.entity_id}
                  </td>
                  <td className="px-4 py-2.5 text-slate-400 text-[11px]">
                    {log.ip_address}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
