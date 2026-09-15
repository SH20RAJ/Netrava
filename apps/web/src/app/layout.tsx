import "./globals.css";
import type { Metadata } from "next";
import { Navigation } from "@/components/Navigation";

export const metadata: Metadata = {
  title: "Netrava — Open Government Video Intelligence Fabric",
  description: "Vendor-neutral, AI-powered, edge-to-cloud video intelligence and cross-camera investigation platform for Gujarat Police Innovation Challenge 2026.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-slate-100 antialiased selection:bg-police-gold/30 selection:text-police-gold">
        <Navigation />
        <main className="flex-1">
          {children}
        </main>
      </body>
    </html>
  );
}
