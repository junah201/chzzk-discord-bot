import { DocsContainer } from "@/components/docs/docs-ui";
import { PolicyCallout } from "@/components/policy";
import routeMap from "@/constants/route-map";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "시작하기 - 치직 문서",
};

export default function InstallationPage() {
  return (
    <DocsContainer title="1. 시작하기 (봇 설치)">
      <PolicyCallout variant="info" className="my-0">
        치직 서비스를 이용하기 위해서는 먼저 디스코드 서버에 봇을 초대하고
        권한을 설정해야 합니다.
      </PolicyCallout>
      <h2>서버에 치직 봇 초대하기</h2>
      <ol>
        <li>
          <a href={routeMap.REDIRECTS.INVITE} target="_blank">
            봇 초대링크
          </a>
          를 클릭합니다.
        </li>
        <li>
          치직이 사용자의 이름과 서버를 볼 수 있도록 허용하는 Discord 창이 뜨면{" "}
          <strong>승인</strong>을 누릅니다.
        </li>
        <li>
          봇을 추가할 <strong>서버를 선택</strong>하고 계속하기를 누릅니다.
        </li>
        <li>
          필수 권한(채널 보기, 메시지 보내기 등)을 확인하고{" "}
          <strong>승인</strong>하면 초대가 완료됩니다.
        </li>
      </ol>

      <h2>디스코드 채널 권한 설정 (중요)</h2>
      <p>
        봇이 들어왔더라도, 알림을 보낼 특정 채널에{" "}
        <strong>권한이 없으면 알림을 보낼 수 없습니다.</strong>
      </p>
      <ol>
        <li>
          디스코드에서 알림을 받을 채널을 우클릭하고 <strong>채널 편집</strong>
          을 누릅니다.
        </li>
        <li>
          <strong>권한</strong> 탭으로 이동하여 [멤버 또는 역할 추가]에서{" "}
          <strong>치직</strong>을 추가합니다.
        </li>
        <li>
          다음 권한을 반드시 <strong>허용</strong>으로 체크해주세요.
          <ul>
            <li>채널 보기 / 메시지 보내기</li>
            <li>링크 첨부 / 파일 첨부</li>
            <li>외부 이모지 사용</li>
            <li>@everyone, @here, 모든 역할 멘션하기 (필요시)</li>
          </ul>
        </li>
      </ol>

      <PolicyCallout variant="success" title="준비 완료!" className="my-0">
        이제 봇이 알림을 보낼 준비가 되었습니다. 다음 단계에서 실제로 알림을
        등록해 보세요.
      </PolicyCallout>
    </DocsContainer>
  );
}
