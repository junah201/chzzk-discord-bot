"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { FileQuestion, SearchX, Home, ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import { LinkButton } from "@/components/ui/link-button";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";
import { StatusIcon } from "@/components/layouts/status-icon";
import routeMap from "@/constants/route-map";

export default function NotFoundPage() {
  const router = useRouter();

  return (
    <StatusPageLayout
      icon={
        <StatusIcon
          icon={<FileQuestion />}
          badge={<SearchX />}
          glowClassName="bg-zinc-500/20"
        />
      }
      title="페이지를 찾을 수 없어요"
      description={
        <div className="flex flex-col w-full">
          요청하신 페이지가 사라졌거나
          <br />
          잘못된 경로로 접근하셨습니다.
          <br />
          <span className="font-semibold text-foreground">입력하신 주소</span>를
          다시 한번 확인해 주세요.
        </div>
      }
      footer={
        <p className="text-sm text-muted-foreground">
          링크가 잘못된 것 같다면
          <br className="sm:hidden" />
          <Link
            href={routeMap.REDIRECTS.SUPPORT_SERVER}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary underline hover:text-primary/80 transition-colors ml-1"
          >
            서포트 서버
          </Link>
          에 제보해 주세요.
        </p>
      }
    >
      <LinkButton href={routeMap.HOME} size="lg" className="w-full group">
        <Home className="w-5 h-5 mr-2" />
        홈으로 가기
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
