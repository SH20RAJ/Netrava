import { Metadata } from "next";
import { VehicleInvestigationView } from "@/components/views/VehicleInvestigationView";

interface PageProps {
  params: Promise<{ plate: string }> | { plate: string };
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const resolvedParams = await Promise.resolve(params);
  const plate = resolvedParams.plate?.toUpperCase() || "VEHICLE";
  return {
    title: `Trajectory Reconstructor: ${plate} | Netrava`,
    description: `Cross-camera kinematic trajectory reconstruction and Section 65B certified evidence history for vehicle ${plate}.`,
  };
}

export default async function VehiclePlatePage({ params }: PageProps) {
  const resolvedParams = await Promise.resolve(params);
  return <VehicleInvestigationView plate={resolvedParams.plate} />;
}
