"use client";

import { useEffect } from "react";
import { LifeBuoy, Loader2, MessageCircle } from "lucide-react";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";
import { StatusIcon } from "@/components/layouts/status-icon";
import { LinkButton } from "@/components/ui/link-button";
import { SUPPORT_SERVER_INVITE_URL } from "@/constants/links";

export default function SupportRedirectPage() {
  useEffect(() => {
    const timer = setTimeout(() => {
      window.location.replace(SUPPORT_SERVER_INVITE_URL);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <StatusPageLayout
      icon={
        <StatusIcon
          icon={<LifeBuoy />}
          badge={<Loader2 className="animate-spin" />}
          glowClassName="bg-orange-500/30"
        />
      }
      title="서포트 서버로 이동 중..."
      description={
        <div className="text-muted-foreground">
          궁금한 점이 있으신가요?
          <br />곧 서포트 서버로 연결됩니다.
        </div>
      }
    >
      <div className="w-full flex justify-center">
        <LinkButton
          href={SUPPORT_SERVER_INVITE_URL}
          variant="secondary"
          size="lg"
          className="w-full max-w-sm"
        >
          <MessageCircle className="w-5 h-5 mr-2" />
          바로 이동하기
        </LinkButton>
      </div>
    </StatusPageLayout>
  );
}
