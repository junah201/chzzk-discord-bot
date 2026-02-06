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
}

export interface Channel {
  id: string;
  type: number;
  last_message_id: string;
  flags: number;
  guild_id: string;
  name: string;
  parent_id: string;
  rate_limit_per_user: number;
  topic: null;
  position: number;
  permission_overwrites: [];
  nsfw: boolean;
}

export interface Notification {
  PK: string;
  SK: string;
  chzzk_id?: string;
  guild_id: string;
  channel_id: string;
  channel_name: string;
  custom_message: string;
  disable_embed: boolean;
  disable_button: boolean;
  disable_notification: boolean;
  last_noti_at: string | null;
  last_noti_status: string;
}

export interface APIError {
  code: string;
  message: string;
}
