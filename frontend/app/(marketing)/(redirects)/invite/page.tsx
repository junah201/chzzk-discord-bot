"use client";

import { useEffect } from "react";
import { Bot, Loader2, ExternalLink } from "lucide-react";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";
import { StatusIcon } from "@/components/layouts/status-icon";
import { LinkButton } from "@/components/ui/link-button";
import { BOT_INVITE_URL } from "@/constants/links";
import { sendGAEvent } from "@next/third-parties/google";

export default function InviteRedirectPage() {
  useEffect(() => {
    sendGAEvent("event", "click_invite_bot", {
      location: "redirect_page",
      method: "auto_redirect",
    });

    const timer = setTimeout(() => {
      window.location.replace(BOT_INVITE_URL);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <StatusPageLayout
      icon={
        <StatusIcon
          icon={<Bot />}
          badge={<Loader2 className="animate-spin" />}
          glowClassName="bg-primary/30"
        />
      }
      title="치직 봇을 초대하러 갈게요!"
      description={
        <div className="text-muted-foreground">
          잠시만 기다려주세요.
          <br />
          디스코드 인증 페이지로 이동하고 있습니다.
        </div>
      }
    >
      <div className="w-full flex justify-center">
        <LinkButton
          href={BOT_INVITE_URL}
          size="lg"
          className="w-full max-w-sm animate-pulse"
          onClick={() => {
            sendGAEvent("event", "click_invite_bot", {
              location: "redirect_page",
              method: "manual_click",
            });
          }}
        >
          <ExternalLink className="w-5 h-5 mr-2" />
          이동하지 않으면 클릭하세요
        </LinkButton>
      </div>
    </StatusPageLayout>
  );
}
