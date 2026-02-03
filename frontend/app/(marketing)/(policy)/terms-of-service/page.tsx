import { PolicyLayout, PolicySection } from "@/components/policy";
import { Metadata } from "next";

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

export default function TermsOfService() {
  const sections = [
    { id: "purpose", title: "목적" },
    { id: "definition", title: "용어의 정의" },
    { id: "agreement", title: "약관의 효력 및 변경" },
    { id: "rights-duties", title: "권리와 의무" },
    { id: "service-interruption", title: "서비스 제공 및 중단" },
    { id: "liability", title: "책임 제한 및 면책" },
  ];

  const notice = {
    title: "치직 서비스 이용약관",
    description:
      "본 약관은 @junah201이 제공하는 치직 서비스 이용과 관련하여 회사와 이용자 간의 권리, 의무 및 책임사항을 규정합니다.",
  };

  return (
    <PolicyLayout
      title="서비스 이용약관"
      lastUpdated="2026년 02월 03일"
      notice={notice}
      sections={sections}
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
        <ul>
          <li>
            <strong>서비스:</strong> ‘치직’ 봇, 대시보드 웹사이트 등 제공자가
            제공하는 모든 형태의 서비스를 의미합니다.
          </li>
          <li>
            <strong>이용자:</strong> 본 약관에 따라 ‘서비스’를 이용하는 모든
            디스코드 서버 관리자 및 구성원을 의미합니다.
          </li>
          <li>
            <strong>치직(Chzzk):</strong> 이용자의 디스코드 서버 내에서 알림 및
            편의 기능을 제공하는 자동화된 봇(Bot) 프로그램을 의미합니다.
          </li>
          <li>
            <strong>치직 대시보드:</strong>{" "}
            <a
              href="https://chzzk.junah.dev"
              className="text-primary hover:underline"
              target="_blank"
              rel="noreferrer"
            >
              https://chzzk.junah.dev
            </a>{" "}
            도메인을 통해 서비스 설정 및 관리를 지원하는 웹사이트를 의미합니다.
          </li>
        </ul>
      </PolicySection>

      <PolicySection id="agreement" index={3} title="약관의 효력 및 변경">
        <ol>
          <li>
            이용자가 서비스를 이용하는 경우, 본 약관에 동의한 것으로 간주합니다.
          </li>
          <li>
            제공자는 필요한 경우 관련 법령을 위배하지 않는 범위 내에서 본 약관을
            개정할 수 있습니다.
          </li>
          <li>
            약관이 변경될 경우, 제공자는 변경 사항을{" "}
            <strong>‘치직 서포트 서버’</strong>
            또는 대시보드를 통해 최소 7일 전에 공지합니다.
          </li>
          <li>
            변경된 약관의 효력 발생일 이후에도 서비스를 계속 이용할 경우, 약관
            변경에 동의한 것으로 간주합니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="rights-duties" index={4} title="권리와 의무">
        <ol>
          <li>
            이용자는 본 약관 및 관련 법령을 준수해야 하며, 서비스의 정상적인
            운영을 방해하는 행위를 해서는 안 됩니다.
          </li>
          <li>
            다음 각 호의 행위는 엄격히 금지되며, 적발 시 사전 통보 없이 서비스
            이용이 영구적으로 제한될 수 있습니다.
            <ul>
              <li>
                서비스를 이용하여 불법적인 정보를 유통하거나 범죄에 악용하는
                행위
              </li>
              <li>제공자의 승인 없이 서비스를 상업적으로 이용하는 행위</li>
              <li>
                서비스의 버그나 취약점을 악용하여 이득을 취하거나 시스템을
                공격하는 행위
              </li>
            </ul>
          </li>
          <li>
            서비스의 오류 또는 보안 취약점을 발견한 경우, 이용자는 즉시 ‘치직
            서포트 서버’를 통해 제보해야 합니다. 이를 악용하거나 방치하여 발생한
            문제에 대한 책임은 이용자에게 있습니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection
        id="service-interruption"
        index={5}
        title="서비스 제공 및 중단"
      >
        <ol>
          <li>
            제공자는 연중무휴 1일 24시간 서비스 제공을 원칙으로 하되, 다음의
            경우 서비스의 전부 또는 일부를 중단할 수 있습니다.
            <ul>
              <li>시스템 정기 점검, 증설 및 교체가 필요한 경우</li>
              <li>
                디스코드(Discord) 또는 치직(Chzzk/Naver) 플랫폼의 API 변경,
                장애, 정책 변경이 발생한 경우
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
            제공자는 서비스 중단으로 인해 이용자에게 발생하는 손해에 대해 고의
            또는 중대한 과실이 없는 한 책임을 지지 않습니다.
          </li>
        </ol>
      </PolicySection>

      <PolicySection id="liability" index={6} title="책임 제한 및 면책">
        <p>
          본 서비스는 <strong>“있는 그대로(As-Is)”</strong> 제공되며, 제공자는
          다음 사항에 대해 책임을 지지 않습니다.
        </p>
        <ol>
          <li>
            제공자는 무료로 제공되는 서비스 이용과 관련하여 관련 법령에 특별한
            규정이 없는 한 어떠한 책임도 지지 않습니다.
          </li>
          <li>
            제공자는 이용자의 귀책사유로 인한 서비스 이용의 장애 또는 데이터
            손실에 대해 책임을 지지 않습니다.
          </li>
          <li>
            제공자는 이용자가 서비스를 이용하여 기대하는 수익을 상실하거나,
            서비스를 통해 얻은 자료로 인한 손해에 대해 책임을 지지 않습니다.
          </li>
          <li>
            제공자는 이용자 상호 간 또는 이용자와 제3자 간에 서비스를 매개로
            발생한 분쟁에 대해 개입할 의무가 없으며, 이로 인한 손해를 배상할
            책임도 없습니다.
          </li>
        </ol>
      </PolicySection>
    </PolicyLayout>
  );
}
