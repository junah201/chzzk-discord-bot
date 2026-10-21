import { DocsContainer } from "@/components/docs/docs-ui";
import { PolicyCallout } from "@/components/policy";
import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "커스텀 웹훅 사용법 - 치직 문서",
};

export default function CustomWebhookPage() {
  return (
    <DocsContainer title="커스텀 웹훅 사용법 (브랜딩 알림)">
      <PolicyCallout className="my-0">
        디스코드 채널마다 개별 웹훅을 연동하여 알림을 보낼 수 있습니다. 특히
        커스텀 웹훅을 사용하면 <strong>치직 봇 기본 이름과 프로필</strong> 대신,
        원하는 <strong>유저명과 프로필 이미지</strong>로 알림을 꾸며 서버의
        브랜드와 아이덴티티를 극대화할 수 있습니다.
      </PolicyCallout>
      <h2>시작하기 전에 (웹훅 생성)</h2>
      <p>
        디스코드 채널에 알림을 보낼 웹훅 URL이 먼저 필요합니다. 이미
        생성하셨다면 다음 단계로 넘어가세요.
      </p>
      <ul>
        <li>
          방법을 모르신다면{" "}
          <a
            href="https://support.discord.com/hc/ko/articles/228383668-%EC%9B%B9%ED%9B%84%ED%81%AC-%EC%86%8C%EA%B0%9C"
            target="_blank"
            rel="noreferrer"
            className="text-primary hover:underline font-medium"
          >
            디스코드 공식 웹훅 가이드
          </a>
          를 참고하여 웹훅을 생성하고 URL을 복사해 주세요.
        </li>
      </ul>

      {/* 설정 단계 */}
      <h2>대시보드에서 웹훅 연동하기</h2>
      <ol>
        <li>
          <Link
            href="https://chzzk.junah.dev"
            className="text-primary hover:underline font-medium"
          >
            치직 대시보드
          </Link>
          에 방문하여 로그인합니다.
        </li>
        <li>
          알림을 설정할 <strong>서버</strong>로 이동합니다.
        </li>
        <li>
          알림을 새로 설정하실 경우, `커스텀 웹훅 URL`에 복사한 웹훅 URL을
          붙여넣고, 기존 알림을 수정하실 경우, 해당 알림의 <strong>수정</strong>{" "}
          버튼을 클릭하고, 동일하게 `커스텀 웹훅 URL`에 복사한 웹훅 URL을
          붙여넣습니다.
        </li>
        <li>
          페이지 하단의 <strong>알림 추가</strong> (기존 수정 시{" "}
          <strong>변경사항 저장</strong>) 버튼을 누르면 설정이 완료됩니다!
        </li>
      </ol>

      <PolicyCallout>
        <p>
          커스텀 웹훅 기능은 월 정기 구독 중인 서버에서 채널별로 자유롭게
          설정하여 이용할 수 있습니다. 구독이 만료되거나 해지될 경우, 웹훅
          데이터는 안전하게 보존되나 일시적으로 기본 봇 알림 방식으로
          전환됩니다.
        </p>
      </PolicyCallout>
    </DocsContainer>
  );
}
