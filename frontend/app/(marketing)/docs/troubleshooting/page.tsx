import { DocsContainer } from "@/components/docs/docs-ui";
import { PolicyCallout } from "@/components/policy";
import routeMap from "@/constants/route-map";
import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "문제 해결 - 치직 문서",
};

export default function TroubleshootingPage() {
  return (
    <DocsContainer title="4. 문제 해결 (FAQ)">
      <PolicyCallout variant="info" className="my-0">
        알림 추가나 전송 과정에서 자주 발생하는 오류 메시지와 해결 방법입니다.
      </PolicyCallout>
      <h2>알림 등록 시 발생하는 오류</h2>
      <PolicyCallout
        variant="warning"
        title="400 해당 치지직 채널을 찾을 수 없습니다."
      >
        <ul className="mb-0">
          <li>
            치지직 ID를 잘못 입력했을 가능성이 큽니다. 채널 URL의 맨 뒷부분이
            정확한지 확인해주세요. 닉네임이 아니라{" "}
            <strong>영문/숫자로 된 고유 ID</strong>여야 합니다.
          </li>
          <li>한 번도 방송을 켜지 않은 채널은 등록할 수 없습니다.</li>
          <li>
            너무 오래 전에 방송을 켰던 채널은 치지직에서 채널 정보를 가져올 수
            없어 등록이 불가능할 수 있습니다.
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
          <li>
            설정을 바꾸고 싶다면 기존 알림의 <strong>수정</strong> 버튼을
            이용해주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout variant="warning" title="400 알림 등록 제한을 초과했습니다.">
        <ul className="mb-0">
          <li>
            서버에서 사용할 수 있는 슬롯을 모두 사용한 경우입니다. (무료 플랜
            기준 5개)
          </li>
          <li>
            사용하지 않는 알림을 삭제하거나,{" "}
            <Link href={routeMap.PRICING}>요금제</Link>를 확인해 슬롯을
            늘려주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="400 서비스 내부 계정이 해당 치지직 채널에서 차단되어 알림을 설정할 수 없습니다."
      >
        <ul className="mb-0">
          <li>
            치직은 내부 네이버 계정으로 치지직 채널을 팔로우하여 방송 여부를
            확인합니다. 이 계정이 해당 채널에서 활동 제한(차단)을 당하면 알림을
            등록할 수 없습니다.
          </li>
          <li>채널 관리자(스트리머/매니저)에게 차단 해제를 요청해주세요.</li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="500 치지직 채널 팔로우에 실패했습니다."
      >
        <ul className="mb-0">
          <li>일시적인 서버 오류일 수 있습니다. 잠시 후 다시 시도해주세요.</li>
          <li>
            계속 실패한다면 오류 메시지 끝의 번호(예: <code>(2)</code>)와 함께
            서포트 서버로 문의해주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="400 커스텀 웹훅(또는 커스텀 임베드 색상)은 활성 월간 정기 구독 서버에서만 사용할 수 있습니다."
      >
        <ul className="mb-0">
          <li>
            <Link href={routeMap.DOCS.CUSTOM_WEBHOOK}>커스텀 웹훅</Link>과
            임베드 색상은 구독자 전용 기능입니다. 서버의 정기 구독이 활성화되어
            있는지 확인해주세요.
          </li>
          <li>
            웹훅 URL은 <code>https://discord.com/api/webhooks/...</code>{" "}
            형식이어야 하며, 임베드 색상은 <code>#RRGGBB</code> 형식으로
            입력해주세요.
          </li>
        </ul>
      </PolicyCallout>
      <h2>알림 전송 관련 오류</h2>
      <PolicyCallout
        variant="warning"
        title="500 테스트 알림 전송에 실패했습니다. 치직 봇이 해당 채널에 메시지를 보낼 권한이 있는지 확인해주세요."
      >
        <ul className="mb-0">
          <li>
            <Link href={routeMap.DOCS.INSTALLATION}>시작하기 문서</Link>의
            디스코드 채널 권한 설정 부분을 참고하여,{" "}
            <strong>채널 보기 / 메시지 보내기 / 링크 첨부</strong> 권한을
            허용했는지 확인해주세요.
          </li>
          <li>
            커스텀 웹훅을 사용 중이라면, 웹훅이 삭제되지 않았는지와 URL이
            올바른지 확인해주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="404 해당 디스코드 채널이 존재하지 않습니다."
      >
        <ul className="mb-0">
          <li>
            디스코드 채널이 삭제되었거나, 치직 봇이 해당 서버에서 추방된
            경우입니다.
          </li>
          <li>봇을 다시 초대하거나, 알림을 받을 채널을 다시 설정해주세요.</li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="방송을 켰는데 알림이 늦게 오거나 오지 않아요."
      >
        <ul className="mb-0">
          <li>
            방송 상태는 약 5분 간격으로 확인하기 때문에, 방송 시작 후 알림까지
            최대 5분 정도 걸릴 수 있습니다.
          </li>
          <li>
            방송을 켰다가 다음 확인 시점이 오기 전에 꺼버리면, 봇은 그 방송을
            감지하지 못해 <strong>알림이 전송되지 않습니다.</strong> 방송 테스트
            등으로 잠깐 켰다 끈 경우에는 알림이 가지 않을 수 있습니다.
          </li>
          <li>
            대시보드에서 <strong>테스트 알림</strong>을 보내 권한과 채널 설정이
            올바른지 먼저 확인해주세요.
          </li>
        </ul>
      </PolicyCallout>
      <h2>문의하기</h2>
      <PolicyCallout variant="info" className="my-0">
        위 방법으로 해결되지 않는다면{" "}
        <Link href={routeMap.REDIRECTS.SUPPORT_SERVER} target="_blank">
          서포트 서버
        </Link>
        에 방문하여 문의해주세요.
      </PolicyCallout>
    </DocsContainer>
  );
}
