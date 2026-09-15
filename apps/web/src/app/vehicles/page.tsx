import { Metadata } from "next";
import { VehicleSearchView } from "@/components/views/VehicleSearchView";

export const metadata: Metadata = {
  title: "Vehicle Intelligence & Route Reconstructor | Netrava",
  description:
    "Cross-camera vehicle trajectory reconstruction, velocity kinematics, and Section 65B certified evidence history.",
};

export default function VehiclesPage() {
  return <VehicleSearchView />;
}
