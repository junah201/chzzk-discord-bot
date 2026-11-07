import { DocsContainer } from "@/components/docs/docs-ui";
import { PolicyCallout } from "@/components/policy";
import routeMap from "@/constants/route-map";
import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "공지 채널 자동 게시 - 치직 문서",
};

export default function AutoCrosspostPage() {
  return (
    <DocsContainer title="6. 공지 채널 자동 게시">
      <PolicyCallout className="my-0">
        공지 채널에 올라온 메시지는 <strong>게시</strong>해야 그 채널을 팔로우한
        다른 서버에도 전달됩니다. 자동 게시를 켜면 치직이 방송 알림을 보낸 뒤
        바로 게시해 줍니다. 월 정기 구독 중인 서버에서만 쓸 수 있습니다.
      </PolicyCallout>

      <h2>시작하기 전에</h2>
      <ul>
        <li>
          알림을 보낼 채널이 <strong>공지 채널</strong>이어야 합니다. 일반
          텍스트 채널은 디스코드 채널 설정의 <strong>개요</strong>에서{" "}
          <strong>공지 채널</strong>로 바꿀 수 있습니다. 서버에 커뮤니티 기능이
          켜져 있어야 합니다.
        </li>
        <li>
          치직 봇으로 보내는 알림은{" "}
          <Link href={`${routeMap.DOCS.INSTALLATION}#channel-permissions`}>
            기본 채널 권한
          </Link>
          만 있으면 게시할 수 있습니다.
        </li>
        <li>
          <Link href={routeMap.DOCS.CUSTOM_WEBHOOK}>커스텀 웹훅</Link>으로
          보내는 알림은 치직 봇이 보낸 메시지가 아니라서, 게시하려면 치직 봇에게
          그 채널의 <strong>메시지 관리</strong> 권한이 추가로 필요합니다.
        </li>
      </ul>

      <h2>대시보드에서 켜기</h2>
      <ol>
        <li>
          <Link href={routeMap.DASHBOARD.HOME}>치직 대시보드</Link>에서 서버를
          고릅니다.
        </li>
        <li>
          새 알림은 알림 추가 폼에서, 기존 알림은 알림 목록의{" "}
          <strong>수정</strong>에서 <strong>공지 채널 자동 게시</strong>를
          체크합니다. 공지 채널이 아니면 체크할 수 없습니다.
        </li>
        <li>
          <strong>알림 추가</strong>(기존 알림은 <strong>변경사항 저장</strong>)
          를 누르면 다음 방송부터 자동으로 게시됩니다.
        </li>
      </ol>

      <PolicyCallout>
        <ul className="mb-0">
          <li>
            <strong>테스트 알림</strong>은 팔로우한 서버에 퍼지지 않도록
            게시하지 않습니다.
          </li>
          <li>
            게시에 실패해도 알림은 정상적으로 보낸 것으로 처리됩니다. 디스코드는
            채널마다 한 시간에 10번까지만 게시를 허용합니다.
          </li>
          <li>
            구독이 만료되거나 해지되면 게시하지 않고 알림만 보냅니다. 설정은
            그대로 남아 있어서, 다시 구독하면 다시 게시됩니다.
          </li>
        </ul>
      </PolicyCallout>
    </DocsContainer>
  );
}
