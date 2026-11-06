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
          badgeClassName="bg-primary text-primary-foreground"
        />
      }
      title="봇 초대 화면으로 이동 중..."
      description={
        <div className="text-muted-foreground">
          디스코드에서 서버를 고르고 권한을 승인하면
          <br />
          초대가 완료됩니다.
        </div>
      }
    >
      <div className="w-full flex justify-center">
        <LinkButton
          href={BOT_INVITE_URL}
          variant="secondary"
          size="lg"
          className="w-full max-w-sm"
          onClick={() => {
            sendGAEvent("event", "click_invite_bot", {
              location: "redirect_page",
              method: "manual_click",
            });
          }}
        >
          <ExternalLink className="w-5 h-5 mr-2" />
          바로 이동하기
        </LinkButton>
      </div>
    </StatusPageLayout>
  );
}
