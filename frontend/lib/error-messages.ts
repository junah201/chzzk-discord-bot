import { SUPPORT_SERVER_INVITE_URL } from "@/constants/links";
import routeMap from "@/constants/route-map";

export interface ApiErrorData {
  code?: string;
  message?: string;
  [key: string]: unknown;
}

export interface ErrorHelp {
  label: string;
  href: string;
  external?: boolean;
}

interface ErrorCopy {
  // undefined를 반환하면 백엔드 message로 대체된다.
  message: string | ((data: ApiErrorData) => string | undefined);
  help?: ErrorHelp;
}

const CHANNEL_PERMISSIONS_HELP: ErrorHelp = {
  label: "채널 권한 설정 가이드 보기",
  href: `${routeMap.DOCS.INSTALLATION}#channel-permissions`,
};

const CUSTOM_WEBHOOK_HELP: ErrorHelp = {
  label: "커스텀 웹훅 가이드 보기",
  href: routeMap.DOCS.CUSTOM_WEBHOOK,
};

const SUPPORT_SERVER_HELP: ErrorHelp = {
  label: "서포트 서버 바로가기",
  href: SUPPORT_SERVER_INVITE_URL,
  external: true,
};

const PRICING_HELP: ErrorHelp = {
  label: "요금제 보기",
  href: routeMap.PRICING,
};

function lines(...text: string[]) {
  return text.join("\n");
}

function withDiscordMessage(message: string) {
  return (data: ApiErrorData) =>
    typeof data.discord_message === "string"
      ? lines(message, `(디스코드 응답: ${data.discord_message})`)
      : message;
}

function slotCounts(data: ApiErrorData) {
  const { max_limit, current_count } = data;
  if (typeof max_limit !== "number" || typeof current_count !== "number") {
    return undefined;
  }
  return { max: max_limit, current: current_count };
}

export const ERROR_MESSAGES: Record<string, ErrorCopy> = {
  CHZZK_CHANNEL_NOT_FOUND: {
    message: lines(
      "입력한 ID로 치지직 채널을 찾지 못했습니다.",
      "• 채널 주소(chzzk.naver.com/…) 맨 끝의 영문·숫자 ID를 입력해 주세요. 닉네임은 쓸 수 없습니다.",
      "• 한 번도 방송하지 않은 채널은 등록할 수 없습니다.",
      "• 오래 방송하지 않은 채널은 방송을 한 번 켠 뒤 다시 등록해 주세요.",
    ),
    help: { label: "문제 해결 문서 보기", href: routeMap.DOCS.TROUBLESHOOTING },
  },
  CHZZK_CHANNEL_UNAVAILABLE: {
    message:
      "치지직에서 채널 정보를 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.",
  },
  TEST_NOTIFICATION_FAILED: {
    message: withDiscordMessage(
      lines(
        "치직 봇에게 이 채널의 메시지 보내기 권한이 없을 수 있습니다.",
        "아래 가이드를 따라 채널 권한을 확인한 뒤 다시 보내 주세요.",
      ),
    ),
    help: CHANNEL_PERMISSIONS_HELP,
  },
  TEST_NOTIFICATION_WEBHOOK_FAILED: {
    message: withDiscordMessage(
      lines(
        "등록한 커스텀 웹훅으로 보낼 수 없습니다.",
        "웹훅이 삭제됐거나 URL이 바뀌었을 수 있으니, 웹훅 URL을 다시 확인해 주세요.",
      ),
    ),
    help: CUSTOM_WEBHOOK_HELP,
  },
  BOT_CHANNEL_ACCESS_DENIED: {
    message: lines(
      "치직 봇이 이 채널에 접근할 수 없습니다.",
      "아래 가이드를 따라 채널 권한에 치직을 추가하고 필요한 권한을 허용한 뒤 다시 등록해 주세요.",
    ),
    help: CHANNEL_PERMISSIONS_HELP,
  },
  DISCORD_CHANNEL_GUILD_MISMATCH: {
    message: lines(
      "선택한 디스코드 채널이 이 서버의 채널이 아닙니다.",
      "페이지를 새로고침한 뒤 채널을 다시 선택해 주세요.",
    ),
  },
  CHZZK_CHANNEL_REGISTER_FAILED: {
    message: lines(
      "치지직 채널 정보를 저장하지 못했습니다. 잠시 후 다시 시도해 주세요.",
      "계속 실패하면 서포트 서버로 문의해 주세요.",
    ),
    help: SUPPORT_SERVER_HELP,
  },
  DISCORD_CHANNEL_NOT_FOUND: {
    message: lines(
      "알림을 보낼 디스코드 채널을 찾을 수 없습니다.",
      "채널이 삭제되었다면 이 알림을 삭제하고 다른 채널로 다시 등록해 주세요.",
    ),
  },
  NOTIFICATION_NOT_FOUND: {
    message: lines(
      "이 알림을 찾을 수 없습니다. 이미 삭제되었을 수 있습니다.",
      "페이지를 새로고침한 뒤 다시 시도해 주세요.",
    ),
  },
  NOTIFICATION_ALREADY_EXISTS: {
    message: lines(
      "이 디스코드 채널에는 같은 치지직 채널의 알림이 이미 있습니다.",
      "설정을 바꾸려면 알림 목록에서 기존 알림을 수정해 주세요.",
    ),
  },
  SERVICE_FOLLOW_LIMIT_REACHED: {
    message: (data) =>
      lines(
        "치직 서비스 계정의 팔로우 한도가 가득 차서 지금은 이 채널을 등록할 수 없습니다.",
        "서포트 서버로 문의해 주시면 관리자가 확인해 드리겠습니다." +
          (typeof data.account_index === "number"
            ? ` (계정 번호: ${data.account_index})`
            : ""),
      ),
    help: SUPPORT_SERVER_HELP,
  },
  NOTIFICATION_LIMIT_REACHED: {
    message: (data) => {
      const counts = slotCounts(data);
      if (!counts) return undefined;
      return lines(
        `알림 슬롯 ${counts.max}개를 모두 사용했습니다.`,
        "쓰지 않는 알림을 삭제하거나 슬롯을 늘린 뒤 다시 등록해 주세요.",
      );
    },
    help: PRICING_HELP,
  },
  NOTIFICATION_LIMIT_EXCEEDED: {
    message: (data) => {
      const counts = slotCounts(data);
      if (!counts) return undefined;
      const over = counts.current - counts.max;
      return lines(
        `등록된 알림이 ${counts.current}개로, 슬롯 ${counts.max}개보다 ${over}개 많습니다.`,
        `알림을 ${over}개 삭제하거나 슬롯을 늘린 뒤 다시 저장해 주세요.`,
      );
    },
    help: PRICING_HELP,
  },
  INVALID_WEBHOOK_URL: {
    message: lines(
      "디스코드 웹훅 URL 형식이 아닙니다.",
      "디스코드에서 만든 웹훅의 URL을 그대로 복사해 붙여 넣어 주세요.",
    ),
    help: CUSTOM_WEBHOOK_HELP,
  },
  WEBHOOK_NOT_FOUND: {
    message: lines(
      "입력한 웹훅을 디스코드에서 찾지 못했습니다.",
      "웹훅이 삭제되지 않았는지 확인하고, URL을 처음부터 끝까지 다시 복사해 주세요.",
    ),
    help: CUSTOM_WEBHOOK_HELP,
  },
  WEBHOOK_GUILD_MISMATCH: {
    message: lines(
      "다른 디스코드 서버에서 만든 웹훅입니다.",
      "알림을 등록하는 이 서버에서 웹훅을 만들어 입력해 주세요.",
    ),
    help: CUSTOM_WEBHOOK_HELP,
  },
  SUBSCRIPTION_REQUIRED: {
    message: lines(
      "커스텀 웹훅과 임베드 색상은 월간 구독 서버 전용 기능입니다.",
      "구독하거나, 해당 항목을 비운 뒤 다시 시도해 주세요.",
    ),
    help: PRICING_HELP,
  },
  INVALID_EMBED_COLOR: {
    message: "임베드 색상은 #RRGGBB 형식(예: #00FFA3)으로 입력해 주세요.",
  },
};
