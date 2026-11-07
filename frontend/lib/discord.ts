// 디스코드 다크 테마 색상. 사이트 테마와 무관하게 실제 디스코드 화면처럼 보이도록 고정값을 사용
export const DISCORD_COLORS = {
  bg: "#313338",
  embed: "#2b2d31",
  code: "#1e1f22",
  text: "#dbdee1",
  header: "#f2f3f5",
  muted: "#949ba4",
  icon: "#80848e",
  interactive: "#b5bac1",
  link: "#00a8fc",
  blurple: "#5865f2",
  button: "#4e5058",
  avatar: "#f47b67",
  mentionBg: "rgba(88, 101, 242, 0.3)",
  mentionText: "#c9cdfb",
  highlightBg: "rgba(240, 178, 50, 0.08)",
  highlightBar: "#f0b232",
  live: "#e5172d",
  timestampBg: "rgba(78, 80, 88, 0.48)",
} as const;

const TIMESTAMP_FORMATS: Record<string, Intl.DateTimeFormatOptions> = {
  t: { hour: "numeric", minute: "2-digit" },
  T: { hour: "numeric", minute: "2-digit", second: "2-digit" },
  d: { year: "numeric", month: "2-digit", day: "2-digit" },
  D: { year: "numeric", month: "long", day: "numeric" },
  f: { dateStyle: "long", timeStyle: "short" },
  F: { dateStyle: "full", timeStyle: "short" },
};

const RELATIVE_UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["year", 365 * 24 * 60 * 60],
  ["month", 30 * 24 * 60 * 60],
  ["day", 24 * 60 * 60],
  ["hour", 60 * 60],
  ["minute", 60],
];

/** 디스코드 타임스탬프(<t:초:형식>)를 디스코드 앱처럼 글자로 바꿈 */
export function formatDiscordTimestamp(
  seconds: number,
  style = "f",
  now = Date.now(),
) {
  const date = new Date(seconds * 1000);
  if (style !== "R") {
    return date.toLocaleString(
      "ko-KR",
      TIMESTAMP_FORMATS[style] ?? TIMESTAMP_FORMATS.f,
    );
  }
  const diff = seconds - Math.floor(now / 1000);
  if (Math.abs(diff) < 60) return "방금";
  const rtf = new Intl.RelativeTimeFormat("ko", { numeric: "auto" });
  const [unit, size] =
    RELATIVE_UNITS.find(([, size]) => Math.abs(diff) >= size) ??
    RELATIVE_UNITS[RELATIVE_UNITS.length - 1];
  return rtf.format(Math.trunc(diff / size), unit);
}

// 백엔드 shared.notification_dispatcher의 임베드 색상 규칙과 맞춰야 함
export const DEFAULT_EMBED_COLOR = 0x02e895;

export const parseEmbedColor = (embedColor: string): number | null => {
  const value = embedColor.trim();
  if (/^#[0-9a-fA-F]{6}$/.test(value)) return parseInt(value.slice(1), 16);
  if (/^\d+$/.test(value)) {
    const color = Number(value);
    if (color <= 0xffffff) return color;
  }
  return null;
};

export const toCssColor = (color: number) =>
  `#${color.toString(16).padStart(6, "0")}`;

export const toHexEmbedColor = (embedColor: string): string => {
  const color = parseEmbedColor(embedColor);
  return color === null ? "" : toCssColor(color).toUpperCase();
};
