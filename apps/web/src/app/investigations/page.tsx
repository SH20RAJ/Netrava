"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { FileText, Shield, ArrowRight, Clock, CheckCircle2 } from "lucide-react";

export default function InvestigationsPage() {
  const router = useRouter();
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/investigations")
      .then((r) => r.json())
      .then((data) => setCases(data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <FileText className="w-5 h-5 text-police-gold" />
          <span>Investigation Dossiers & Chain of Custody</span>
        </h1>
        <p className="text-xs text-slate-400">
          Formal cross-camera case files with cryptographic evidence provenance and Section 65B compliance.
        </p>
      </div>

      <div className="space-y-3">
        {cases.map((c) => (
          <div
            key={c.id}
            className="p-4 rounded-xl bg-surface border border-surface-border hover:border-police-gold/40 transition-all shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-police-gold/20 text-police-gold border border-police-gold/30">
                  {c.case_number}
                </span>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-surface-raised text-slate-300">
                  {c.status}
                </span>
              </div>
              <div className="text-base font-bold text-white">{c.title}</div>
              <div className="text-xs text-slate-400">{c.summary}</div>
              <div className="text-[11px] font-mono text-slate-400 pt-1">
                Lead: {c.lead_investigator} • Department: {c.department} • Target Plate: {c.target_plate}
              </div>
            </div>

            <button
              onClick={() => router.push(`/vehicles/${c.target_plate}`)}
              className="px-4 py-2 rounded bg-surface-raised border border-surface-border text-xs font-bold text-police-gold hover:bg-slate-700 flex items-center gap-1.5 whitespace-nowrap"
            >
              <span>View Route & Evidence</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
