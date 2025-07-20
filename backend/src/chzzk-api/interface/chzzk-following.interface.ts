import { ChzzkChannel } from './chzzk-channel.interface';
import { ChzzkLive } from './chzzk-live.interface';

export interface Streamer {
  openLive: boolean;
}

export interface Following {
  channel: ChzzkChannel;
  liveInfo: ChzzkLive;
  streamer: Streamer;
}
