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
          <Link href={routeMap.HOME} target="_blank">
            치직 대시보드
          </Link>
          에 접속하여 디스코드 계정으로 로그인합니다.
        </li>
        <li>관리자 권한이 있는 서버를 선택합니다.</li>
        <PolicyCallout variant="warning" title="서버가 보이지 않나요?">
          봇이 해당 서버에 초대되어 있는지, 관리자 권한이 있는지 확인해주세요.
        </PolicyCallout>
        <li>
          <strong>치지직 ID</strong>와 <strong>디스코드 채널</strong>을
          입력합니다.
        </li>
        <PolicyCallout variant="info" title="치지직 ID는 어디서 찾나요?">
          <p className="mb-2">
            치지직 채널 페이지 URL의 <strong>마지막 부분</strong>이 고유
            ID입니다.
          </p>
          <div className="bg-secondary p-3 rounded-md font-mono text-xs break-all border border-border">
            https://chzzk.naver.com/
            <span className="text-primary font-bold">bb382c2c0cc9fa7c86</span>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">
            위 예시에서는 <code>bb382c2c0cc9fa7c86</code> 복사해서 붙여넣으세요.
          </p>
        </PolicyCallout>
      </ol>

      <h2>테스트 및 확인</h2>
      <ol>
        <li>
          <strong>[추가하기]</strong> 버튼을 눌러 설정을 저장합니다.
        </li>
        <PolicyCallout variant="warning" title="알림 추가에 실패했나요?">
          <Link href={routeMap.DOCS.TROUBLESHOOTING} target="_blank">
            문제 해결 가이드
          </Link>
          를 참고해주세요.
        </PolicyCallout>
        <li>
          알림 목록에 카드가 생기면 <strong>[테스트 전송]</strong> 버튼을
          눌러보세요.
        </li>
        <li>
          디스코드 채널에{" "}
          <code>관리자의 요청에 따라 전송된 테스트 알림입니다.</code>로 시작하는
          메시지가 오면 성공입니다!
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
