"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Hourglass,
  TriangleAlert,
  RefreshCcw,
  LayoutDashboard,
  ArrowLeft,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { LinkButton } from "@/components/ui/link-button";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";
import { StatusIcon } from "@/components/layouts/status-icon";
import routeMap from "@/constants/route-map";

export default function RateLimitedPage() {
  const router = useRouter();

  return (
    <StatusPageLayout
      icon={
        <StatusIcon
          icon={<Hourglass />}
          badge={<TriangleAlert />}
          glowClassName="bg-orange-500/20"
        />
      }
      title="너무 많은 요청을 보냈어요"
      description={
        <div className="flex flex-col w-full">
          짧은 시간 동안 너무 많은 요청이 발생했습니다.
          <br />
          서버의 안정적인 운영을 위해
          <br />
          <span className="font-semibold text-foreground">
            잠시만 기다렸다가
          </span>{" "}
          다시 시도해주세요.
        </div>
      }
      footer={
        <p className="text-sm text-muted-foreground">
          반복적으로 문제가 발생한다면
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
        다시 시도하기
      </Button>
      <LinkButton
        href={routeMap.DASHBOARD.HOME}
        variant="secondary"
        size="lg"
        className="w-full"
      >
        <LayoutDashboard className="w-5 h-5 mr-2" />
        대시보드 홈으로
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
