"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, ArrowRight } from "lucide-react";

export function VehicleSearchView() {
  const router = useRouter();
  const [searchPlate, setSearchPlate] = useState("");

  const recentSearches = [
    { plate: "GJ01AB1234", description: "Target Stolen Vehicle (FIR 142/2026)", threat: "CRITICAL", hits: 4, corridor: "SG Highway Corridor" },
    { plate: "GJ05CD5678", description: "Flagged Inter-District Surveillance", threat: "HIGH", hits: 2, corridor: "NH-48 Surat-Vadodara" },
    { plate: "GJ27EF9012", description: "Priority Smuggling Watchlist", threat: "MEDIUM", hits: 1, corridor: "Gandhinagar Koba" }
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchPlate.trim()) return;
    router.push(`/vehicles/${searchPlate.trim().toUpperCase()}`);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Search className="w-5 h-5 text-police-gold" />
          <span>Cross-Camera Vehicle Intelligence & Route Search</span>
        </h1>
        <p className="text-xs text-slate-400">
          Search any license plate to reconstruct its statewide movement history, kinematic velocity profile, and surveillance evidence.
        </p>
      </div>

      {/* Search Input Box */}
      <form onSubmit={handleSearch} className="p-4 rounded-xl bg-surface border border-surface-border shadow-xl space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={searchPlate}
            onChange={(e) => setSearchPlate(e.target.value)}
            placeholder="Enter Plate Number (e.g. GJ01AB1234, GJ05CD5678)..."
            className="flex-1 px-4 py-3 rounded-lg bg-surface-raised border border-surface-border text-white text-base font-mono font-bold tracking-wider placeholder-slate-500 focus:outline-none focus:border-police-gold"
          />
          <button
            type="submit"
            className="px-6 py-3 rounded-lg bg-police-gold text-black font-bold text-sm hover:bg-yellow-400 transition-all flex items-center gap-2 shadow-lg shadow-police-gold/20"
          >
            <span>Reconstruct Route</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </form>

      {/* Quick Access Reference Targets */}
      <div className="space-y-3">
        <div className="text-xs font-mono uppercase text-slate-400">
          Official Gujarat Innovation Challenge Evaluation Targets
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {recentSearches.map((item) => (
            <div
              key={item.plate}
              onClick={() => router.push(`/vehicles/${item.plate}`)}
              className="p-4 rounded-lg bg-surface border border-surface-border hover:border-police-gold/50 cursor-pointer transition-all group flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-black text-base text-white group-hover:text-police-gold">
                    {item.plate}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-alert-red/20 text-alert-red border border-alert-red/30 font-bold">
                    {item.threat}
                  </span>
                </div>
                <div className="text-xs text-slate-300">{item.description}</div>
                <div className="text-[11px] font-mono text-slate-400">{item.corridor}</div>
              </div>
              <div className="pt-3 mt-3 border-t border-surface-border flex items-center justify-between text-xs text-police-gold font-bold">
                <span>{item.hits} Recorded Sightings</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
