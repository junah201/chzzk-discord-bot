"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { ChevronRight } from "lucide-react";
import { motion } from "motion/react";
import routeMap from "@/constants/route-map";

const NAV_ITEMS = [
  { title: "1. 시작하기 (봇 설치)", href: routeMap.DOCS.INSTALLATION },
  { title: "2. 알림 등록하기", href: routeMap.DOCS.NOTIFICATIONS },
  { title: "3. 메시지 커스텀 (멘션)", href: routeMap.DOCS.CUSTOMIZATION },
  { title: "4. 문제 해결 (FAQ)", href: routeMap.DOCS.TROUBLESHOOTING },
];

export function DocsSidebar() {
  const pathname = usePathname();

  console.log(pathname);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-card border border-border rounded-2xl p-6"
    >
      <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
        <ChevronRight className="w-5 h-5 text-primary" />
        목차
      </h3>
      <nav className="space-y-2">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "block w-full text-left px-4 py-2 rounded-lg transition-all text-sm font-medium",
                isActive
                  ? "bg-primary/10 text-primary border-l-4 border-primary translate-x-1"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary",
              )}
            >
              {item.title}
            </Link>
          );
        })}
      </nav>
    </motion.div>
  );
}
