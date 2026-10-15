import type { Metadata } from "next";
import { Cormorant_Garamond, Manrope } from "next/font/google";
import "./globals.css";
import { BirthProfileProvider } from "@/context/BirthProfileContext";
import { AppShell } from "@/components/layout/AppShell";

const display = Cormorant_Garamond({ subsets: ["latin"], weight: ["500", "600", "700"], variable: "--font-display" });
const body = Manrope({ subsets: ["latin"], variable: "--font-body" });

export const metadata: Metadata = {
  title: "AstroBuddy",
  description: "AI-assisted astrology platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body>
        <BirthProfileProvider>
          <AppShell>{children}</AppShell>
        </BirthProfileProvider>
      </body>
    </html>
  );
}
