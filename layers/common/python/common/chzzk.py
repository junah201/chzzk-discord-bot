from typing import TypedDict
import aiohttp


class ChzzkChannel(TypedDict):
    channelId: str
    channelName: str
    channelImageUrl: str
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


async def get_chzzk(channel_id: str, session: aiohttp.ClientSession) -> ChzzkLive | None:
    """채널 ID를 통해 치지직 채널 정보를 가져옵니다.
    만약 채널이 존재하지 않는다면 None을 반환합니다.
    """
    # 정규화되지 않은 채널 ID
    if "/" in channel_id:
        return None

    try:
        async with session.get(
            url=f"https://api.chzzk.naver.com/service/v2/channels/{channel_id}/live-detail",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            }
        ) as res:
            # 채널이 존재하지 않는 경우 or 알 수 없는 오류
            if res.status != 200:
                return None

            content = await res.json()
            content = content["content"]

            # 한번도 방송을 키지 않은 경우
            if content is None:
                return None

            return content
    except Exception as e:
        print(e)
        return None
