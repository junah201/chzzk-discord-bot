"use client";

import { useState } from "react";
import Link from "next/link";
import { LayoutDashboard, Menu } from "lucide-react";

import { Button } from "@/components/ui/button";
import { LinkButton } from "@/components/ui/link-button";
import { Logo } from "@/components/ui/logo";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { navLinks } from "@/constants/nav";
import routeMap from "@/constants/route-map";

export function MobileNav() {
  const [open, setOpen] = useState(false);

  // 메뉴 안의 링크를 누르면 이동과 함께 시트를 닫음
  const handleContentClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if ((e.target as HTMLElement).closest("a")) {
      setOpen(false);
    }
  };

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="메뉴 열기">
          <Menu className="size-6" />
        </Button>
      </SheetTrigger>
      <SheetContent
        side="right"
        className="w-72 gap-0 bg-background p-0"
        onClick={handleContentClick}
      >
        <SheetTitle className="sr-only">메뉴</SheetTitle>
        <div className="flex h-16 items-center border-b border-border px-6">
          <Logo size="sm" />
        </div>

        <nav className="flex flex-col p-3">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-lg px-3 py-3 text-base font-medium text-foreground/80 transition-colors hover:bg-muted hover:text-primary"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="mt-auto border-t border-border p-4">
          <LinkButton
            href={routeMap.DASHBOARD.HOME}
            variant="primary"
            className="w-full"
          >
            <LayoutDashboard className="size-4" />
            대시보드로 이동
          </LinkButton>
        </div>
      </SheetContent>
    </Sheet>
  );
}
