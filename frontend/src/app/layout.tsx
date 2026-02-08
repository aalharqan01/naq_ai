import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dhakira | Qatar Heritage AI Assistant",
  description:
    "AI-powered heritage preservation and exploration platform for the National Archives of Qatar",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased overflow-x-hidden">
        <div className="islamic-pattern" aria-hidden="true" />
        <div className="glow-orb glow-orb-maroon" aria-hidden="true" />
        <div className="glow-orb glow-orb-gold" aria-hidden="true" />
        <div className="glow-orb glow-orb-blue" aria-hidden="true" />
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
