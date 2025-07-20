import { ChzzkChannel } from './chzzk-channel.interface';

export interface ChzzkLive {
  liveId: number;
  liveTitle: string;
  status: string;
  liveImageUrl: string;
  defaultThumbnailImageUrl?: string | null;
  concurrentUserCount: number;
  accumulateCount: number;
  chatDonationRankingExposure?: boolean | null;
  openDate: string;
  closeDate: string;
  adult?: boolean | null;
  chatChannelId?: string | null;
  categoryType: string;
  liveCategory: string;
  liveCategoryValue: string;
  chatActive: boolean;
  chatAvailableGroup: string;
  paidPromotion: boolean;
  chatAvailableCondition: string;
  minFollowerMinute: number;
  livePlaybackJson: string;
  channel: ChzzkChannel;
  livePollingStatusJson: string;
  userAdultStatus?: string | null;
}
