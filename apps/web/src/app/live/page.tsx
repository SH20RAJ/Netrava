import { Metadata } from "next";
import { TacticalWallView } from "@/components/views/TacticalWallView";

export const metadata: Metadata = {
  title: "Tactical Video Wall | Netrava Video Intelligence",
  description:
    "Real-time video relay matrix with low-latency WebRTC/HLS edge streaming and automated AI detection overlays.",
};

export default function TacticalLivePage() {
  return <TacticalWallView />;
}
