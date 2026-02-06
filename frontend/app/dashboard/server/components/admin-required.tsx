"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ShieldBan,
  Lock,
  RefreshCcw,
  LayoutDashboard,
  ArrowLeft,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { LinkButton } from "@/components/ui/link-button";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";
import { StatusIcon } from "@/components/layouts/status-icon";
import routeMap from "@/constants/route-map";

export default function AdminRequiredPage() {
  const router = useRouter();

  return (
    <StatusPageLayout
      icon={
        <StatusIcon
          icon={<ShieldBan />}
          badge={<Lock />}
          glowClassName="bg-destructive/20"
        />
      }
      title="관리자 권한이 필요해요"
      description={
        <div className="flex flex-col w-full">
          해당 서버의{" "}
          <span className="font-semibold text-foreground">
            관리자(Administrator)
          </span>{" "}
          권한이
          <br />
          확인되지 않아 접근할 수 없습니다.
          <br />
          <span className="block mt-4 text-sm bg-muted/50 p-3 rounded-lg border border-border/50">
            디스코드 역할 설정에서 <b>&apos;관리자&apos;</b> 스위치가
            <br />
            반드시 켜져 있어야 합니다.
          </span>
        </div>
      }
      footer={
        <p className="text-sm text-muted-foreground">
          권한을 수정했는데도 접근이 안 되나요?
          <br className="sm:hidden" />
          <Link
            href={routeMap.REDIRECTS.SUPPORT_SERVER}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary underline hover:text-primary/80 transition-colors ml-1"
          >
            서포트 서버
          </Link>
          에 문의해 주세요.
        </p>
      }
    >
      <Button
        size="lg"
        className="w-full group"
        onClick={() => window.location.reload()}
      >
        <RefreshCcw className="w-5 h-5 mr-2 group-hover:rotate-180 transition-transform duration-500" />
        권한 확인 후 새로고침
      </Button>
      <LinkButton
        href={routeMap.DASHBOARD.HOME}
        variant="secondary"
        size="lg"
        className="w-full"
      >
        <LayoutDashboard className="w-5 h-5 mr-2" />
        다른 서버 선택하기
      </LinkButton>
      <Button
        variant="ghost"
        size="lg"
        className="w-full text-muted-foreground hover:bg-transparent hover:text-foreground"
        onClick={() => router.back()}
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        이전 페이지
      </Button>
    </StatusPageLayout>
  );
}
