"use client";

import { GlowEffect } from "@/components/ui/glow-effect";
import { FooterBrand } from "./footer-brand";
import { FooterNav } from "./footer-nav";
import { FooterBottom } from "./footer-bottom";

const Footer = () => {
  return (
    <footer className="relative bg-card border-t border-border overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="absolute inset-0 pointer-events-none">
          <GlowEffect
            variant="static"
            className="top-0 left-[10%] w-96 h-96 bg-primary/5 blur-3xl"
          />
          <GlowEffect
            variant="static"
            className="bottom-0 right-[10%] w-96 h-96 bg-emerald-500/5 blur-3xl"
          />
        </div>
        {/* Main Footer Content */}
        <div className="py-12 sm:py-16 lg:py-20">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-12">
            <FooterBrand />
            <FooterNav />
          </div>
        </div>

        {/* Bottom Bar */}
        <FooterBottom />
      </div>
    </footer>
  );
};

export default Footer;
