"use client";

import { Logo } from "@/components/ui/logo";
import { Github, Mail } from "lucide-react";
import { motion } from "motion/react";

const socialLinks = [
  {
    icon: Github,
    href: "https://github.com/junah201/chzzk-discord-bot",
    label: "GitHub",
  },
  { icon: Mail, href: "mailto:junah.dev+chzzk@gmail.com", label: "Email" },
];

export const FooterBrand = () => {
  return (
    <div className="lg:col-span-2">
      <Logo />
      <p className="text-muted-foreground mb-6 max-w-sm">
        치지직 스트리밍 플랫폼의 방송 알림을 디스코드로 전송하는 가장 빠르고
        안정적인 봇 서비스입니다.
      </p>

      {/* Social Links */}
      <div className="flex items-center gap-3">
        {socialLinks.map((social) => (
          <motion.a
            key={social.label}
            href={social.href}
            target="_blank"
            rel="noopener noreferrer"
            className="w-10 h-10 rounded-lg bg-secondary hover:bg-primary/10 border border-border hover:border-primary/50 flex items-center justify-center transition-all group"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            aria-label={social.label}
          >
            <social.icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
          </motion.a>
        ))}
      </div>
    </div>
  );
};
