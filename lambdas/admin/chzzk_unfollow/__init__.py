import json
import logging

import boto3
from shared import middleware
from shared.chzzk import unfollow_chzzk_channel
from shared.utils import build_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table("chzzk-bot-db")


@middleware(logger)
def handler(event, context):
    chzzk_id = event.get("chzzk_id", None)
    index = event.get("index", None)

    if chzzk_id is None:
        logger.info(
            json.dumps(
                {
                    "type": "MISSING_CHZZK_ID",
                }
            )
        )
        return build_response(400, "'chzzk_id' is required in the event.")

    if index is None:
        res = table.get_item(Key={"PK": f"CHZZK#{chzzk_id}", "SK": f"CHZZK#{chzzk_id}"})
        chzzk_item = res.get("Item")

        if chzzk_item is None:
            logger.info(
                json.dumps(
                    {
                        "type": "CHZZK_NOT_REGISTERED",
                        "chzzk_id": chzzk_id,
                    }
                )
            )
            return build_response(
                400, f"치지직 채널 '{chzzk_id}'은 등록되지 않았습니다."
            )

        index = chzzk_item.get("index", None)
        if index is None:
            logger.info(
                json.dumps(
                    {
                        "type": "MISSING_INDEX",
                        "chzzk_id": chzzk_id,
                    }
                )
            )
            return build_response(
                400, f"치지직 채널 '{chzzk_id}'의 'index' 정보가 없습니다."
            )

    res = table.get_item(Key={"PK": "NAVER#ACCOUNTS", "SK": f"NAVER#{index}"})
    naver_account = res.get("Item")

    if naver_account is None:
        logger.info(
            json.dumps(
                {
                    "type": "NAVER_ACCOUNT_NOT_FOUND",
                    "index": index,
                }
            )
        )
        return build_response(
            400, f"인덱스 '{index}'에 해당하는 네이버 계정이 없습니다."
        )

    success, status_code, err_message = unfollow_chzzk_channel(
        chzzk_id, naver_account.get("NID_AUT"), naver_account.get("NID_SES")
    )

    if not success:
        logger.info(
            json.dumps(
                {
                    "type": "UNFOLLOW_FAILED",
                    "chzzk_id": chzzk_id,
                    "err_message": err_message,
                }
            )
        )
        return build_response(
            status_code,
            f"치지직 채널 '{chzzk_id}'의 팔로우 해제에 실패했습니다: {err_message}",
        )

    return build_response(
        200, f"치지직 채널 '{chzzk_id}'의 팔로우 해제에 성공했습니다."
    )
