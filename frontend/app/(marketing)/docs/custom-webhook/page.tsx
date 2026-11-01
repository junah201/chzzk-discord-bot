import { DocsContainer } from "@/components/docs/docs-ui";
import { PolicyCallout } from "@/components/policy";
import routeMap from "@/constants/route-map";
import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "커스텀 웹훅 사용법 - 치직 문서",
};

export default function CustomWebhookPage() {
  return (
    <DocsContainer title="5. 커스텀 웹훅 사용하기">
      <PolicyCallout className="my-0">
        알림마다 디스코드 웹훅을 연결해 보낼 수 있습니다. 커스텀 웹훅을 쓰면{" "}
        <strong>치직 봇의 이름과 프로필</strong> 대신, 웹훅에 설정한{" "}
        <strong>이름과 프로필 이미지</strong>로 알림이 옵니다. 월 정기 구독
        중인 서버에서만 쓸 수 있습니다.
      </PolicyCallout>
      <h2>시작하기 전에 (웹훅 생성)</h2>
      <p>
        알림을 보낼 디스코드 채널의 웹훅 URL이 먼저 필요합니다. 이미 만들었다면
        다음 단계로 넘어가세요.
      </p>
      <ul>
        <li>
          만드는 방법은{" "}
          <a
            href="https://support.discord.com/hc/ko/articles/228383668-%EC%9B%B9%ED%9B%84%ED%81%AC-%EC%86%8C%EA%B0%9C"
            target="_blank"
            rel="noreferrer"
            className="text-primary hover:underline font-medium"
          >
            디스코드 공식 웹훅 가이드
          </a>
          를 참고해 주세요. 웹훅을 만든 뒤 URL을 복사해 둡니다.
        </li>
      </ul>

      {/* 설정 단계 */}
      <h2>대시보드에서 웹훅 연동하기</h2>
      <ol>
        <li>
          <Link
            href={routeMap.DASHBOARD.HOME}
            className="text-primary hover:underline font-medium"
          >
            치직 대시보드
          </Link>
          에 로그인합니다.
        </li>
        <li>
          <strong>내 서버</strong> 목록에서 알림을 설정할 서버를 누릅니다.
        </li>
        <li>
          <strong>커스텀 웹훅 URL</strong> 칸에 복사한 URL을 붙여 넣습니다.
          <ul>
            <li>새 알림: 알림 추가 폼에서 입력합니다.</li>
            <li>
              기존 알림: 알림 목록에서 <strong>수정</strong>을 누른 뒤
              입력합니다.
            </li>
          </ul>
        </li>
        <li>
          <strong>알림 추가</strong>(기존 알림은{" "}
          <strong>변경사항 저장</strong>) 버튼을 누르면 끝납니다. 미리보기에서
          이름과 프로필 자리가 웹훅 설정으로 바뀐 것을 확인할 수 있습니다.
        </li>
      </ol>

      <PolicyCallout>
        <p>
          구독이 만료되거나 해지되면 알림은 다시 치직 봇 이름으로 전송됩니다.
          입력한 웹훅 URL은 그대로 남아 있어서, 다시 구독하면 웹훅으로
          전송됩니다.
        </p>
      </PolicyCallout>
    </DocsContainer>
  );
}
