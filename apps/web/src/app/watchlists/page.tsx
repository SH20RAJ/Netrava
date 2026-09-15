import { Metadata } from "next";
import { WatchlistsView } from "@/components/views/WatchlistsView";

export const metadata: Metadata = {
  title: "Watchlists & Hotlist Rules | Netrava Video Intelligence",
  description:
    "Statewide hotlists and operational target registries synchronized with CCTNS, VAHAN, and police crime databases.",
};

export default function WatchlistsPage() {
  return <WatchlistsView />;
}
