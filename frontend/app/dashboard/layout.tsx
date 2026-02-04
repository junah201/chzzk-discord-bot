"use client";

import { DashboardSidebar } from "./components/sidebar";
import { GridPattern } from "@/components/ui/grid-pattern";
import MobileHeader from "./components/mobile-header";
import { AuthGuard } from "./components/auth-guard";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-background text-foreground">
        {/* Mobile Header */}
        <MobileHeader />

        {/* Desktop Sidebar */}
        <aside className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-30 lg:block lg:w-64">
          <DashboardSidebar />
        </aside>

        {/* Main Content */}
        <main className="lg:pl-64">
          <div className="absolute inset-0 pointer-events-none">
            <GridPattern mask="radial" />
          </div>
          <div className="pt-16 lg:pt-0">{children}</div>
        </main>
      </div>
    </AuthGuard>
  );
}
