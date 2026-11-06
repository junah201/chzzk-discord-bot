import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import "dayjs/locale/ko";

dayjs.extend(relativeTime);

dayjs.locale("ko");

const dateTimeFormatter = new Intl.DateTimeFormat("ko-KR", {
  dateStyle: "long",
  timeStyle: "medium",
  timeZone: "Asia/Seoul",
});

export const formatDateTime = (date: string | Date) => {
  return dateTimeFormatter.format(new Date(date));
};

export const fromNow = (date: string | Date) => {
  return dayjs(date).fromNow();
};

export default dayjs;
