import json
import logging
from typing import Literal, TypedDict

import requests
from user_agent import generate_user_agent

__all__ = ["ChzzkChannel", "ChzzkLive", "get_chzzk", "Following"]

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CHZZK_FOLLOW_URL = "https://api.chzzk.naver.com/service/v1/channels/{channel_id}/follow"


class ChzzkChannel(TypedDict):
    channelId: str
    channelName: str
    channelImageUrl: str | None
    verifiedMark: bool


class ChzzkLive(TypedDict):
    liveId: int
    liveTitle: str
    status: str
    liveImageUrl: str
    defaultThumbnailImageUrl: str | None
    concurrentUserCount: int
    accumulateCount: int
    chatDonationRankingExposure: bool | None
    openDate: str
    closeDate: str
    adult: bool | None
    chatChannelId: str | None
    categoryType: str
    liveCategory: str
    liveCategoryValue: str
    chatActive: bool
    chatAvailableGroup: str
    paidPromotion: bool
    chatAvailableCondition: str
    minFollowerMinute: int
    livePlaybackJson: str
    channel: ChzzkChannel
    livePollingStatusJson: str
    userAdultStatus: str | None

    def __str__(self) -> str:
        return f"ChzzkLive(liveId={self.liveId}, liveTitle={self.liveTitle}, status={self.status})"

    def __repr__(self) -> str:
        return self.__str__()


class Streamer(TypedDict):
    openLive: bool


class Following(TypedDict):
    channel: ChzzkChannel
    liveInfo: ChzzkLive
    streamer: Streamer


def get_chzzk(
    channel_id: str, logger: logging.Logger | None = None, retry: int = 2
) -> ChzzkLive | None:
    """채널 ID를 통해 치지직 채널 정보를 가져옵니다.
    만약 채널이 존재하지 않는다면 None을 반환합니다.
    """
    # 정규화되지 않은 채널 ID
    if "/" in channel_id:
        if logger:
            logger.error(
                json.dumps(
                    {"type": "INVALID_CHZZK_CHANNEL_ID", "channel_id": channel_id}
                )
            )
        return None

    for _retry in range(1, retry + 1):
        try:
            res = requests.get(
                f"https://api.chzzk.naver.com/service/v2/channels/{channel_id}/live-detail",
                headers={
                    "User-Agent": generate_user_agent(os="win", device_type="desktop"),
                },
                timeout=1,
            )
            break
        except requests.exceptions.Timeout as e:
            if logger:
                logger.error(
                    json.dumps(
                        {
                            "type": "CHZZK_REQUEST_TIMEOUT",
                            "channel_id": channel_id,
                            "exception": str(e),
                            "retry": _retry,
                        }
                    )
                )
        except Exception as e:
            if logger:
                logger.error(
                    json.dumps(
                        {
                            "type": "CHZZK_REQUEST_ERROR",
                            "channel_id": channel_id,
                            "exception": str(e),
                            "retry": _retry,
                        }
                    )
                )
            continue
    else:
        # Break 없이 끝났을 때 -> retry 모두 실패
        if logger:
            logger.error(
                json.dumps({"type": "CHZZK_REQUEST_FAILED", "channel_id": channel_id})
            )
        return None

    # 채널이 존재하지 않는 경우 or 알 수 없는 오류
    if res.status_code != 200:
        if logger:
            logger.error(
                json.dumps(
                    {
                        "type": "CHZZK_INVALID_RESPONSE",
                        "channel_id": channel_id,
                        "status_code": res.status_code,
                        "response": res.text,
                    }
                )
            )
        return None

    content = res.json()["content"]

    # 한번도 방송을 키지 않은 경우
    if content is None:
        return None

    return content


def _handle_follow_request(
    method: Literal["POST", "DELETE"], chzzk_id: str, nid_aut: str, nid_ses: str
) -> tuple[bool, int, str]:
    """팔로우/언팔로우 요청 공통 처리 함수. 성공 시 (True, 200, "")를 반환하고, 실패 시 (False, status_code, error_message)를 반환합니다."""
    action_name = "FOLLOW" if method == "POST" else "UNFOLLOW"
    url = CHZZK_FOLLOW_URL.format(channel_id=chzzk_id)

    try:
        res = requests.request(
            method,
            url,
            headers={
                "User-Agent": generate_user_agent(os="win", device_type="desktop"),
                "Cookie": f"NID_AUT={nid_aut}; NID_SES={nid_ses}",
            },
            timeout=3,
        )
        res.raise_for_status()
    except requests.exceptions.Timeout as e:
        logger.error(
            json.dumps(
                {
                    "type": f"CHZZK_{action_name}_TIMEOUT",
                    "chzzk_id": chzzk_id,
                    "exception": str(e),
                }
            )
        )
        return False, -1, f"TimeoutError: {str(e)}"
    except requests.exceptions.ConnectionError as e:
        logger.error(
            json.dumps(
                {
                    "type": f"CHZZK_{action_name}_CONNECTION_ERROR",
                    "chzzk_id": chzzk_id,
                    "exception": str(e),
                }
            )
        )
        return False, -2, f"ConnectionError: {str(e)}"
    except requests.exceptions.HTTPError:
        logger.error(
            json.dumps(
                {
                    "type": f"CHZZK_{action_name}_HTTP_ERROR",
                    "chzzk_id": chzzk_id,
                    "status_code": res.status_code,
                    "text": res.text,
                }
            )
        )
        try:
            err_data = res.json()
            err_message = err_data.get("message", f"HTTPError: {res.status_code}")
        except Exception:
            err_message = f"HTTPError: {res.status_code} - {res.text}"
        return False, res.status_code, err_message
    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "type": f"CHZZK_{action_name}_UNKNOWN_ERROR",
                    "chzzk_id": chzzk_id,
                    "exception": str(e),
                }
            )
        )
        return False, -3, f"UnknownError: {str(e)}"

    return True, 200, ""


def follow_chzzk_channel(
    chzzk_id: str, nid_aut: str, nid_ses: str
) -> tuple[bool, int, str]:
    """치지직 채널 팔로우 요청을 수행합니다. 성공 시 (True, 200, "")를 반환하고, 실패 시 (False, status_code, error_message)를 반환합니다."""
    return _handle_follow_request("POST", chzzk_id, nid_aut, nid_ses)


def unfollow_chzzk_channel(
    chzzk_id: str, nid_aut: str, nid_ses: str
) -> tuple[bool, int, str]:
    """치지직 채널 언팔로우 요청을 수행합니다. 성공 시 (True, 200, "")를 반환하고, 실패 시 (False, status_code, error_message)를 반환합니다."""
    return _handle_follow_request("DELETE", chzzk_id, nid_aut, nid_ses)
