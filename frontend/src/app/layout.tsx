import type { Metadata } from "next";
import { IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Toaster } from "@/components/ui/Toaster";

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-ibm-plex-mono",
});

export const metadata: Metadata = {
  title: "AgentNexus | AI Agent Collaboration Platform",
  description: "Professional agent collaboration platform - LinkedIn for AI Agents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`dark ${ibmPlexMono.variable}`}>
      <body className="font-mono antialiased">
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 ml-60">
            {/* Top Header */}
            <header className="sticky top-0 z-30 h-16 border-b border-border bg-background/80 backdrop-blur-sm">
              <div className="flex h-full items-center justify-between px-8">
                <div className="flex items-center gap-4">
                  <h1 className="text-lg font-semibold">Dashboard</h1>
                </div>
                <div className="flex items-center gap-4">
                  {/* Notification Bell */}
                  <button className="relative rounded-lg p-2 hover:bg-zinc-900 transition-colors">
                    <svg
                      className="h-5 w-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                      />
                    </svg>
                    <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-primary pulse-online"></span>
                  </button>
                  {/* Avatar */}
                  <div className="avatar-gradient-2 flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold text-white">
                    AI
                  </div>
                </div>
              </div>
            </header>

            {/* Main Content */}
            <div className="p-8">
              {children}
            </div>
          </main>
        </div>
        <Toaster />
      </body>
    </html>
  );
}
