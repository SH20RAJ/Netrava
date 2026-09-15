"use client";

import React from "react";
import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import { Shield } from "lucide-react";

export function WatchlistsView() {
  const { data: watchlists = [], isLoading } = useSWR<any[]>(
    "/api/v1/watchlists",
    fetcher,
    { dedupingInterval: 10000 }
  );

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Shield className="w-5 h-5 text-police-gold" />
            <span>Statewide Hotlists & Operational Watchlists</span>
          </h1>
          <p className="text-xs text-slate-400">
            Automated entity rules synchronized with CCTNS, VAHAN, and police crime databases.
          </p>
        </div>
      </div>

      {isLoading && watchlists.length === 0 ? (
        <div className="flex flex-col items-center justify-center min-h-[300px] gap-2">
          <div className="w-6 h-6 border-2 border-police-gold border-t-transparent rounded-full animate-spin" />
          <span className="text-xs font-mono text-slate-400">Loading Active Watchlists...</span>
        </div>
      ) : (
        <div className="space-y-4">
          {watchlists.map((wl) => (
            <div key={wl.id} className="p-4 rounded-xl bg-surface border border-surface-border shadow-xl space-y-3">
              <div className="flex items-center justify-between border-b border-surface-border pb-3">
                <div>
                  <h2 className="text-sm font-bold text-white">{wl.name}</h2>
                  <div className="text-xs text-slate-400">{wl.description}</div>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-police-gold/10 text-police-gold border border-police-gold/30 font-bold">
                  {wl.category}
                </span>
              </div>

              <div className="space-y-2">
                <div className="text-[11px] font-mono uppercase text-slate-400">Active Watchlist Entries</div>
                <div className="divide-y divide-surface-border/60 bg-surface-raised/40 rounded-lg border border-surface-border overflow-hidden">
                  {wl.entries?.map((entry: any) => (
                    <div key={entry.id} className="p-3 flex items-center justify-between text-xs">
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-white text-sm">{entry.identifier}</span>
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-alert-red/20 text-alert-red border border-alert-red/30 font-bold">
                            {entry.threat_level}
                          </span>
                          <span className="text-slate-400">{entry.secondary_identifier}</span>
                        </div>
                        <div className="text-[11px] text-slate-400">{entry.notes}</div>
                      </div>
                      <div className="text-right text-[11px] font-mono text-slate-400">
                        <div>{entry.case_reference}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
