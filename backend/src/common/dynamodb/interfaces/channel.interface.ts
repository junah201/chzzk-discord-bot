import { Base } from './base.interface';

export interface ChzzkChannel extends Base {
  channelId: string;
  channelImageUrl: string;
  channelName: string;
  index: number;
  lastLiveId: number;
  lastLiveTitle: string;
  type: 'CHZZK';
}
