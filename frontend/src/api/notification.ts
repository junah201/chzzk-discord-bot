import { API_ROUTE, ACCESS_TOEKN } from '@/constants';
import { Axios } from '@/lib/Axios';
import { User, Guild, Notification } from '@/types';

const { VITE_API_URL } = import.meta.env;

const AuthAxios = new Axios(true, VITE_API_URL, ACCESS_TOEKN);

interface NotificationCreate {
  channel_id: string;
  chzzk_id: string;
  custom_message: string;
}

export const addNotification = async (data: NotificationCreate) => {
  const res = await AuthAxios.post(API_ROUTE.NOTIFICATION.ADD, data);

  return res;
};

export const getNotificationsByGuildId = async (guildId: string) => {
  const res = await AuthAxios.get<Notification[]>(
    API_ROUTE.NOTIFICATION.GET_BY_GUILD_ID(guildId)
  );

  return res;
};

interface NotificationDelete {
  channel_id: string;
  chzzk_id: string;
}

export const deleteNotification = async (data: NotificationDelete) => {
  const res = await AuthAxios.delete(API_ROUTE.NOTIFICATION.DELETE, data);

  return res;
};

interface NotificationUpdate extends NotificationCreate {}

export const updateNotification = async (data: NotificationUpdate) => {
  const res = await AuthAxios.put(API_ROUTE.NOTIFICATION.UPDATE, data);

  return res;
};

interface NotificationTest extends NotificationDelete {}

export const sendTestNotification = async (data: NotificationTest) => {
  const res = await AuthAxios.post(API_ROUTE.NOTIFICATION.SEND_TEST, data);

  return res;
};
