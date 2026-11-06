"use client";

import { useEffect } from "react";
import { SiDiscord } from "@icons-pack/react-simple-icons";
import { ExternalLink, Loader2 } from "lucide-react";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";
import { StatusIcon } from "@/components/layouts/status-icon";
import { LinkButton } from "@/components/ui/link-button";
import { SUPPORT_SERVER_INVITE_URL } from "@/constants/links";
import { sendGAEvent } from "@next/third-parties/google";

export default function SupportRedirectPage() {
  useEffect(() => {
    sendGAEvent("event", "click_support_discord", {
      location: "redirect_page",
      method: "auto_redirect",
    });

    const timer = setTimeout(() => {
      window.location.replace(SUPPORT_SERVER_INVITE_URL);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <StatusPageLayout
      icon={
        <StatusIcon
          icon={<SiDiscord />}
          badge={<Loader2 className="animate-spin" />}
          glowClassName="bg-primary/30"
          badgeClassName="bg-primary text-primary-foreground"
        />
      }
      title="서포트 서버로 이동 중..."
      description={
        <div className="text-muted-foreground">
          서포트 서버에서 궁금한 점을 질문하거나
          <br />
          문제를 알려주세요.
        </div>
      }
    >
      <div className="w-full flex justify-center">
        <LinkButton
          href={SUPPORT_SERVER_INVITE_URL}
          target="_self"
          variant="secondary"
          size="lg"
          className="w-full max-w-sm"
          onClick={() => {
            sendGAEvent("event", "click_support_discord", {
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
