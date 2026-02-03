import { DocsContainer } from "@/components/docs/docs-ui";
import { PolicyCallout } from "@/components/policy";
import routeMap from "@/constants/route-map";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "문제 해결 - 치직 문서",
};

export default function TroubleshootingPage() {
  return (
    <DocsContainer title="4. 문제 해결 (FAQ)">
      <PolicyCallout variant="info" className="my-0">
        알림 추가나 전송 과정에서 자주 발생하는 오류 메시지와 해결 방법입니다.
      </PolicyCallout>
      <h2>자주 발생하는 오류</h2>
      <PolicyCallout
        variant="warning"
        title="400 해당 치지직의 채널을 찿을수 없습니다."
      >
        <ul className="mb-0">
          <li>치지직 ID를 잘못 입력했을 가능성이 큽니다.</li>
          <li>
            채널 URL의 맨 뒷부분이 정확한지 확인해주세요. 닉네임이 아니라
            영문/숫자로 된 고유 ID여야 합니다.
          </li>
          <li>한번도 방송을 키지 않는 채널은 등록할 수 없습니다.</li>
          <li>
            너무 오래 전에 방송을 켰던 채널은 치지직에서 채널 정보를 가져올 수
            없어 등록이 불가능할 수 있습니다.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="500 테스트 알림 전송에 실패했습니다. 치직 봇이 해당 채널에 메시지를 보낼 권한이 있는지 확인해주세요."
      >
        <ul>
          <li>
            <a href={routeMap.DOCS.INSTALLATION}>시작하기 문서</a>의 디스코드
            채널 권한 설정 부분을 참고하여, 치직 봇에게 충분한 권한이 있는지
            확인해주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="400 이미 해당 디스코드 채널에 등록된 치지직 채널입니다."
      >
        <ul className="mb-0">
          <li>
            한 디스코드 채널에 동일한 치지직 방송 알림을 중복해서 등록할 수
            없습니다.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="500 치지직 채널 팔로우에 실패했습니다."
      >
        <ul>
          <li>일시적인 서버 오류일 수 있습니다. 잠시 후 다시 시도해주세요.</li>
          <li>
            해당 치지직 채널에서 치직 봇을 차단하진 않았는지 한번 확인해주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="404 해당 디스코드 채널이 존재하지 않습니다."
      >
        <ul>
          <li>
            디스코드 채널이 삭제되었거나, 치직 봇이 해당 서버에서 추방당했을 수
            있습니다.
          </li>
        </ul>
      </PolicyCallout>
      <h2>문의하기</h2>
      <PolicyCallout variant="info" className="my-0">
        위 방법으로 해결되지 않는다면{" "}
        <a href={routeMap.REDIRECTS.SUPPORT_SERVER} target="_blank">
          서포트 서버
        </a>
        에 방문하여 문의해주세요.
      </PolicyCallout>
    </DocsContainer>
  );
}
