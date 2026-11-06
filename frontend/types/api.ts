export interface User {
  id: string;
  username: string;
  avatar: string;
  discriminator: string;
  public_flags: number;
  premium_type: number;
  flags: number;
  banner: string;
  accent_color: string | null;
  global_name: string;
  banner_color: string | null;
  mfa_enabled: boolean;
  locale: string;
  email: string;
  verified: boolean;
}

export interface Guild {
  id: string;
  name: string;
  icon: string | null;
  description: string | null;
  approximate_member_count: number | null;
  current_count: number;
  max_limit: number;
}

export interface SlotSyncResult {
  current_count: number;
  previous_count: number;
  max_limit: number;
}

export interface PermissionOverwrite {
  id: string;
  type: 0 | 1;
  allow: string;
  deny: string;
}

export interface Channel {
  id: string;
  type: number;
  last_message_id: string | null;
  flags: number;
  guild_id: string;
  name: string;
  parent_id: string | null;
  rate_limit_per_user: number;
  topic: string | null;
  position: number;
  permission_overwrites: PermissionOverwrite[];
  nsfw: boolean;
}

export interface Notification {
  chzzk_id: string;
  chzzk_name?: string;
  chzzk_image_url?: string;
  guild_id: string;
  channel_id: string;
  channel_name: string;
  custom_message: string;
  webhook_url?: string;
  embed_color?: string;
  disable_embed: boolean;
  disable_tag?: boolean;
  disable_button: boolean;
  disable_notification: boolean;
  last_noti_at: string | null;
  last_noti_status: string;
}

export interface APIError {
  code: string;
  message: string;
}
