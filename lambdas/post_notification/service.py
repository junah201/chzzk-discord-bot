import boto3

dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table("chzzk-bot-db")


def check_guild_limit(guild_id: str) -> tuple[bool, str, bool]:
    """
    서버의 알림 등록 제한 검증
    반환값: (통과 여부, 에러 메시지, 신규 서버 여부)
    """
    guild_res = table.get_item(
        Key={"PK": f"GUILD#{guild_id}", "SK": f"GUILD#{guild_id}"}
    )
    guild_item = guild_res.get("Item")

    is_new_guild = guild_item is None
    max_limit = int(guild_item.get("max_limit", 5)) if guild_item else 5
    current_count = int(guild_item.get("current_count", 0)) if guild_item else 0

    if current_count >= max_limit:
        return (
            False,
            f"알림 등록 제한을 초과했습니다. (최대 {max_limit}개 등록 가능 / 현재 {current_count}개)",
            is_new_guild,
        )

    return True, "", is_new_guild


def is_chzzk_registered(chzzk_id: str) -> bool:
    """치지직 채널 정보 등록 여부 확인"""
    res = dynamodb.query(
        TableName="chzzk-bot-db",
        KeyConditionExpression="#pk = :pk_val AND #sk = :sk_val",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk_val": {"S": f"CHZZK#{chzzk_id}"},
            ":sk_val": {"S": f"CHZZK#{chzzk_id}"},
        },
    )
    return bool(res.get("Items", []))


def register_chzzk_channel(chzzk_id: str, chzzk_data: dict, index: int) -> bool:
    """치지직 채널 정보 DB 저장"""
    res = dynamodb.put_item(
        TableName="chzzk-bot-db",
        Item={
            "PK": {"S": f"CHZZK#{chzzk_id}"},
            "SK": {"S": f"CHZZK#{chzzk_id}"},
            "lastLiveId": {"N": f"{chzzk_data['liveId']}"},
            "lastLiveTitle": {"S": chzzk_data["liveTitle"]},
            "channelId": {"S": chzzk_data["channel"]["channelId"]},
            "channelName": {"S": chzzk_data["channel"]["channelName"]},
            "channelImageUrl": {"S": chzzk_data["channel"]["channelImageUrl"] or ""},
            "type": {"S": "CHZZK"},
            "index": {"N": f"{index}"},
        },
    )
    return res["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_naver_account(index: int) -> dict | None:
    """네이버 세션 쿠키 정보 조회"""
    res = table.get_item(Key={"PK": f"NAVER#{index}", "SK": f"NAVER#{index}"})
    return res.get("Item")


def is_notification_exists(chzzk_id: str, channel_id: str, guild_id: str) -> bool:
    """동일 서버/채널에 이미 등록된 알림인지 확인"""
    res = dynamodb.query(
        TableName="chzzk-bot-db",
        KeyConditionExpression="#pk = :pk_val AND #sk = :sk_val",
        FilterExpression="guild_id = :guild_id",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk_val": {"S": f"CHZZK#{chzzk_id}"},
            ":sk_val": {"S": f"NOTI#{channel_id}"},
            ":guild_id": {"S": guild_id},
        },
    )
    return bool(res.get("Items", []))


def save_notification_and_increment_counter(
    guild_id: str,
    channel_id: str,
    channel_data: dict,
    chzzk_id: str,
    chzzk_data: dict,
    body: dict,
    is_new_guild: bool,
):
    """신규 GUILD 객체 생성(필요 시), NOTI 아이템 저장 및 current_count 원자적 증가(+1)"""
    # 1. 신규 서버인 경우 GUILD 기본 메타데이터 객체 생성 (limit: 5)
    if is_new_guild:
        table.put_item(
            Item={
                "PK": f"GUILD#{guild_id}",
                "SK": f"GUILD#{guild_id}",
                "guild_id": guild_id,
                "max_limit": 5,
                "current_count": 0,
                "type": "GUILD",
            }
        )

    # 2. NOTI 아이템 추가
    dynamodb.put_item(
        TableName="chzzk-bot-db",
        Item={
            "PK": {"S": f"CHZZK#{chzzk_id}"},
            "SK": {"S": f"NOTI#{channel_id}"},
            "chzzk_id": {"S": str(chzzk_id)},
            "chzzk_name": {"S": chzzk_data["channel"]["channelName"]},
            "chzzk_image_url": {
                "S": chzzk_data["channel"]["channelImageUrl"] or ""
            },
            "channel_id": {"S": str(channel_id)},
            "channel_name": {"S": channel_data.get("name", "")},
            "guild_id": {"S": guild_id},
            "custom_message": {"S": body.get("custom_message", "")},
            "type": {"S": "NOTI"},
            "disable_embed": {"BOOL": body.get("disable_embed", False)},
            "disable_button": {"BOOL": body.get("disable_button", False)},
            "disable_notification": {"BOOL": body.get("disable_notification", False)},
            "index": {"N": "-1"},
        },
    )

    # 3. GUILD.current_count +1 원자적 증가 (Atomic Counter)
    table.update_item(
        Key={"PK": f"GUILD#{guild_id}", "SK": f"GUILD#{guild_id}"},
        UpdateExpression="ADD current_count :inc",
        ExpressionAttributeValues={":inc": 1},
    )