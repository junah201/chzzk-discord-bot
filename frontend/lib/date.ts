import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import relativeTime from "dayjs/plugin/relativeTime";
import "dayjs/locale/ko";

dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(relativeTime);

dayjs.locale("ko");
dayjs.tz.setDefault("Asia/Seoul");

export const formatDate = (
  date: string | Date,
  format = "YYYY-MM-DD HH:mm:ss",
) => {
  return dayjs(date).tz().format(format);
};

export const fromNow = (date: string | Date) => {
  return dayjs(date).fromNow();
};

export default dayjs;
