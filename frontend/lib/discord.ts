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
} as const;

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
