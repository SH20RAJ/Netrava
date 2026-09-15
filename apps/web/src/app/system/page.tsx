import { Metadata } from "next";
import { SystemDiagnosticsView } from "@/components/views/SystemDiagnosticsView";

export const metadata: Metadata = {
  title: "Platform Diagnostics & 80,000-Camera Scalability Calculator | Netrava",
  description:
    "System diagnostics, cluster telemetry, and dynamic 80,000-camera edge-to-cloud capacity planning calculator.",
};

export default function SystemPage() {
  return <SystemDiagnosticsView />;
}
