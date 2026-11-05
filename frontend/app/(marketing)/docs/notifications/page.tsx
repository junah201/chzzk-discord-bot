import { DocsContainer } from "@/components/docs/docs-ui";
import { PolicyCallout } from "@/components/policy";
import routeMap from "@/constants/route-map";
import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "알림 등록하기 - 치직 문서",
};

export default function NotificationsPage() {
  return (
    <DocsContainer title="2. 알림 등록하기">
      <h2>대시보드에서 알림 추가</h2>
      <ol>
        <li>
          <Link href={routeMap.DASHBOARD.HOME} target="_blank">
            치직 대시보드
          </Link>
          에 디스코드 계정으로 로그인합니다.
        </li>
        <li>
          <strong>내 서버</strong> 목록에서 알림을 등록할 서버를 누릅니다.
          서버가 많다면 검색창에 서버 이름을 입력해 찾을 수 있습니다.
        </li>
        <PolicyCallout variant="warning" title="서버가 보이지 않나요?">
          대시보드에는 내가 관리자 권한을 가진 서버만 나옵니다. 디스코드에서
          해당 서버의 관리자 권한이 있는지 확인해 주세요.
        </PolicyCallout>
        <li>
          <strong>치지직 ID</strong>를 입력하고, 알림을 받을{" "}
          <strong>디스코드 채널</strong>을 고릅니다. 오른쪽(좁은 화면에서는
          아래쪽) 미리보기에서 알림이 어떻게 보일지 바로 확인할 수 있습니다.
        </li>
        <PolicyCallout variant="info" title="치지직 ID는 어디서 찾나요?">
          <p className="mb-2">
            치지직 채널 페이지 주소의 <strong>마지막 부분</strong>이 고유
            ID입니다.
          </p>
          <div className="bg-secondary p-3 rounded-md font-mono text-xs break-all border border-border">
            https://chzzk.naver.com/
            <span className="text-primary font-bold">bb382c2c0cc9fa7c86</span>
            <br />
            https://chzzk.naver.com/live/
            <span className="text-primary font-bold">bb382c2c0cc9fa7c86</span>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">
            위 예시라면 <code>bb382c2c0cc9fa7c86</code>을 복사해 붙여 넣으세요.
          </p>
        </PolicyCallout>
      </ol>

      <h2>테스트 및 확인</h2>
      <ol>
        <li>
          <strong>알림 추가</strong> 버튼을 눌러 저장합니다.
        </li>
        <PolicyCallout variant="warning" title="알림 추가에 실패했나요?">
          <Link href={routeMap.DOCS.TROUBLESHOOTING} target="_blank">
            문제 해결 가이드
          </Link>
          를 참고해주세요.
        </PolicyCallout>
        <li>
          아래 알림 목록에 새 알림이 생기면 <strong>테스트 알림 보내기</strong>
          를 누릅니다.
        </li>
        <li>
          디스코드 채널에{" "}
          <code>관리자의 요청에 따라 전송된 테스트 알림입니다.</code>라는
          메시지가 오면 설정이 끝난 것입니다.
        </li>
        <PolicyCallout variant="warning" title="메시지가 오지 않나요?">
          <Link href={routeMap.DOCS.TROUBLESHOOTING} target="_blank">
            문제 해결 가이드
          </Link>
          를 참고해주세요.
        </PolicyCallout>
      </ol>
    </DocsContainer>
  );
}
