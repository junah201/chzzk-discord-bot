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
