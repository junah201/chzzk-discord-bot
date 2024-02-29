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
  avatar_decoration_data: any | null;
  banner_color: string | null;
  mfa_enabled: boolean;
  locale: string;
  email: string;
  verified: boolean;
}

export interface Guild {
  id: string;
  name: string;
  icon: string;
  owner: boolean;
  permissions: number;
  permissions_new: string;
  features: string[];
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
  guild_id: string;
  channel_id: string;
  channel_name: string;
  custom_message: string;
}
