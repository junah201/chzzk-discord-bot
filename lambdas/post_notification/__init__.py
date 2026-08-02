import json
import logging

from shared import build_response, get_channel, get_chzzk, middleware
from shared.exceptions import BadRequestError

from lambdas.post_notification.client import follow_chzzk_channel
from lambdas.post_notification.service import (
    check_guild_limit,
    get_naver_account,
    is_chzzk_registered,
    is_notification_exists,
    register_chzzk_channel,
    save_notification_and_increment_counter,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger, admin_check=True)
def handler(event, context):
    headers = event.get("headers", {})
    token = headers.get("Authorization")
    body = json.loads(event.get("body", "{}"))

    chzzk_id = body.get("chzzk_id")
    guild_id = body.get("guild_id")
    channel_id = body.get("channel_id")

    if not all([token, chzzk_id, channel_id, guild_id]):
        raise BadRequestError()

    # 1. 디스코드 채널 및 서버 소속 검증
    channel_data = get_channel(channel_id)
    if not channel_data:
        return build_response(400, "해당 디스코드 채널을 찾을 수 없습니다.")

    if channel_data.get("guild_id") != guild_id:
        return build_response(400, "해당 디스코드 채널이 서버에 속해있지 않습니다.")

    # 2. 서버 알림 개수 제한 검증
    is_valid, err_msg, is_new_guild = check_guild_limit(guild_id)
    if not is_valid:
        return build_response(400, err_msg)

    # 3. 치지직 채널 존재 검증
    chzzk_data = get_chzzk(chzzk_id)
    if not chzzk_data:
        return build_response(400, "해당 치지직 채널을 찾을 수 없습니다.")

    # 4. 치지직 채널 DB 저장 및 샤딩 인덱스 처리
    index = int(chzzk_id, 16) % 7
    if not is_chzzk_registered(chzzk_id):
        if index >= 5:
            index = 4
        if not register_chzzk_channel(chzzk_id, chzzk_data, index):
            return build_response(500, "치지직 채널 정보 등록에 실패했습니다.")

    # 5. 연동 계정 팔로우 수행
    naver_item = get_naver_account(index)
    if naver_item:
        if not follow_chzzk_channel(chzzk_id, index, naver_item):
            return build_response(
                500, f"치지직 채널 팔로우에 실패했습니다. 관리자에게 문의해주세요. ({index})"
            )

    # 6. 알림 중복 확인
    if is_notification_exists(chzzk_id, channel_id, guild_id):
        return build_response(
            400,
            f"이미 {channel_data['name']}에 등록된 채널({chzzk_data['channel']['channelName']})입니다.",
        )

    # 7. NOTI 저장 및 GUILD 카운터 증가 (+1)
    save_notification_and_increment_counter(
        guild_id,
        channel_id,
        channel_data,
        chzzk_id,
        chzzk_data,
        body,
        is_new_guild,
    )

    return build_response(204)