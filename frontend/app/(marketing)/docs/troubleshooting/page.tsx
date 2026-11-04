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
        알림을 등록하거나 보낼 때 자주 보이는 오류 메시지와 해결 방법입니다.
        화면에 뜬 메시지와 같은 제목을 찾아보세요.
      </PolicyCallout>
      <h2>알림 등록 시 발생하는 오류</h2>
      <PolicyCallout
        variant="warning"
        title="해당 치지직 채널을 찾을 수 없습니다."
      >
        <ul className="mb-0">
          <li>
            치지직 ID를 잘못 입력했을 가능성이 큽니다. 채널 주소의 맨 뒷부분이
            정확한지 확인해 주세요. 닉네임이 아니라{" "}
            <strong>영문/숫자로 된 고유 ID</strong>여야 합니다.
          </li>
          <li>한 번도 방송을 켜지 않은 채널은 등록할 수 없습니다.</li>
          <li>
            마지막 방송이 너무 오래된 채널은 치지직에서 정보를 가져오지 못해
            등록되지 않을 수 있습니다.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="이미 해당 디스코드 채널에 등록된 치지직 채널입니다."
      >
        <ul className="mb-0">
          <li>
            한 디스코드 채널에 동일한 치지직 방송 알림을 중복해서 등록할 수
            없습니다.
          </li>
          <li>
            설정을 바꾸려면 기존 알림의 <strong>수정</strong> 버튼을 눌러
            주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="봇이 해당 디스코드 채널에 접근할 권한이 없습니다."
      >
        <ul className="mb-0">
          <li>
            디스코드 채널이 삭제되었거나, 봇에게 그 채널의{" "}
            <strong>채널 보기 / 메시지 보내기</strong> 권한이 없는 경우입니다.
          </li>
          <li>
            <Link href={routeMap.DOCS.INSTALLATION}>시작하기 문서</Link>의
            채널 권한 설정을 확인하거나, 봇을 서버에 다시 초대해 주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout variant="warning" title="알림 등록 제한을 초과했습니다.">
        <ul className="mb-0">
          <li>
            서버의 알림 슬롯을 모두 쓴 경우입니다. 무료로는 5개까지 등록할 수
            있습니다.
          </li>
          <li>
            사용하지 않는 알림을 삭제하거나,{" "}
            <Link href={routeMap.PRICING}>요금제</Link>를 확인해 슬롯을 늘려
            주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="서비스 내부 계정이 해당 치지직 채널에서 차단되어 알림을 설정할 수 없습니다."
      >
        <ul className="mb-0">
          <li>
            치직은 내부 네이버 계정으로 치지직 채널을 팔로우해 방송 여부를
            확인합니다. 이 계정이 채널에서 활동 제한(차단)되면 알림을 등록할 수
            없습니다.
          </li>
          <li>채널 관리자(스트리머/매니저)에게 차단 해제를 요청해 주세요.</li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="현재 서비스 계정의 팔로우 한도가 초과되어 등록할 수 없습니다."
      >
        <ul className="mb-0">
          <li>
            방송 확인에 쓰는 내부 계정이 팔로우할 수 있는 채널 수를 모두 쓴
            경우입니다. 직접 해결할 수 있는 문제가 아닙니다.
          </li>
          <li>
            오류 메시지 끝의 번호와 함께 서포트 서버로 알려 주시면 관리자가
            조치합니다.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="치지직 채널 팔로우 처리에 실패했습니다."
      >
        <ul className="mb-0">
          <li>일시적인 서버 오류일 수 있습니다. 잠시 후 다시 시도해 주세요.</li>
          <li>
            계속 실패하면 오류 메시지 끝의 번호(예: <code>(2)</code>)와 함께
            서포트 서버로 문의해 주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="커스텀 웹훅(커스텀 임베드 색상)은 활성 월간 정기 구독 서버에서만 사용할 수 있습니다."
      >
        <ul className="mb-0">
          <li>
            <Link href={routeMap.DOCS.CUSTOM_WEBHOOK}>커스텀 웹훅</Link>과
            임베드 색상은 구독자 전용 기능입니다. 서버의 정기 구독이 유지되고
            있는지 확인해 주세요.
          </li>
          <li>
            웹훅 URL은 <code>https://discord.com/api/webhooks/...</code>{" "}
            형식이어야 합니다. 임베드 색상은 색상 선택기에서 고르거나{" "}
            <code>5865F2</code>처럼 6자리 16진수 색상 코드로 입력해 주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="유효한 디스코드 웹훅 URL을 입력해주세요."
      >
        <ul className="mb-0">
          <li>
            디스코드 채널 설정의 <strong>연동 → 웹후크</strong>에서{" "}
            <strong>웹후크 URL 복사</strong>를 누르고, 복사한 URL을 그대로 붙여
            넣어 주세요.
          </li>
          <li>
            URL은 <code>https://discord.com/api/webhooks/</code>로 시작해야
            합니다. <code>ptb.discord.com</code>이나{" "}
            <code>canary.discord.com</code>으로 시작하면 그 부분을{" "}
            <code>discord.com</code>으로 바꿔 주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout variant="warning" title="디스코드 웹훅을 찾을 수 없습니다.">
        <ul className="mb-0">
          <li>
            웹훅이 삭제되었거나 URL이 일부만 복사된 경우입니다. 디스코드에서
            웹훅이 남아 있는지 확인하고, <strong>웹후크 URL 복사</strong>로
            다시 복사해 붙여 넣어 주세요.
          </li>
          <li>
            등록해 둔 웹훅을 디스코드에서 지웠다면 다른 설정을 바꿀 때도 이
            오류가 납니다. 새 웹훅 URL을 넣거나 웹훅 칸을 비운 뒤 저장해 주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout variant="warning" title="다른 디스코드 서버의 웹훅입니다.">
        <ul className="mb-0">
          <li>
            커스텀 웹훅은 <strong>알림을 등록하는 서버에서 만든 웹훅</strong>만
            쓸 수 있습니다.
          </li>
          <li>그 서버의 채널에서 웹훅을 새로 만들어 URL을 입력해 주세요.</li>
        </ul>
      </PolicyCallout>
      <h2>알림 전송 관련 오류</h2>
      <PolicyCallout
        variant="warning"
        title="테스트 알림 전송에 실패했습니다. 치직 봇이 해당 채널에 메시지를 보낼 권한이 있는지 확인해주세요."
      >
        <ul className="mb-0">
          <li>
            <Link href={routeMap.DOCS.INSTALLATION}>시작하기 문서</Link>의
            채널 권한 설정을 보고{" "}
            <strong>채널 보기 / 메시지 보내기 / 링크 첨부</strong> 권한이
            허용되어 있는지 확인해 주세요.
          </li>
          <li>
            커스텀 웹훅을 쓰고 있다면, 웹훅이 삭제되지 않았는지와 URL이
            올바른지 확인해 주세요.
          </li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="해당 디스코드 채널이 존재하지 않습니다."
      >
        <ul className="mb-0">
          <li>
            디스코드 채널이 삭제되었거나, 치직 봇이 해당 서버에서 추방된
            경우입니다.
          </li>
          <li>봇을 다시 초대하거나, 알림을 받을 채널을 다시 설정해 주세요.</li>
        </ul>
      </PolicyCallout>
      <PolicyCallout
        variant="warning"
        title="방송을 켰는데 알림이 늦게 오거나 오지 않아요."
      >
        <ul className="mb-0">
          <li>
            방송 상태를 약 5분마다 확인하기 때문에, 방송을 켜고 알림이 오기까지
            최대 5분 정도 걸릴 수 있습니다.
          </li>
          <li>
            다음 확인 시점이 오기 전에 방송을 끄면 봇이 그 방송을 감지하지 못해{" "}
            <strong>알림이 전송되지 않습니다.</strong> 방송 테스트처럼 잠깐
            켰다 끈 경우가 여기에 해당합니다.
          </li>
          <li>
            대시보드에서 <strong>테스트 알림</strong>을 보내 권한과 채널 설정이
            올바른지 먼저 확인해 주세요.
          </li>
        </ul>
      </PolicyCallout>
      <h2>문의하기</h2>
      <PolicyCallout variant="info" className="my-0">
        위 방법으로 해결되지 않는다면{" "}
        <Link href={routeMap.REDIRECTS.SUPPORT_SERVER} target="_blank">
          서포트 서버
        </Link>
        에서 문의해 주세요.
      </PolicyCallout>
    </DocsContainer>
  );
}
