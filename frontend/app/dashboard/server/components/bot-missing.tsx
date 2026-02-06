"use client";

import { Bot, ArrowLeft, ExternalLink, ShieldAlert } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import routeMap from "@/constants/route-map";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";
import { StatusIcon } from "@/components/layouts/status-icon";

export default function BotMissingPage() {
  return (
    <StatusPageLayout
      icon={<StatusIcon icon={<Bot />} badge={<ShieldAlert />} />}
      title="봇이 서버에 없어요!"
      description={
        <>
          서비스를 이용하려면 먼저 치직 봇을
          <br />
          서버에 초대해야 합니다.
        </>
      }
      footer={
        <p className="text-sm text-muted-foreground">
          이미 봇을 초대하셨나요? ‘채널 보기’ 권한이 꺼져 있을 수 있습니다. 서버
          설정에서 봇의 권한을 확인해 주세요. 문제가 지속된다면{" "}
          <Link
            href={routeMap.REDIRECTS.SUPPORT_SERVER}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary underline"
          >
            서포트 서버
          </Link>
          에 문의해 주세요.
        </p>
      }
    >
      <LinkButton
        href={routeMap.REDIRECTS.INVITE}
        size="lg"
        className="w-full group"
      >
        <ExternalLink className="w-5 h-5 mr-2" />봇 초대하러 가기
      </LinkButton>
      <Button
        variant="outline"
        size="lg"
        className="w-full hover:bg-transparent hover:text-foreground text-muted-foreground"
        onClick={() => window.location.reload()}
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        이미 초대했어요
      </Button>
    </StatusPageLayout>
  );
}
