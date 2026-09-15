import { Metadata } from "next";
import { InvestigationsView } from "@/components/views/InvestigationsView";

export const metadata: Metadata = {
  title: "Investigations & Section 65B Dossiers | Netrava",
  description:
    "Formal cross-camera case files with cryptographic evidence provenance and Indian Evidence Act Section 65B compliance.",
};

export default function InvestigationsPage() {
  return <InvestigationsView />;
}
