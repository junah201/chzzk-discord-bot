"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  TriangleAlert,
  ServerCrash,
  RefreshCcw,
  LayoutDashboard,
  ArrowLeft,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { LinkButton } from "@/components/ui/link-button";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";
import { StatusIcon } from "@/components/layouts/status-icon";
import routeMap from "@/constants/route-map";
import { isAxiosError } from "axios";

interface UnknownErrorPageProps {
  error: unknown;
}

export default function UnknownErrorPage({ error }: UnknownErrorPageProps) {
  const router = useRouter();

  const errorMessage = (() => {
    if (isAxiosError(error)) {
      return `${error.response?.status} ${JSON.stringify(error.response?.data)}`;
    } else {
      return String(error);
    }
  })();

  return (
    <StatusPageLayout
      icon={
        <StatusIcon
          icon={<TriangleAlert />}
          badge={<ServerCrash />}
          glowClassName="bg-destructive/20"
        />
      }
      title="알 수 없는 오류가 발생했어요"
      description={
        <>
          서버 내부 정보를 가져오는 도중
          <br />
          예기치 못한 문제가 발생했습니다.
          <br />
          {errorMessage}
        </>
      }
      footer={
        <p className="text-sm text-muted-foreground">
          문제가 지속적으로 발생한다면 <br className="sm:hidden" />
          <Link
            href={routeMap.REDIRECTS.SUPPORT_SERVER}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary underline hover:text-primary/80 transition-colors"
          >
            서포트 서버
          </Link>
          에 오류 내용을 제보해 주세요.
        </p>
      }
    >
      <Button
        size="lg"
        className="w-full group"
        onClick={() => window.location.reload()}
      >
        <RefreshCcw className="w-5 h-5 mr-2 group-hover:rotate-180 transition-transform duration-500" />
        페이지 새로고침
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
