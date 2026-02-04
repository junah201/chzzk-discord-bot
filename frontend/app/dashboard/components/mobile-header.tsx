import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { DashboardSidebar } from "./sidebar";
import { Logo } from "@/components/ui/logo";

export default function MobileHeader() {
  return (
    <header className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-background/95 backdrop-blur-lg border-b border-border">
      <div className="flex items-center justify-between h-16 px-4">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" className="lg:hidden" size="icon">
              <Menu className="w-6 h-6" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64 p-0 bg-sidebar">
            <DashboardSidebar />
          </SheetContent>
        </Sheet>

        {/* Mobile Logo */}
        <div className="flex-1 flex justify-center">
          <Logo size="md" />
        </div>

        {/* Spacer for balance */}
        <div className="w-10" />
      </div>
    </header>
  );
}
