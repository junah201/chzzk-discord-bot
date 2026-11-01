import { PolicyLayout, PolicySection } from "@/components/policy";
import routeMap from "@/constants/route-map";
import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "치직 - 서비스 이용약관",
  description: "치직 서비스 이용약관 페이지입니다.",
  openGraph: {
    title: "치직 - 서비스 이용약관",
    description: "치직 서비스 이용약관 페이지입니다.",
  },
  twitter: {
    title: "치직 - 서비스 이용약관",
    description: "치직 서비스 이용약관 페이지입니다.",
  },
};

const SECTIONS = [
  { id: "purpose", title: "목적" },
  { id: "definition", title: "용어의 정의" },
  { id: "agreement", title: "약관의 효력 및 변경" },
  { id: "service", title: "서비스의 제공" },
  { id: "provider-duties", title: "제공자의 의무" },
  { id: "user-duties", title: "이용자의 의무" },
  { id: "restriction", title: "이용 제한" },
  { id: "paid-service", title: "유료 서비스" },
  { id: "refund", title: "청약철회 및 환불" },
  { id: "service-interruption", title: "서비스의 중단 및 종료" },
  { id: "liability", title: "책임 제한" },
  { id: "dispute", title: "분쟁 해결" },
  { id: "addendum", title: "부칙" },
];

const NOTICE = {
  title: "치직 서비스 이용약관",
  description:
    "본 약관은 @junah201이 제공하는 치직 서비스 이용과 관련하여 제공자와 이용자 간의 권리, 의무 및 책임사항을 규정합니다.",
};

const SUPPORT_EMAIL = "junah.dev+chzzk@gmail.com";

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

export default function TermsOfService() {
  return (
    <PolicyLayout
      title="서비스 이용약관"
      lastUpdated="2026년 11월 2일"
      notice={NOTICE}
      sections={SECTIONS}
    >
      <PolicySection id="purpose" index={1} title="목적">
        <p>
          본 약관은 개발자 <strong>@junah201</strong>(이하 “제공자”)이 제공하는
          디스코드 봇 서비스 <strong>치직</strong> 및 관련 제반 서비스(이하
          “서비스”)의 이용과 관련하여 제공자와 이용자의 권리, 의무 및 책임사항,
          기타 필요한 사항을 규정함을 목적으로 합니다.
        </p>
      </PolicySection>

      <PolicySection id="definition" index={2} title="용어의 정의">
        <ol>
          <li>
            <strong>서비스:</strong> 치직 봇, 치직 대시보드 등 제공자가 제공하는
            모든 형태의 서비스를 의미합니다.
          </li>
          <li>
            <strong>치직:</strong> 이용자의 디스코드 서버에서 방송 알림 및 편의
            기능을 제공하는 자동화된 봇(Bot) 프로그램을 의미합니다.
          </li>
          <li>
            <strong>치직 대시보드:</strong>{" "}
            <Link
              href={routeMap.HOME}
              className="text-primary hover:underline"
              target="_blank"
            >
              https://chzzk.junah.dev
            </Link>{" "}
            도메인에서 서비스 설정 및 관리를 지원하는 웹사이트를 의미합니다.
          </li>
          <li>
            <strong>이용자:</strong> 본 약관에 따라 서비스를 이용하는 디스코드
            서버 관리자 및 구성원을 의미합니다.
          </li>
          <li>
            <strong>치지직(CHZZK):</strong> 네이버가 운영하는 스트리밍
            플랫폼으로, 서비스가 방송 정보를 확인하는 대상을 의미합니다.
          </li>
          <li>
            <strong>유료 서비스:</strong> 알림 슬롯 추가, 월 정기 구독 등
            이용자가 대금을 지불하고 이용하는 서비스를 의미합니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="agreement" index={3} title="약관의 효력 및 변경">
        <ol>
          <li>
            이용자가 치직을 디스코드 서버에 추가하거나 치직 대시보드에
            로그인하면 본 약관에 동의한 것으로 봅니다.
          </li>
          <li>
            제공자는 관련 법령을 위배하지 않는 범위에서 본 약관을 개정할 수
            있습니다.
          </li>
          <li>
            약관을 변경하는 경우, 제공자는 변경 내용과 시행일을{" "}
            <SupportServerLink /> 또는 치직 대시보드에 시행일 7일 전부터
            공지합니다. 다만 이용자에게 불리하거나 유료 서비스 조건에 관한
            변경은 시행일 30일 전부터 공지합니다.
          </li>
          <li>
            이용자는 변경된 약관에 동의하지 않으면 서비스 이용을 중단할 수
            있습니다. 변경된 약관의 시행일 이후에도 서비스를 계속 이용하면 약관
            변경에 동의한 것으로 봅니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="service" index={4} title="서비스의 제공">
        <ol>
          <li>
            서비스는 개인 개발자가 운영하는 비공식 서비스이며, 네이버(치지직)
            또는 디스코드(Discord)와 제휴하거나 그 승인을 받은 서비스가
            아닙니다.
          </li>
          <li>
            서비스는 치지직의 방송 상태를 주기적으로 확인하여 알림을 보냅니다.
            따라서 알림은 방송 시작 후 수 분 늦게 전송될 수 있으며, 외부
            플랫폼의 상황에 따라 전송되지 않을 수도 있습니다.
          </li>
          <li>
            이용자는 서비스를 이용할 때 본 약관과 함께 디스코드 및 치지직의
            이용약관과 정책을 지켜야 합니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="provider-duties" index={5} title="제공자의 의무">
        <ol>
          <li>
            제공자는 관련 법령과 본 약관을 지키며, 서비스를 안정적으로 제공하기
            위해 노력합니다.
          </li>
          <li>
            제공자는 이용자의 개인정보를{" "}
            <Link href={routeMap.PRIVACY_POLICY}>개인정보처리방침</Link>에 따라
            보호합니다. 이용자가 치직을 서버에서 내보내거나 이용을 중단할 때의
            정보 처리도 개인정보처리방침을 따릅니다.
          </li>
          <li>
            제공자는 이용자의 문의나 불만 사항이 정당하다고 인정되면 이를
            처리하기 위해 노력하며, 처리 결과를 <SupportServerLink /> 또는
            이메일로 알립니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="user-duties" index={6} title="이용자의 의무">
        <ol>
          <li>
            이용자는 본 약관과 관련 법령을 지켜야 하며, 서비스의 정상적인 운영을
            방해해서는 안 됩니다.
          </li>
          <li>
            이용자는 다음 행위를 해서는 안 됩니다.
            <ul>
              <li>
                서비스를 이용하여 불법적인 정보를 유통하거나 범죄에 악용하는
                행위
              </li>
              <li>
                제공자의 승인 없이 서비스를 재판매, 재배포하거나 유료로 중개하는
                행위
              </li>
              <li>
                서비스의 버그나 취약점을 악용하여 이득을 취하거나 시스템을
                공격하는 행위
              </li>
              <li>
                자동화된 수단으로 과도한 요청을 보내 서비스에 부하를 주는 행위
              </li>
              <li>
                권한이 없는 디스코드 서버의 설정을 변경하거나 다른 사람의 계정을
                도용하는 행위
              </li>
            </ul>
          </li>
          <li>
            서비스의 오류나 보안 취약점을 발견하면 <SupportServerLink />로 알려
            주세요. 취약점을 악용하여 발생한 손해는 해당 이용자가 책임집니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="restriction" index={7} title="이용 제한">
        <ol>
          <li>
            이용자가 제6조의 의무를 위반하면, 제공자는 위반의 정도에 따라 경고,
            일시 정지, 영구 이용 제한 등의 조치를 할 수 있습니다.
          </li>
          <li>
            제공자는 이용을 제한하기 전에 사유와 기간을 이용자에게 알립니다.
            다만 범죄 악용이나 시스템 공격처럼 즉시 조치가 필요한 경우에는
            제한한 후에 알릴 수 있습니다.
          </li>
          <li>
            이용 제한에 이의가 있는 이용자는 <SupportServerLink /> 또는 이메일(
            <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a>)로 이의를
            제기할 수 있으며, 제공자는 이의가 정당하다고 인정되면 즉시 제한을
            해제합니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="paid-service" index={8} title="유료 서비스">
        <ol>
          <li>
            유료 서비스의 종류와 가격은{" "}
            <Link href={routeMap.PRICING}>요금제</Link> 페이지에 안내합니다.
            <ul>
              <li>
                <strong>알림 슬롯 추가:</strong> 한 번 결제하면 해당 디스코드
                서버의 알림 슬롯이 늘어나며, 서비스가 운영되는 동안 유지됩니다.
              </li>
              <li>
                <strong>월 정기 구독:</strong> 결제한 날부터 1개월 동안 해당
                디스코드 서버에 슬롯 250개와 커스텀 웹훅, 임베드 색상 등 구독자
                전용 기능을 제공합니다.
              </li>
            </ul>
          </li>
          <li>
            유료 서비스는 계좌이체로 결제합니다. 이용자가 입금 후{" "}
            <SupportServerLink />에 알리면, 제공자가 입금을 확인한 뒤 유료
            서비스를 적용합니다.
          </li>
          <li>
            유료 서비스는 결제 시 지정한 디스코드 서버에만 적용되며, 다른 서버로
            옮길 수 없습니다.
          </li>
          <li>
            월 정기 구독은 자동으로 갱신되지 않습니다. 구독을 이어 가려면 만료
            전에 다시 결제해야 합니다.
          </li>
          <li>
            구독이 만료되면 구독자 전용 기능이 해제되어 커스텀 웹훅 알림은 치직
            봇 이름으로 전송됩니다. 슬롯 수보다 많은 알림이 등록되어 있으면
            초과한 알림을 정리하기 전까지 알림을 새로 등록하거나 수정할 수
            없습니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="refund" index={9} title="청약철회 및 환불">
        <ol>
          <li>
            이용자는 결제일로부터 7일 이내에 <SupportServerLink /> 또는 이메일로
            청약을 철회하고 전액 환불을 요청할 수 있습니다.
          </li>
          <li>
            다만 「전자상거래 등에서의 소비자보호에 관한 법률」 제17조 제2항에
            따라, 추가된 슬롯에 알림을 등록하거나 구독자 전용 기능을 사용하는 등
            유료 서비스의 제공이 시작된 경우에는 청약철회가 제한될 수 있습니다.
          </li>
          <li>
            제공자의 귀책사유로 유료 서비스를 정상적으로 이용하지 못한 경우,
            제공자는 이용하지 못한 기간만큼 구독 기간을 연장하거나 해당 금액을
            환불합니다.
          </li>
          <li>
            환불은 이용자가 입금에 사용한 계좌로, 환불이 확정된 날부터 3영업일
            이내에 진행합니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection
        id="service-interruption"
        index={10}
        title="서비스의 중단 및 종료"
      >
        <ol>
          <li>
            제공자는 연중무휴 1일 24시간 서비스 제공을 원칙으로 하되, 다음의
            경우 서비스의 전부 또는 일부를 일시적으로 중단할 수 있습니다.
            <ul>
              <li>시스템 정기 점검, 증설 및 교체가 필요한 경우</li>
              <li>
                디스코드 또는 치지직 플랫폼의 API 변경, 장애, 정책 변경이 발생한
                경우
              </li>
              <li>
                천재지변, 국가비상사태, 정전 등 불가항력적인 사유가 발생한 경우
              </li>
              <li>
                기타 제공자가 통제할 수 없는 기술적, 운영적 사유가 있는 경우
              </li>
            </ul>
          </li>
          <li>
            제공자는 서비스를 일시 중단할 경우 이를 미리 공지합니다. 다만 예측할
            수 없는 장애처럼 미리 알릴 수 없는 경우에는 사후에 공지합니다.
          </li>
          <li>
            제공자가 서비스를 완전히 종료하려면 종료일 30일 전까지{" "}
            <SupportServerLink /> 및 치직 대시보드에 공지합니다. 이때 남은 월
            정기 구독 기간에 해당하는 금액은 일할 계산하여 환불합니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="liability" index={11} title="책임 제한">
        <p>
          서비스는 <strong>“있는 그대로(As-Is)”</strong> 제공되며, 제공자는 고의
          또는 중대한 과실이 없는 한 다음 사항에 대해 책임을 지지 않습니다.
        </p>
        <ol>
          <li>
            제10조 제1항의 사유로 서비스가 중단되어 발생한 손해. 다만 유료
            서비스는 제9조 제3항에 따릅니다.
          </li>
          <li>알림이 늦게 전송되거나 전송되지 않아 발생한 손해</li>
          <li>이용자의 귀책사유로 인한 서비스 이용 장애 또는 데이터 손실</li>
          <li>
            이용자가 서비스를 이용하여 기대한 수익을 얻지 못하거나, 서비스를
            통해 얻은 자료로 인해 발생한 손해
          </li>
          <li>
            이용자 상호 간 또는 이용자와 제3자 간에 서비스를 매개로 발생한 분쟁.
            제공자는 이러한 분쟁에 개입할 의무가 없습니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="dispute" index={12} title="분쟁 해결">
        <ol>
          <li>
            서비스 이용과 관련한 문의는 <SupportServerLink /> 또는 이메일(
            <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a>)로 할 수
            있습니다.
          </li>
          <li>
            제공자와 이용자는 서비스와 관련하여 분쟁이 발생하면 원만하게
            해결하기 위해 성실히 협의합니다.
          </li>
          <li>
            본 약관은 대한민국 법률에 따라 해석되며, 협의로 해결되지 않은 분쟁은
            「민사소송법」에 따른 관할 법원에서 해결합니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="addendum" index={13} title="부칙">
        <p>본 약관은 2026년 11월 9일부터 시행합니다.</p>
      </PolicySection>
    </PolicyLayout>
  );
}
