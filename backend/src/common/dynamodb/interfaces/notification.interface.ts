import { Base } from './base.interface';

export interface Notification extends Base {
  channel_id: string;
  channel_name: string;
  custom_message: string;
  guild_id: string;
  index: number;
  last_noti_at: string; // ISO timestamp
  last_noti_status: 'SUCCESS' | string; // 'SUCCESS' | 'FAIL_403 | 'FAIL_500' | 'FAIL_503'
  noti_fail_count: number;
  type: 'NOTI';
}
