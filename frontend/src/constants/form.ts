export const INPUT = Object.freeze({
  CHZZK_ID: Object.freeze({
    name: 'chzzk_id',
    rules: {
      required: {
        value: true,
        message: '필수 입력 항목입니다.',
      },
    },
  }),
  CHANNEL_ID: Object.freeze({
    name: 'channel_id',
    rules: {
      required: {
        value: true,
        message: '필수 입력 항목입니다.',
      },
    },
  }),
  GUILD_ID: Object.freeze({
    name: 'guild_id',
    rules: {
      required: {
        value: true,
        message: '필수 입력 항목입니다.',
      },
    },
  }),
  CUSTOM_MESSAGE: Object.freeze({
    name: 'custom_message',
    rules: {},
  }),
  DISABLE_EMBED: Object.freeze({
    name: 'disable_embed',
    rules: {},
  }),
  DISABLE_BUTTON: Object.freeze({
    name: 'disable_button',
    rules: {},
  }),
  DISABLE_NOTIFICATION: Object.freeze({
    name: 'disable_notification',
    rules: {},
  }),
});

export type RegisterTypes = (typeof INPUT)[keyof typeof INPUT]['name'];
export type RegisterField = Record<RegisterTypes, any>;
