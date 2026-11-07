export interface MessageVariable {
  key: string;
  label: string;
}

/** lambdas/shared/message_template.py와 같은 변수 목록 */
export const MESSAGE_VARIABLES: readonly MessageVariable[] = [
  { key: "channel.name", label: "채널 이름" },
  { key: "channel.url", label: "채널 주소" },
  { key: "stream.url", label: "방송 주소" },
  { key: "stream.title", label: "방송 제목" },
  { key: "stream.category", label: "카테고리" },
  { key: "stream.tags", label: "태그" },
  { key: "stream.started_at", label: "시작 시각" },
  { key: "everyone", label: "@everyone" },
  { key: "here", label: "@here" },
];

const ALIASES = ["stream.game"];
const KNOWN_KEYS = new Set([
  ...MESSAGE_VARIABLES.map((variable) => variable.key),
  ...ALIASES,
]);
const VARIABLE_PATTERN = /\{([a-z_.]+)\}/g;

export interface MessageTemplateSample {
  chzzkId: string;
  channelName: string;
  title: string;
  category: string;
  tags: string[];
  startedAtLabel: string;
}

export function renderMessage(template: string, sample: MessageTemplateSample) {
  const values: Record<string, string> = {
    "channel.name": sample.channelName,
    "channel.url": `https://chzzk.naver.com/${sample.chzzkId}`,
    "stream.url": `https://chzzk.naver.com/live/${sample.chzzkId}`,
    "stream.title": sample.title,
    "stream.category": sample.category,
    "stream.game": sample.category,
    "stream.tags": sample.tags.join(", "),
    "stream.started_at": sample.startedAtLabel,
    everyone: "@everyone",
    here: "@here",
  };
  return template.replace(
    VARIABLE_PATTERN,
    (match, key: string) => values[key] ?? match,
  );
}

export function findUnknownVariables(template: string) {
  const unknown = new Set<string>();
  for (const [match, key] of template.matchAll(VARIABLE_PATTERN)) {
    if (!KNOWN_KEYS.has(key)) unknown.add(match);
  }
  return [...unknown];
}
