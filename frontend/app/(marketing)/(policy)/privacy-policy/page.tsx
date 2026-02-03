import {
  PolicyExternalLink,
  PolicyLayout,
  PolicySection,
  PolicyTable,
  PolicyTbody,
  PolicyTd,
  PolicyTh,
  PolicyThead,
  PolicyTr,
} from "@/components/policy";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "치직 - 개인정보 처리방침",
  description: "치직 개인정보 처리방침 페이지입니다.",
  openGraph: {
    title: "치직 - 개인정보 처리방침",
    description: "치직 개인정보 처리방침 페이지입니다.",
  },
  twitter: {
    title: "치직 - 개인정보 처리방침",
    description: "치직 개인정보 처리방침 페이지입니다.",
  },
};

export default function PrivacyPolicy() {
  const sections = [
    { id: "collection", title: "수집하는 정보 및 보유기간" },
    { id: "rights", title: "정보주체의 권리 및 행사 방법" },
    { id: "destruction", title: "개인정보 파기 절차 및 방법" },
    { id: "cpo", title: "개인정보 보호책임자 및 담당부서" },
    { id: "remedy", title: "권익침해 구제방법" },
  ];

  const notice = {
    title: "개인정보 처리방침",
    description:
      "치직 서비스는 이용자의 개인정보를 소중히 다루며, 정보통신망법 및 개인정보보호법을 준수합니다.",
  };

  const REMEDY_AGENCIES = [
    {
      title: "개인정보분쟁조정위원회",
      description: "📞 (국번없이) 1833-6972",
      href: "https://www.kopico.go.kr",
      label: "www.kopico.go.kr",
    },
    {
      title: "개인정보침해신고센터",
      description: "📞 (국번없이) 118",
      href: "https://privacy.kisa.or.kr",
      label: "privacy.kisa.or.kr",
    },
    {
      title: "대검찰청",
      description: "📞 (국번없이) 1301",
      href: "https://www.spo.go.kr",
      label: "www.spo.go.kr",
    },
    {
      title: "경찰청",
      description: "📞 (국번없이) 182",
      href: "https://ecrm.cyber.go.kr",
      label: "ecrm.cyber.go.kr",
    },
  ];

  return (
    <PolicyLayout
      title="개인정보 처리방침"
      lastUpdated="2025년 03월 08일"
      notice={notice}
      sections={sections}
    >
      <PolicySection
        id="collection"
        index={1}
        title="수집하는 개인정보의 항목, 목적, 보유기간"
      >
        <p>
          회사는 원활한 서비스 제공을 위해 필요한 최소한의 정보만을 수집하며,
          <strong>
            서비스 기능 수행(알림 발송)을 위해 저장하는 정보
          </strong>와{" "}
          <strong>본인 확인 및 권한 확인을 위해 임시로 사용하는 정보</strong>를
          구분하여 처리합니다.
        </p>
        <PolicyTable>
          <PolicyThead>
            <PolicyTh className="min-w-25">구분</PolicyTh>
            <PolicyTh className="min-w-50">수집 항목</PolicyTh>
            <PolicyTh className="min-w-50">수집 및 이용 목적</PolicyTh>
            <PolicyTh className="min-w-35 text-primary font-bold">
              보유 및 이용 기간
            </PolicyTh>
          </PolicyThead>
          <PolicyTbody>
            <PolicyTr>
              <PolicyTd className="font-medium text-primary">
                방송 알림 정보
                <br />
                <span className="text-xs text-muted-foreground font-normal">
                  (DB 저장)
                </span>
              </PolicyTd>
              <PolicyTd>
                <ul className="list-disc pl-4 space-y-1">
                  <li>
                    <strong>치지직:</strong> 채널명, 채널 ID, 프로필 이미지 URL,
                    마지막 Live ID
                  </li>
                  <li>
                    <strong>디스코드:</strong> 서버명, 서버 ID, 채널명, 채널 ID
                  </li>
                  <li>
                    <strong>기타:</strong> 유저 설정 커스텀 알림 메시지
                  </li>
                </ul>
              </PolicyTd>
              <PolicyTd>
                방송 상태 모니터링 및 지정된 디스코드 채널로 알림 발송
              </PolicyTd>
              <PolicyTd className="font-semibold">
                알림 설정 삭제 시 즉시 파기
              </PolicyTd>
            </PolicyTr>

            {/* Row 2: 대시보드 접속 정보 (휘발성) */}
            <PolicyTr>
              <PolicyTd className="font-medium text-muted-foreground">
                대시보드 접속 정보
                <br />
                <span className="text-xs font-normal">(저장 안함)</span>
              </PolicyTd>
              <PolicyTd>
                <ul className="list-disc pl-4 space-y-1">
                  <li>이용자 디스코드 이름, 프로필 이미지</li>
                  <li>접근하려는 서버의 관리자 권한 보유 여부</li>
                  <li>관리 가능한 디스코드 서버 목록</li>
                </ul>
              </PolicyTd>
              <PolicyTd>
                서비스 이용 자격 확인(로그인) 및 서버 설정 권한 검증
              </PolicyTd>
              <PolicyTd className="text-muted-foreground">
                <strong>저장하지 않음</strong>
                <br />
                (브라우저 종료 또는 세션 만료 시 소멸)
              </PolicyTd>
            </PolicyTr>
          </PolicyTbody>
        </PolicyTable>

        <div className="mt-4 p-4 bg-secondary/30 rounded-lg border border-border/50 text-sm">
          <p className="font-semibold mb-1 text-primary">
            ※ 디스코드 서버 정보 처리에 대한 안내
          </p>
          <p className="text-muted-foreground leading-relaxed">
            대시보드에서 보여지는 ‘서버 목록’은 이용자가 관리자 권한을 가진
            서버를 확인하기 위해 Discord API를 통해 실시간으로 조회하여 화면에
            표시할 뿐,
            <strong>
              실제로 알림을 등록하기 전까지는 해당 서버의 정보를 회사의
              데이터베이스에 저장하지 않습니다.
            </strong>
          </p>
        </div>
      </PolicySection>

      <PolicySection id="rights" index={2} title="정보주체의 권리 및 행사 방법">
        <ul>
          <li>
            이용자는 언제든지 등록된 알림 설정을 삭제함으로써 저장된
            개인정보(알림 설정 정보)를 즉시 파기할 수 있습니다.
          </li>
          <li>
            대시보드 접속 시 사용된 개인정보(이름, 프로필 등)는 별도로 저장되지
            않으므로, 로그아웃 시 더 이상 처리되지 않습니다.
          </li>
          <li>
            권리 행사는 치직 서포트 서버 문의 채널 또는 개인정보 보호책임자
            이메일을 통해 요청하실 수 있습니다.
          </li>
        </ul>
      </PolicySection>

      <PolicySection
        id="destruction"
        index={3}
        title="개인정보 파기 절차 및 방법"
      >
        <p>회사는 수집 목적이 달성된 개인정보를 지체 없이 파기합니다.</p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div className="bg-secondary/30 p-4 rounded-lg border border-border/50">
            <h4 className="font-semibold mb-2 text-sm text-primary">
              자동 파기 (알림 데이터)
            </h4>
            <p className="text-sm text-muted-foreground">
              이용자가 대시보드 또는 명령어를 통해 알림 설정을 삭제하거나, 봇이
              서버에서 추방되어 알림을 발송할 수 없게 된 경우 해당 데이터는
              DB에서 즉시 영구 삭제됩니다.
            </p>
          </div>
          <div className="bg-secondary/30 p-4 rounded-lg border border-border/50">
            <h4 className="font-semibold mb-2 text-sm text-primary">
              휘발성 데이터
            </h4>
            <p className="text-sm text-muted-foreground">
              대시보드 이용 과정에서 조회된 이용자 정보 및 서버 목록은 화면 표시
              및 권한 검증 용도로만 사용되며, 별도의 저장 장치에 기록되지
              않습니다.
            </p>
          </div>
        </div>
      </PolicySection>

      <PolicySection id="cpo" index={4} title="개인정보 보호책임자 및 연락처">
        <div className="bg-card border-l-4 border-primary p-4 rounded-r-lg">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-muted-foreground">
                이름
              </dt>
              <dd className="mt-1 text-sm font-semibold">@junah201</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-muted-foreground">
                직책
              </dt>
              <dd className="mt-1 text-sm">개발자 및 운영자</dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-muted-foreground">
                이메일 문의
              </dt>
              <dd className="mt-1 text-sm font-semibold hover:text-primary transition-colors">
                <a href="mailto:junah.dev+chzzk@gmail.com">
                  junah.dev+chzzk@gmail.com
                </a>
              </dd>
            </div>
          </dl>
        </div>
      </PolicySection>

      <PolicySection
        id="remedy"
        index={5}
        title="정보주체의 권익침해에 대한 구제방법"
      >
        <p>
          기타 개인정보침해에 대한 신고나 상담이 필요하신 경우에는 아래 기관에
          문의하시기 바랍니다.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {REMEDY_AGENCIES.map((agency) => (
            <PolicyExternalLink key={agency.title} {...agency} />
          ))}
        </div>
      </PolicySection>
    </PolicyLayout>
  );
}
