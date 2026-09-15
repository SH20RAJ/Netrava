import type { Metadata } from "next";
import { CamerasRegistryView } from "@/components/views/CamerasRegistryView";

export const metadata: Metadata = {
  title: "Central CCTV Registry (Model 1) | Netrava Fabric",
  description: "Statewide registry of 80,000 heterogeneous camera endpoints across 26 government departments and 34 Gujarat districts with real-time health telemetry.",
};

export default function CamerasPage() {
  return <CamerasRegistryView />;
}
