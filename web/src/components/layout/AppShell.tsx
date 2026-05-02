import { Outlet, useLocation } from "react-router-dom";

import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { AuraNightSky } from "@/components/ui/AuraNightSky";
import { FloatingAnimation } from "@/components/ui/FloatingAnimation";

export function AppShell() {
  const { pathname } = useLocation();
  const isCreate = pathname === "/" || pathname.startsWith("/create");

  return (
    <>
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 z-0"
      >
        {isCreate ? (
          <AuraNightSky
            stripesColor="#0F172A"
            rainbowColors={["#3B82F6", "#F59E0B", "#1E40AF", "#3B82F6", "#F59E0B"]}
            speed={0.6}
            stripeWidth={6}
            fadeEdges
            fadeStrength={60}
          />
        ) : (
          <div className="size-full opacity-25">
            <FloatingAnimation
              colorStops={["#1E3A8A", "#F59E0B", "#0F172A"]}
              amplitude={0.8}
              blend={0.7}
              speed={0.4}
            />
          </div>
        )}
      </div>
      <div className="relative z-10 flex min-h-dvh text-slate-100">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <TopBar />
          <main className="flex-1 overflow-y-auto px-6 py-8">
            <div className="mx-auto w-full max-w-6xl">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </>
  );
}
