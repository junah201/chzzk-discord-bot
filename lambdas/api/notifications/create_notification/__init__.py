import json
import logging

from api.notifications.create_notification.client import process_follow
from api.notifications.create_notification.service import (
    check_guild_limit,
    get_naver_account,
    is_chzzk_registered,
    is_notification_exists,
    register_chzzk_channel,
    save_notification_and_increment_counter,
)
from shared import CHANNEL_TYPE, build_response, get_channel, get_chzzk, middleware
from shared.exceptions import (
    BadRequestError,
    ChzzkChannelNotFoundError,
    ChzzkChannelRegisterError,
    ServiceAccountBlockedError,
    ServiceFollowLimitError,
)
from shared.notification_dispatcher import (
    is_guild_subscription_active,
    is_valid_webhook_url,
    parse_embed_color,
    verify_webhook_guild,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger, admin_check=True)
def handler(event, _context):
    headers = event.get("headers", {})
    token = headers.get("Authorization")
    body = json.loads(event.get("body", "{}"))

    chzzk_id = body.get("chzzk_id")
    guild_id = body.get("guild_id")
    channel_id = body.get("channel_id")
    webhook_url = body.get("webhook_url", "").strip()
    embed_color = body.get("embed_color", "").strip()
    auto_crosspost = body.get("auto_crosspost", False)

    if not all([token, chzzk_id, channel_id, guild_id]):
        raise BadRequestError()
    is_subscription_active = is_guild_subscription_active(guild_id)
    if webhook_url and not is_valid_webhook_url(webhook_url):
        raise BadRequestError(
            "디스코드 웹훅 URL 형식이 아닙니다.", code="INVALID_WEBHOOK_URL"
        )
    if webhook_url and not is_subscription_active:
        raise BadRequestError(
            "커스텀 웹훅은 월간 구독 서버 전용 기능입니다.",
            code="SUBSCRIPTION_REQUIRED",
        )
    if embed_color and parse_embed_color(embed_color) is None:
        raise BadRequestError(
            "임베드 색상은 #RRGGBB 형식으로 입력해 주세요.",
            code="INVALID_EMBED_COLOR",
        )
    if embed_color and not is_subscription_active:
        raise BadRequestError(
            "커스텀 임베드 색상은 월간 구독 서버 전용 기능입니다.",
            code="SUBSCRIPTION_REQUIRED",
        )
    if auto_crosspost and not is_subscription_active:
        raise BadRequestError(
            "공지 채널 자동 게시는 월간 구독 서버 전용 기능입니다.",
            code="SUBSCRIPTION_REQUIRED",
        )
    if webhook_url:
        verify_webhook_guild(webhook_url, guild_id)

    # 1. 디스코드 채널 및 서버 소속 검증
    channel_data = get_channel(channel_id)
    if not channel_data:
        raise BadRequestError(
            "치직 봇이 이 채널에 접근할 수 없습니다. 채널 권한을 확인해 주세요.",
            code="BOT_CHANNEL_ACCESS_DENIED",
        )

    if channel_data.get("guild_id") != guild_id:
        raise BadRequestError(
            "이 서버의 채널이 아닙니다. 새로고침 후 다시 시도해 주세요.",
            code="DISCORD_CHANNEL_GUILD_MISMATCH",
        )

    if auto_crosspost and channel_data.get("type") != CHANNEL_TYPE.GUILD_NEWS:
        raise BadRequestError(
            "공지 채널 자동 게시는 공지 채널에서만 사용할 수 있습니다.",
            code="CROSSPOST_REQUIRES_ANNOUNCEMENT_CHANNEL",
        )

    # 2. 서버 알림 개수 제한 검증
    check_guild_limit(guild_id)

    # 3. 치지직 채널 존재 검증
    chzzk_data = get_chzzk(chzzk_id)
    if not chzzk_data:
        raise ChzzkChannelNotFoundError()

    # 4. 치지직 채널 DB 저장 및 샤딩 인덱스 처리
    # 팔로우 한도가 찬 계정은 건너뛰고 다음 계정에 배정한다.
    full_indices = {3, 4}
    index = int(chzzk_id, 16) % 7
    while index in full_indices:
        index = (index + 1) % 7
    if not is_chzzk_registered(chzzk_id):
        if not register_chzzk_channel(chzzk_id, chzzk_data, index):
            raise ChzzkChannelRegisterError()

    # 5. 연동 계정 팔로우 수행
    naver_item = get_naver_account(index)
    if naver_item:
        success, err_message = process_follow(chzzk_id, index, naver_item)
        if not success:
            if "영구 활동 제한" in err_message:
                # TODO: NAVER 계정 아이템에 치지직 닉네임도 저장해 두고, 차단 해제할 계정을
                # account_index 대신 닉네임으로 응답에 담아 사용자가 바로 알 수 있게 하기
                raise ServiceAccountBlockedError(index)
            elif "최대 팔로우 수를 초과" in err_message:
                raise ServiceFollowLimitError(index)
            return build_response(
                500,
                f"치지직 채널 팔로우 처리에 실패했습니다. 잠시 후 다시 시도한 후에도 동일한 현상이 발생하면 서포트 서버로 문의해 주세요. ({index})",
            )
    else:
        return build_response(
            500,
            f"치지직 채널 팔로우 처리에 실패했습니다. 잠시 후 다시 시도한 후에도 동일한 현상이 발생하면 서포트 서버로 문의해 주세요. ({index})",
        )

    # 6. 알림 중복 확인
    if is_notification_exists(chzzk_id, channel_id, guild_id):
        raise BadRequestError(
            "이 디스코드 채널에 이미 등록된 치지직 채널입니다.",
            code="NOTIFICATION_ALREADY_EXISTS",
        )

    # 7. NOTI 저장 및 GUILD 카운터 증가 (+1)
    save_notification_and_increment_counter(
        guild_id,
        channel_id,
        channel_data,
        chzzk_id,
        chzzk_data,
        body,
    )

    return build_response(204)
