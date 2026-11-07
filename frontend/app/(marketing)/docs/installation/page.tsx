import { DocsContainer } from "@/components/docs/docs-ui";
import { PolicyCallout } from "@/components/policy";
import routeMap from "@/constants/route-map";
import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "시작하기 - 치직 문서",
};

export default function InstallationPage() {
  return (
    <DocsContainer title="1. 시작하기 (봇 설치)">
      <PolicyCallout variant="info" className="my-0">
        치직을 쓰려면 먼저 디스코드 서버에 봇을 초대하고, 알림을 보낼 채널에
        권한을 주어야 합니다.
      </PolicyCallout>
      <h2>서버에 치직 봇 초대하기</h2>
      <ol>
        <li>
          <Link href={routeMap.REDIRECTS.INVITE} target="_blank">
            봇 초대 링크
          </Link>
          를 엽니다.
        </li>
        <li>
          봇을 추가할 <strong>서버를 선택</strong>하고 <strong>계속하기</strong>
          를 누릅니다. 관리자 권한이 있는 서버만 목록에 나옵니다.
        </li>
        <li>
          요청하는 권한(채널 보기, 메시지 보내기 등)을 확인하고{" "}
          <strong>승인</strong>을 누르면 초대가 끝납니다.
        </li>
      </ol>

      <h2 id="channel-permissions" className="scroll-mt-32">
        디스코드 채널 권한 설정 (중요)
      </h2>
      <p>
        봇이 서버에 들어와 있어도, 알림을 보낼 채널에{" "}
        <strong>권한이 없으면 알림을 보낼 수 없습니다.</strong> 비공개 채널이나
        권한을 따로 설정한 채널이라면 아래 설정을 꼭 확인해 주세요.
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
          다음 권한을 <strong>허용</strong>으로 바꿉니다.
          <ul>
            <li>채널 보기 / 메시지 보내기</li>
            <li>링크 첨부 / 파일 첨부</li>
            <li>외부 이모지 사용</li>
            <li>@everyone, @here, 모든 역할 멘션하기 (멘션을 쓸 때만)</li>
          </ul>
        </li>
      </ol>

      <PolicyCallout variant="success" title="준비 완료!" className="my-0">
        이제 봇이 알림을 보낼 수 있습니다. 다음 단계에서{" "}
        <Link href={routeMap.DOCS.NOTIFICATIONS}>알림을 등록</Link>해 보세요.
      </PolicyCallout>
    </DocsContainer>
  );
}
