"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Shield,
  Activity,
  Video,
  Search,
  AlertTriangle,
  FileText,
  Sliders,
  Database,
  Lock,
  Layers,
  CheckCircle2,
  Radio,
  ExternalLink
} from "lucide-react";

export function Navigation() {
  const pathname = usePathname();
  const router = useRouter();
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const navItems = [
    { label: "Command Center", href: "/", icon: Layers },
    { label: "CCTV Registry", href: "/cameras", icon: Database },
    { label: "Tactical Wall", href: "/live", icon: Video },
    { label: "Vehicle Intel", href: "/vehicles", icon: Search },
    { label: "Alerts", href: "/alerts", icon: AlertTriangle, badge: "1 CRITICAL" },
    { label: "Watchlists", href: "/watchlists", icon: Shield },
    { label: "Investigations", href: "/investigations", icon: FileText },
    { label: "80k Scalability", href: "/system", icon: Sliders },
    { label: "Audit Logs", href: "/audit", icon: Lock },
  ];

  // Cmd+K hotkey
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    const query = searchQuery.trim().toUpperCase();
    setSearchOpen(false);
    setSearchQuery("");
    // If format matches license plate or plate search
    router.push(`/vehicles/${query}`);
  };

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-surface-border bg-surface/95 backdrop-blur px-4 py-2.5">
        <div className="flex items-center justify-between gap-4">
          {/* Brand & Deploy Location */}
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 rounded bg-police-gold/10 border border-police-gold/40 flex items-center justify-center text-police-gold shadow-lg shadow-police-gold/10 group-hover:bg-police-gold/20 transition-all">
                <Shield className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold tracking-wider text-sm text-white">NETRAVA</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-police-gold/20 text-police-gold border border-police-gold/30">
                    GJ-POLICE 2026
                  </span>
                </div>
                <div className="text-[10px] text-slate-400">Open Video Intelligence Fabric</div>
              </div>
            </Link>
          </div>

          {/* Center Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors relative ${
                    isActive
                      ? "bg-surface-raised text-white border border-surface-border"
                      : "text-slate-400 hover:text-slate-200 hover:bg-surface-raised/50"
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? "text-police-gold" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded-full bg-alert-red/20 text-alert-red border border-alert-red/40 animate-pulse">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Right Action Bar & Operator Info */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSearchOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-surface-raised text-xs text-slate-400 border border-surface-border hover:border-slate-600 transition-colors"
            >
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <span className="hidden sm:inline">Search Plate (e.g. GJ01AB1234)...</span>
              <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-mono bg-surface rounded border border-surface-border text-slate-400">
                ⌘K
              </kbd>
            </button>

            {/* Operator Badge */}
            <div className="hidden xl:flex items-center gap-2 pl-3 border-l border-surface-border text-xs">
              <div className="w-2 h-2 rounded-full bg-telemetry-green animate-ping" />
              <div className="text-right">
                <div className="text-slate-200 font-medium text-[11px]">DySP Vikram Patel</div>
                <div className="text-slate-400 text-[9px] font-mono">CID Crime • Ahmedabad</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Global Command Palette Modal */}
      {searchOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-start justify-center pt-24 p-4">
          <div className="bg-surface border border-surface-border rounded-xl w-full max-w-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <form onSubmit={handleSearchSubmit} className="flex items-center gap-3 px-4 py-3 border-b border-surface-border">
              <Search className="w-5 h-5 text-police-gold" />
              <input
                autoFocus
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search Plate (e.g. GJ01AB1234), Camera ID, or Case No..."
                className="w-full bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setSearchOpen(false)}
                className="text-xs px-2 py-1 rounded bg-surface-raised border border-surface-border text-slate-400 hover:text-white"
              >
                ESC
              </button>
            </form>

            <div className="p-3 bg-surface-raised/40">
              <div className="text-[10px] font-mono uppercase text-slate-400 mb-2 px-2">Quick Hackathon Evaluation Targets</div>
              <div className="space-y-1">
                <button
                  type="button"
                  onClick={() => {
                    setSearchOpen(false);
                    router.push("/vehicles/GJ01AB1234");
                  }}
                  className="w-full text-left px-3 py-2 rounded-lg bg-surface border border-surface-border hover:border-police-gold/50 flex items-center justify-between group transition-all"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded bg-alert-red/10 border border-alert-red/30 flex items-center justify-center text-alert-red">
                      <AlertTriangle className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-mono font-bold text-white group-hover:text-police-gold">
                        GJ01AB1234
                      </div>
                      <div className="text-[11px] text-slate-400">Target Stolen Vehicle • SG Highway Corridor (4 Sightings)</div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-alert-red/20 text-alert-red border border-alert-red/30 font-bold">
                    CRITICAL HIT
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setSearchOpen(false);
                    router.push("/cameras");
                  }}
                  className="w-full text-left px-3 py-2 rounded-lg bg-surface border border-surface-border hover:border-slate-500 flex items-center justify-between group transition-all"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded bg-surface-raised border border-surface-border flex items-center justify-center text-slate-400">
                      <Database className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-medium text-white group-hover:text-slate-200">
                        View All 52 Seeded Cameras
                      </div>
                      <div className="text-[11px] text-slate-400">Ahmedabad, Surat, Gandhinagar, Vadodara, Rajkot</div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">52 NODES</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
