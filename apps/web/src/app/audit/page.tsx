import { Metadata } from "next";
import { AuditLogsView } from "@/components/views/AuditLogsView";

export const metadata: Metadata = {
  title: "Security & Chain-of-Custody Audit Trail | Netrava",
  description:
    "Immutable forensic audit log recording all operator queries, vehicle lookups, and surveillance video access.",
};

export default function AuditPage() {
  return <AuditLogsView />;
}
