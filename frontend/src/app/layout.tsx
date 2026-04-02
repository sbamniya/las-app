import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FuzeBox AEOS Assess — AI Readiness & Agentic ROI Platform",
  description: "Deep AI readiness assessment using CAITO, GSTI, RAI, RAIA, and RAW frameworks",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
