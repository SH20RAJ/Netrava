import type { Metadata } from "next";
import { CommandDashboardView } from "@/components/views/CommandDashboardView";

export const metadata: Metadata = {
  title: "Tactical Command Center | Netrava Video Intelligence",
  description: "Real-time statewide CCTV command and control dashboard with MapLibre GIS, active threat triage, and video relay for Gujarat Police 2026.",
};

export default function CommandDashboardPage() {
  return <CommandDashboardView />;
}
