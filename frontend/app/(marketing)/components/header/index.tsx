"use client";

import { LinkButton } from "@/components/ui/link-button";
import { Logo } from "@/components/ui/logo";
import { NavLink } from "@/components/ui/nav-link";
import { navLinks } from "@/constants/nav";
import { useScrollThreshold } from "@/hooks/use-scroll-threshold";
import { cn } from "@/lib/utils";
import { motion } from "motion/react";

export default function Header() {
  const isScrolled = useScrollThreshold(10);

  return (
    <motion.header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        {
          "bg-background/80 backdrop-blur-lg border-b border-border":
            isScrolled,
          "bg-transparent": !isScrolled,
        },
      )}
    >
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">
          <Logo />

          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <NavLink key={link.href} {...link} />
            ))}
            <LinkButton href="/login" variant="primary">
              대시보드 로그인
            </LinkButton>
          </div>
        </div>
      </nav>
    </motion.header>
  );
}
