from dataclasses import dataclass

import requests


@dataclass
class ChzzkChannel:
    channelId: str
    channelName: str
    channelImageUrl: str
    verifiedMark: bool

    def __str__(self) -> str:
        return f"ChzzkChannel(channelId={self.channelId}, channelName={self.channelName})"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class ChzzkLive:
    liveId: int
    liveTitle: str
    status: str
    liveImageUrl: str
    defaultThumbnailImageUrl: str | None
    concurrentUserCount: int
    accumulateCount: int
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


def get_chzzk(channel_id: str) -> ChzzkLive | None:
    """채널 ID를 통해 치지직 채널 정보를 가져옵니다.
    만약 채널이 존재하지 않는다면 None을 반환합니다.
    """
    # 정규화되지 않은 채널 ID
    if "/" in channel_id:
        return None

    try:
        res = requests.get(
            f"https://api.chzzk.naver.com/service/v2/channels/{channel_id}/live-detail")
    except Exception as e:
        print(e)
        return None

    # 채널이 존재하지 않는 경우 or 알 수 없는 오류
    if res.status_code != 200:
        return None

    content = res.json()["content"]

    # 한번도 방송을 키지 않은 경우
    if content is None:
        return None
    channel = content.pop("channel", {})
    return ChzzkLive(
        **content,
        channel=ChzzkChannel(**channel)
    )
