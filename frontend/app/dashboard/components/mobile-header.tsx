"use client";

import { useState } from "react";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { DashboardSidebar } from "./sidebar";
import { Logo } from "@/components/ui/logo";

export default function MobileHeader() {
  const [open, setOpen] = useState(false);

  // 사이드바 안의 링크를 누르면 페이지 이동과 함께 시트를 닫음
  const handleContentClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if ((e.target as HTMLElement).closest("a")) {
      setOpen(false);
    }
  };

  return (
    <header className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-background/95 backdrop-blur-lg border-b border-border">
      <div className="flex items-center justify-between h-16 px-4">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="outline" className="lg:hidden" size="icon">
              <Menu className="w-6 h-6" />
            </Button>
          </SheetTrigger>
          <SheetContent
            side="left"
            className="w-64 p-0 bg-sidebar"
            onClick={handleContentClick}
          >
            <SheetTitle className="sr-only">대시보드 메뉴</SheetTitle>
            <DashboardSidebar />
          </SheetContent>
        </Sheet>

        <div className="flex-1 flex justify-center">
          <Logo size="md" />
        </div>

        {/* 로고가 가운데 오도록 메뉴 버튼만큼 비워 둠 */}
        <div className="w-10" />
      </div>
    </header>
  );
}
