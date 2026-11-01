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
import routeMap from "@/constants/route-map";
import { Metadata } from "next";
import Link from "next/link";

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

const SECTIONS = [
  { id: "collection", title: "처리하는 개인정보의 항목, 목적, 보유기간" },
  { id: "third-party", title: "개인정보의 제3자 제공" },
  { id: "outsourcing", title: "개인정보 처리위탁 및 국외이전" },
  { id: "rights", title: "정보주체의 권리 및 행사 방법" },
  { id: "destruction", title: "개인정보 파기 절차 및 방법" },
  { id: "security", title: "개인정보의 안전성 확보 조치" },
  { id: "cookie", title: "자동 수집 장치의 설치, 운영 및 거부" },
  { id: "cpo", title: "개인정보 보호책임자 및 연락처" },
  { id: "remedy", title: "권익침해 구제방법" },
  { id: "changes", title: "개인정보 처리방침의 변경" },
];

const NOTICE = {
  title: "개인정보 처리방침",
  description:
    "@junah201(이하 “제공자”)은 치직 서비스 이용자의 개인정보를 소중히 다루며, 「개인정보 보호법」을 준수합니다.",
};

const SUPPORT_EMAIL = "junah.dev+chzzk@gmail.com";

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

function SupportServerLink() {
  return (
    <Link
      href={routeMap.REDIRECTS.SUPPORT_SERVER}
      target="_blank"
      rel="noopener noreferrer"
    >
      치직 서포트 서버
    </Link>
  );
}

export default function PrivacyPolicy() {
  return (
    <PolicyLayout
      title="개인정보 처리방침"
      lastUpdated="2026년 11월 2일"
      notice={NOTICE}
      sections={SECTIONS}
    >
      <PolicySection
        id="collection"
        index={1}
        title="처리하는 개인정보의 항목, 목적, 보유기간"
      >
        <p>
          제공자는 서비스 제공에 필요한 최소한의 정보만 처리하며,{" "}
          <strong>알림 발송과 유료 서비스 제공을 위해 저장하는 정보</strong>와{" "}
          <strong>로그인과 권한 확인에만 잠시 사용하는 정보</strong>를 구분하여
          처리합니다.
        </p>
        <PolicyTable>
          <PolicyThead>
            <PolicyTh className="min-w-25">구분</PolicyTh>
            <PolicyTh className="min-w-50">처리 항목</PolicyTh>
            <PolicyTh className="min-w-50">처리 목적</PolicyTh>
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
                  (서버에 저장)
                </span>
              </PolicyTd>
              <PolicyTd>
                <ul className="list-disc pl-4 space-y-1">
                  <li>
                    <strong>치지직:</strong> 채널명, 채널 ID, 프로필 이미지 URL,
                    마지막으로 알림을 보낸 방송 정보(방송 ID, 방송 제목)
                  </li>
                  <li>
                    <strong>디스코드:</strong> 서버 ID, 채널명, 채널 ID
                  </li>
                  <li>
                    <strong>알림 설정:</strong> 이용자가 입력한 알림 메시지,
                    알림 표시 옵션, 커스텀 웹훅 URL과 임베드 색상(구독자 기능
                    이용 시)
                  </li>
                  <li>
                    <strong>발송 기록:</strong> 마지막 발송 시각, 발송 결과,
                    연속 실패 횟수
                  </li>
                </ul>
              </PolicyTd>
              <PolicyTd>
                방송 상태 확인, 지정한 디스코드 채널로 알림 발송, 발송 실패 확인
              </PolicyTd>
              <PolicyTd className="font-semibold">
                알림 설정 삭제 시 즉시 파기
              </PolicyTd>
            </PolicyTr>

            <PolicyTr>
              <PolicyTd className="font-medium text-primary">
                유료 서비스 결제 정보
                <br />
                <span className="text-xs text-muted-foreground font-normal">
                  (서버에 저장)
                </span>
              </PolicyTd>
              <PolicyTd>
                <ul className="list-disc pl-4 space-y-1">
                  <li>결제자 디스코드 ID, 적용 대상 디스코드 서버 ID</li>
                  <li>
                    상품 종류, 결제 금액, 결제 일시, 결제 상태, 구독 만료일,
                    알림 슬롯 변경 내역
                  </li>
                  <li>입금자명(계좌이체 입금 확인용)</li>
                </ul>
              </PolicyTd>
              <PolicyTd>
                입금 확인, 유료 서비스 적용, 구독 관리, 환불 및 분쟁 처리
              </PolicyTd>
              <PolicyTd className="font-semibold">
                결제일로부터 5년
                <br />
                <span className="text-xs text-muted-foreground font-normal">
                  (「전자상거래 등에서의 소비자보호에 관한 법률」)
                </span>
              </PolicyTd>
            </PolicyTr>

            <PolicyTr>
              <PolicyTd className="font-medium text-muted-foreground">
                대시보드 접속 정보
                <br />
                <span className="text-xs font-normal">(저장하지 않음)</span>
              </PolicyTd>
              <PolicyTd>
                <ul className="list-disc pl-4 space-y-1">
                  <li>디스코드 이름, 프로필 이미지, 이메일 주소</li>
                  <li>참여 중인 디스코드 서버 목록과 서버별 관리자 권한</li>
                  <li>서버별 멤버 정보(서버 닉네임, 역할 등)</li>
                </ul>
              </PolicyTd>
              <PolicyTd>대시보드 로그인, 서버 설정 권한 확인</PolicyTd>
              <PolicyTd className="text-muted-foreground">
                <strong>저장하지 않음</strong>
                <br />
                (브라우저 종료 또는 세션 만료 시 소멸)
              </PolicyTd>
            </PolicyTr>

            <PolicyTr>
              <PolicyTd className="font-medium text-muted-foreground">
                자동 수집 정보
                <br />
                <span className="text-xs font-normal">(Google Analytics)</span>
              </PolicyTd>
              <PolicyTd>
                <ul className="list-disc pl-4 space-y-1">
                  <li>쿠키 식별자, 방문 페이지, 방문 일시</li>
                  <li>기기, 브라우저, 운영체제 정보</li>
                  <li>로그인 시도 등 서비스 이용 기록</li>
                </ul>
              </PolicyTd>
              <PolicyTd>방문 통계 분석, 서비스 개선</PolicyTd>
              <PolicyTd className="text-muted-foreground">
                수집일로부터 최대 14개월
              </PolicyTd>
            </PolicyTr>
          </PolicyTbody>
        </PolicyTable>

        <div className="mt-4 p-4 bg-secondary/30 rounded-lg border border-border/50 text-sm">
          <p className="font-semibold mb-1 text-primary">
            ※ 디스코드 서버 정보 처리 안내
          </p>
          <p className="text-muted-foreground leading-relaxed">
            대시보드의 ‘서버 목록’은 이용자가 관리자 권한을 가진 서버를 보여주기
            위해 접속할 때마다 디스코드에서 불러와 화면에 표시합니다.{" "}
            <strong>
              알림을 등록하기 전까지는 해당 서버의 정보를 저장하지 않습니다.
            </strong>
          </p>
        </div>
      </PolicySection>

      <PolicySection id="third-party" index={2} title="개인정보의 제3자 제공">
        <p>
          제공자는 이용자의 개인정보를 제3자에게 제공하지 않습니다. 다만 법령에
          특별한 규정이 있거나, 수사기관이 법령에 정해진 절차에 따라 요청하는
          경우에는 예외로 합니다.
        </p>
      </PolicySection>

      <PolicySection
        id="outsourcing"
        index={3}
        title="개인정보 처리위탁 및 국외이전"
      >
        <p>
          제공자는 서비스 운영을 위해 아래와 같이 개인정보 처리 업무를 위탁하고
          있습니다.
        </p>
        <PolicyTable>
          <PolicyThead>
            <PolicyTh className="min-w-35">수탁자</PolicyTh>
            <PolicyTh className="min-w-50">위탁 업무</PolicyTh>
            <PolicyTh className="min-w-35">처리 위치</PolicyTh>
          </PolicyThead>
          <PolicyTbody>
            <PolicyTr>
              <PolicyTd className="font-medium">
                Amazon Web Services, Inc.
              </PolicyTd>
              <PolicyTd>
                서버 운영, 데이터베이스 저장, 서비스 로그 보관
              </PolicyTd>
              <PolicyTd>대한민국(서울 리전)</PolicyTd>
            </PolicyTr>
            <PolicyTr>
              <PolicyTd className="font-medium">Google LLC</PolicyTd>
              <PolicyTd>Google Analytics를 이용한 방문 통계 분석</PolicyTd>
              <PolicyTd>미국</PolicyTd>
            </PolicyTr>
          </PolicyTbody>
        </PolicyTable>

        <p className="mt-6">
          이 중 Google Analytics 이용 과정에서 아래와 같이 개인정보가 국외로
          이전됩니다.
        </p>
        <ul>
          <li>
            <strong>이전받는 자:</strong> Google LLC (
            <a
              href="https://support.google.com/policies/contact/general_privacy_form"
              target="_blank"
              rel="noopener noreferrer"
            >
              개인정보 문의
            </a>
            )
          </li>
          <li>
            <strong>이전 국가:</strong> 미국
          </li>
          <li>
            <strong>이전 항목:</strong> 1조의 ‘자동 수집 정보’
          </li>
          <li>
            <strong>이전 시기 및 방법:</strong> 웹사이트 방문 시 네트워크를 통해
            전송
          </li>
          <li>
            <strong>이전 목적:</strong> 방문 통계 분석
          </li>
          <li>
            <strong>보유 및 이용 기간:</strong> 수집일로부터 최대 14개월
          </li>
          <li>
            <strong>거부 방법:</strong> 7조의 방법으로 쿠키 저장을 거부할 수
            있으며, 거부해도 서비스 이용에는 지장이 없습니다.
          </li>
        </ul>
      </PolicySection>

      <PolicySection id="rights" index={4} title="정보주체의 권리 및 행사 방법">
        <ol>
          <li>
            이용자는 언제든지 자신의 개인정보 열람, 정정, 삭제, 처리정지를
            요구할 수 있습니다.
          </li>
          <li>
            등록한 알림 정보는 대시보드나 명령어로 알림 설정을 삭제하여 직접
            파기할 수 있습니다.
          </li>
          <li>
            그 밖의 요구는 <SupportServerLink /> 문의 채널이나 개인정보
            보호책임자 이메일(
            <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a>)로 할 수
            있으며, 제공자는 요구를 받은 날부터 10일 이내에 처리 결과를
            알립니다.
          </li>
          <li>
            법정대리인이나 위임을 받은 사람을 통해서도 권리를 행사할 수
            있습니다.
          </li>
          <li>
            법령에서 보관하도록 정한 정보(유료 서비스 결제 정보 등)는 보관
            기간이 끝나기 전까지 삭제를 요구할 수 없습니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection
        id="destruction"
        index={5}
        title="개인정보 파기 절차 및 방법"
      >
        <p>
          제공자는 보유기간이 끝났거나 처리 목적을 이룬 개인정보를 지체 없이
          파기합니다. 전자 파일 형태의 정보는 복구할 수 없는 방법으로
          삭제합니다.
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div className="bg-secondary/30 p-4 rounded-lg border border-border/50">
            <h4 className="font-semibold mb-2 text-sm text-primary">
              알림 정보
            </h4>
            <p className="text-sm text-muted-foreground">
              이용자가 대시보드나 명령어로 알림 설정을 삭제하거나, 봇이 서버에서
              추방되어 알림을 보낼 수 없게 되면 해당 정보를 즉시 영구
              삭제합니다.
            </p>
          </div>
          <div className="bg-secondary/30 p-4 rounded-lg border border-border/50">
            <h4 className="font-semibold mb-2 text-sm text-primary">
              유료 서비스 결제 정보
            </h4>
            <p className="text-sm text-muted-foreground">
              법령에 따라 결제일로부터 5년간 보관한 뒤 삭제합니다. 보관하는
              동안에는 법령에서 정한 목적 외에는 이용하지 않습니다.
            </p>
          </div>
          <div className="bg-secondary/30 p-4 rounded-lg border border-border/50 md:col-span-2">
            <h4 className="font-semibold mb-2 text-sm text-primary">
              저장하지 않는 정보
            </h4>
            <p className="text-sm text-muted-foreground">
              대시보드에서 불러온 이용자 정보와 서버 목록은 화면 표시와 권한
              확인에만 쓰고 따로 저장하지 않으므로, 로그아웃하면 더 이상
              처리하지 않습니다.
            </p>
          </div>
        </div>
      </PolicySection>

      <PolicySection
        id="security"
        index={6}
        title="개인정보의 안전성 확보 조치"
      >
        <ul>
          <li>
            서비스와 주고받는 모든 데이터는 HTTPS로 암호화하여 전송합니다.
          </li>
          <li>
            개인정보가 저장된 데이터베이스와 서버는 제공자만 접근할 수 있으며,
            각 기능에는 필요한 최소한의 접근 권한만 부여합니다.
          </li>
          <li>
            대시보드의 모든 서버 설정 요청은 디스코드에서 관리자 권한을 확인한
            뒤에만 처리합니다.
          </li>
          <li>서비스 로그는 14일이 지나면 자동으로 삭제됩니다.</li>
        </ul>
      </PolicySection>

      <PolicySection
        id="cookie"
        index={7}
        title="자동 수집 장치의 설치, 운영 및 거부"
      >
        <p>
          제공자는 로그인 유지와 방문 통계 분석을 위해 쿠키를 사용합니다.
          사용하는 쿠키의 종류와 목적은{" "}
          <Link href={routeMap.COOKIE_POLICY}>쿠키 정책</Link>에서 확인할 수
          있습니다.
        </p>
        <ul>
          <li>
            브라우저 설정에서 쿠키 저장을 거부하거나 저장된 쿠키를 삭제할 수
            있습니다. 다만 로그인 쿠키를 거부하면 대시보드를 이용할 수 없습니다.
          </li>
          <li>
            방문 통계 수집만 거부하려면{" "}
            <a
              href="https://tools.google.com/dlpage/gaoptout"
              target="_blank"
              rel="noopener noreferrer"
            >
              Google Analytics 차단 브라우저 부가기능
            </a>
            을 설치하세요.
          </li>
        </ul>
      </PolicySection>

      <PolicySection id="cpo" index={8} title="개인정보 보호책임자 및 연락처">
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
                <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a>
              </dd>
            </div>
          </dl>
        </div>
      </PolicySection>

      <PolicySection id="remedy" index={9} title="권익침해 구제방법">
        <p>
          개인정보 침해에 대한 신고나 상담이 필요하면 아래 기관에 문의할 수
          있습니다.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {REMEDY_AGENCIES.map((agency) => (
            <PolicyExternalLink key={agency.title} {...agency} />
          ))}
        </div>
      </PolicySection>

      <PolicySection id="changes" index={10} title="개인정보 처리방침의 변경">
        <ol>
          <li>
            이 처리방침을 변경하는 경우, 제공자는 변경 내용과 시행일을{" "}
            <SupportServerLink /> 또는 치직 대시보드에 시행일 7일 전부터
            공지합니다. 처리하는 개인정보 항목이 늘어나는 등 이용자에게 중요한
            변경은 시행일 30일 전부터 공지합니다.
          </li>
          <li>이 처리방침은 2026년 11월 9일부터 시행합니다.</li>
          <li>이전 처리방침: 2025년 3월 8일 시행</li>
        </ol>
      </PolicySection>
    </PolicyLayout>
  );
}
