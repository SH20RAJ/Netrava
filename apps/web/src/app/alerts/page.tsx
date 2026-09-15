import { Metadata } from "next";
import { AlertsManagementView } from "@/components/views/AlertsManagementView";

export const metadata: Metadata = {
  title: "Alert Triage & Watchlist Hits | Netrava Video Intelligence",
  description:
    "Real-time sub-second threat alerts, watchlist matching, and AI detection events across statewide camera networks.",
};

export default function AlertsPage() {
  return <AlertsManagementView />;
}
