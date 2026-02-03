import {
  PolicyCallout,
  PolicyLayout,
  PolicySection,
  PolicyTable,
  PolicyTd,
  PolicyTh,
  PolicyThead,
  PolicyTr,
} from "@/components/policy";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "치직 - 쿠키 정책",
  description: "치직 쿠키 정책 페이지입니다.",
  openGraph: {
    title: "치직 - 쿠키 정책",
    description: "치직 쿠키 정책 페이지입니다.",
  },
  twitter: {
    title: "치직 - 쿠키 정책",
    description: "치직 쿠키 정책 페이지입니다.",
  },
};

export default function CookiePolicy() {
  const lastUpdated = "2026년 02월 01일";

  const sections = [
    { id: "what-is-cookie", title: "쿠키란 무엇인가요?" },
    { id: "purpose", title: "쿠키 사용 목적" },
    { id: "cookie-list", title: "사용하는 쿠키 목록" },
    { id: "control", title: "쿠키 관리 및 거부 방법" },
  ];

  const notice = {
    title: "쿠키 정책",
    description:
      "치직 서비스가 사용자 경험을 개선하기 위해 쿠키 및 유사 기술을 사용하는 방식을 설명합니다.",
  };

  return (
    <PolicyLayout
      title="쿠키 정책"
      lastUpdated={lastUpdated}
      notice={notice}
      sections={sections}
    >
      {/* 01. 쿠키란 무엇인가요? */}
      <PolicySection id="what-is-cookie" index={1} title="쿠키란 무엇인가요?">
        <p>
          쿠키(Cookie)는 웹사이트를 방문할 때 사용자의 브라우저에 저장되는 작은
          텍스트 파일입니다. 이는 사용자의 로그인 상태를 유지하거나, 서비스 이용
          통계(방문자 수 등)를 측정하는 데 사용됩니다.
        </p>
      </PolicySection>

      {/* 02. 쿠키 사용 목적 */}
      <PolicySection id="purpose" index={2} title="쿠키 사용 목적">
        <p>
          회사는 최소한의 정보만을 수집하며, 다음과 같은 구체적인 목적을 위해
          쿠키를 사용합니다.
        </p>
        <ul>
          <li>
            <strong>서비스 핵심 기능 제공 (필수):</strong> 사용자의 디스코드
            계정 인증 정보를 유지하여 대시보드 접근 권한을 부여합니다. 이 쿠키가
            없으면 로그인이 필요한 모든 기능을 사용할 수 없습니다.
          </li>
          <li>
            <strong>서비스 이용 분석 (분석):</strong> Google Analytics를
            활용하여 방문자 수, 페이지 조회수, 그리고 알림 추가/삭제와 같은 주요
            이벤트 활동을 익명으로 수집합니다. 이는 서비스 개선과 오류 분석을
            위한 기초 자료로 활용됩니다.
          </li>
        </ul>
      </PolicySection>

      <PolicySection id="cookie-list" index={3} title="사용하는 쿠키 목록">
        <p>
          서비스에서 사용하는 쿠키의 상세 목록과 만료 기간은 다음과 같습니다.
        </p>

        <PolicyTable>
          <PolicyThead>
            <PolicyTh className="min-w-35">쿠키 이름</PolicyTh>
            <PolicyTh className="min-w-20">구분</PolicyTh>
            <PolicyTh className="min-w-25">제공자</PolicyTh>
            <PolicyTh className="min-w-35">만료 기간</PolicyTh>
            <PolicyTh className="min-w-100">상세 설명 및 목적</PolicyTh>
          </PolicyThead>

          <tbody className="divide-y divide-border">
            <PolicyTr>
              <PolicyTd className="font-mono text-primary font-medium">
                access-token
              </PolicyTd>
              <PolicyTd>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-500">
                  필수
                </span>
              </PolicyTd>
              <PolicyTd>치직 (자사)</PolicyTd>
              <PolicyTd>
                세션 종료 시<br />
                (또는 로그아웃 시)
              </PolicyTd>
              <PolicyTd className="leading-relaxed">
                Discord 로그인을 통해 발급된 인증 토큰입니다. 사용자를 식별하고
                대시보드 기능을 이용하기 위해 필요합니다.
              </PolicyTd>
            </PolicyTr>

            <PolicyTr>
              <PolicyTd className="font-mono text-primary font-medium">
                _ga
              </PolicyTd>
              <PolicyTd>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-500">
                  분석
                </span>
              </PolicyTd>
              <PolicyTd>Google</PolicyTd>
              <PolicyTd>2년</PolicyTd>
              <PolicyTd className="leading-relaxed">
                방문자를 구분하기 위해 사용되는 Google Analytics 식별자입니다.
              </PolicyTd>
            </PolicyTr>

            <PolicyTr>
              <PolicyTd className="font-mono text-primary font-medium">
                _gid
              </PolicyTd>
              <PolicyTd>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-500">
                  분석
                </span>
              </PolicyTd>
              <PolicyTd>Google</PolicyTd>
              <PolicyTd>24시간</PolicyTd>
              <PolicyTd className="leading-relaxed">
                페이지별 사용자 행동을 구분하기 위해 사용됩니다.
              </PolicyTd>
            </PolicyTr>
          </tbody>
        </PolicyTable>
      </PolicySection>

      <PolicySection id="control" index={4} title="쿠키 관리 및 거부 방법">
        <p>
          이용자는 웹 브라우저 설정을 통해 쿠키 저장을 거부할 수 있습니다. 다만,
          필수 쿠키(access-token) 저장을 거부할 경우{" "}
          <strong>
            로그인을 포함한 대시보드의 모든 기능을 사용할 수 없습니다.
          </strong>
        </p>
        <PolicyCallout variant="warning" title="주의사항">
          Google Analytics 쿠키는 차단하더라도 서비스 이용에 지장이 없으나,
          access-token 쿠키를 차단하면 인증이 불가능하여 서비스를 이용하실 수
          없습니다.
        </PolicyCallout>

        <div className="bg-secondary/30 p-4 rounded-lg border border-border/50">
          <h4 className="font-semibold mb-3 text-sm">
            브라우저별 쿠키 설정 가이드
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-sm">
            <a
              href="https://support.google.com/chrome/answer/95647?hl=ko"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 p-2 hover:bg-secondary rounded-md transition-colors"
            >
              🔵 Chrome 설정
            </a>
            <a
              href="https://support.apple.com/ko-kr/guide/safari/sfri11471/mac"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 p-2 hover:bg-secondary rounded-md transition-colors"
            >
              🔵 Safari 설정
            </a>
            <a
              href="https://support.microsoft.com/ko-kr/windows/microsoft-edge%EC%97%90%EC%84%9C-%EC%BF%A0%ED%82%A4-%EA%B4%80%EB%A6%AC-%EB%B3%B4%EA%B8%B0-%ED%97%88%EC%9A%A9-%EC%B0%A8%EB%8B%A8-%EC%82%AD%EC%A0%9C-%EB%B0%8F-%EC%82%AC%EC%9A%A9-168dab11-0753-043d-7c16-ede5947fc64d"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 p-2 hover:bg-secondary rounded-md transition-colors"
            >
              🔵 Edge 설정
            </a>
          </div>
        </div>
      </PolicySection>
    </PolicyLayout>
  );
}
