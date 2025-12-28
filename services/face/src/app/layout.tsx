import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Helixa-One | Smart Brain",
  description: "Advanced Data Center Intelligence System",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased flex min-h-screen flex-col bg-background text-foreground`}
      >
        <div className="flex-1">
          {children}
        </div>
        <footer className="w-full bg-black/95 backdrop-blur-sm text-white/80 py-6 px-4 border-t border-white/10 shadow-[0_-10px_30px_rgba(0,0,0,0.5)]">
          <div className="container mx-auto text-center">
            <p className="text-xs sm:text-sm md:text-base font-mono tracking-wide">
              Developed by <span className="font-bold text-accent">Cezi Cola</span> Senior Software Engineer CEO{" "}
              <span className="font-bold text-accent">Bio Code Technology</span> — All Rights Reserved 2025
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
