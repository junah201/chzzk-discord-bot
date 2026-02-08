"use client";

import { GITHUB_REPO_CHANGELOG_URL, GITHUB_USER_URL } from "@/constants/links";

export function FooterBottom() {
  const currentYear = new Date().getFullYear();
  const startYear = 2024;

  return (
    <div className="py-6 border-t border-border">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="text-center md:text-left space-y-1">
          <p className="text-sm text-muted-foreground">
            &copy; {startYear}-{currentYear}{" "}
            <a
              href={GITHUB_USER_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold hover:text-primary transition-colors"
            >
              @junah201
            </a>
            . All rights reserved.
          </p>
          <p className="text-[11px] text-muted-foreground/50 leading-tight">
            본 서비스는 네이버 주식회사에 의해 운영되지 않습니다.{" "}
            <br className="sm:hidden" />
            &apos;CHZZK&apos; 및 &apos;치지직&apos;은 네이버 주식회사의 등록
            상표입니다.
          </p>
        </div>

        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span className="text-border">•</span>
          <a
            href={GITHUB_REPO_CHANGELOG_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-primary transition-colors"
          >
            변경사항
          </a>
          <span className="text-border">•</span>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span>운영 중</span>
          </div>
        </div>
      </div>
    </div>
  );
}
