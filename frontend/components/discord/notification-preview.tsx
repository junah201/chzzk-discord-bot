import { Fragment } from "react";
import { ExternalLink, UserRound } from "lucide-react";
import { cn } from "@/lib/utils";
import { DEFAULT_EMBED_COLOR, toCssColor } from "@/lib/discord";
import { getChzzkChannelImageUrl } from "@/lib/urls";

// 디스코드 다크 테마 색상. 사이트 테마와 무관하게 실제 디스코드 화면처럼 보이도록 고정값을 사용
const DISCORD = {
  bg: "#313338",
  embed: "#2b2d31",
  code: "#1e1f22",
  text: "#dbdee1",
  header: "#f2f3f5",
  muted: "#949ba4",
  link: "#00a8fc",
  blurple: "#5865f2",
  button: "#4e5058",
};

const MENTION_PATTERN = /(@everyone|@here|<@&\d+>|<@!?\d+>|<#\d+>)/g;

export interface NotificationPreviewLive {
  channelName: string;
  channelImageUrl?: string;
  title: string;
  category: string;
  tags: string[];
  thumbnailUrl?: string;
}

export interface NotificationPreviewProps {
  content: string;
  live: NotificationPreviewLive;
  embedColor?: number;
  disableEmbed?: boolean;
  disableTag?: boolean;
  disableButton?: boolean;
  timestampLabel?: string;
  /** 채널 멘션(<#id>)을 이름으로 보여주기 위한 목록 */
  channelNames?: Record<string, string>;
  /** 커스텀 웹훅으로 보낼 때: 봇 대신 웹훅에 설정한 이름과 프로필 이미지로 보낸다는 자리표시 */
  customSender?: boolean;
  className?: string;
}

/** live_check가 보내는 방송 알림 메시지를 디스코드 화면처럼 그림 */
export function NotificationPreview({
  content,
  live,
  embedColor = DEFAULT_EMBED_COLOR,
  disableEmbed = false,
  disableTag = false,
  disableButton = false,
  timestampLabel = "오늘 오후 8:00",
  channelNames,
  customSender = false,
  className,
}: NotificationPreviewProps) {
  const mentionsEveryone = /@(everyone|here)/.test(content);
  const tags = disableTag ? [] : live.tags.filter(Boolean);
  const isEmpty = !content.trim() && disableEmbed && disableButton;

  return (
    <div
      className={cn(
        "relative text-left text-[15px] leading-[1.375rem] font-normal",
        className,
      )}
      style={{ backgroundColor: DISCORD.bg, color: DISCORD.text }}
    >
      <div
        className="flex gap-4 px-4 py-2"
        style={
          mentionsEveryone
            ? {
                backgroundColor: "rgba(240, 178, 50, 0.08)",
                boxShadow: "inset 2px 0 0 #f0b232",
              }
            : undefined
        }
      >
        {customSender ? (
          <div
            className="mt-0.5 flex size-10 shrink-0 items-center justify-center rounded-full border border-dashed"
            style={{ borderColor: DISCORD.muted, color: DISCORD.muted }}
            title="웹훅에 설정한 프로필 이미지"
          >
            <UserRound className="size-5" />
          </div>
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src="/favicon-192.png"
            alt=""
            className="mt-0.5 size-10 shrink-0 rounded-full bg-black"
          />
        )}

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            {customSender ? (
              <span
                className="rounded-[3px] border border-dashed px-1 text-sm font-medium"
                style={{ borderColor: DISCORD.muted, color: DISCORD.header }}
              >
                웹훅 이름
              </span>
            ) : (
              <span className="font-medium" style={{ color: DISCORD.header }}>
                치직
              </span>
            )}
            <span
              className="rounded-[3px] px-[0.275rem] text-[10px] leading-[15px] font-semibold text-white"
              style={{ backgroundColor: DISCORD.blurple }}
            >
              앱
            </span>
            <span className="ml-0.5 text-xs" style={{ color: DISCORD.muted }}>
              {timestampLabel}
            </span>
          </div>

          {content.trim() && (
            <p className="break-words whitespace-pre-wrap">
              <MessageContent content={content} channelNames={channelNames} />
            </p>
          )}

          {isEmpty && (
            <p className="text-sm italic" style={{ color: DISCORD.muted }}>
              보낼 내용이 없어 알림이 전송되지 않아요. 메시지를 입력하거나
              임베드·버튼 중 하나를 켜주세요.
            </p>
          )}

          {!disableEmbed && (
            <div
              className="mt-1 grid max-w-[432px] rounded-[4px] border-l-4 py-2 pr-4 pl-3"
              style={{
                backgroundColor: DISCORD.embed,
                borderColor: toCssColor(embedColor),
              }}
            >
              <div className="mt-1 flex items-center gap-2">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={getChzzkChannelImageUrl(live.channelImageUrl)}
                  alt=""
                  className="size-6 rounded-full object-cover"
                />
                <span
                  className="text-sm font-semibold"
                  style={{ color: DISCORD.header }}
                >
                  {live.channelName}
                </span>
              </div>

              <p
                className="mt-2 font-semibold break-words"
                style={{ color: DISCORD.link }}
              >
                {live.title}
              </p>
              <p className="mt-2 text-sm">
                {live.channelName} 님이 방송을 시작했습니다.
              </p>

              <div className="mt-2 grid gap-2 text-sm">
                <EmbedField name="카테고리">{live.category}</EmbedField>
                {tags.length > 0 && (
                  <EmbedField name="태그">
                    <span className="flex flex-wrap gap-1">
                      {tags.map((tag) => (
                        <code
                          key={tag}
                          className="rounded-[4px] px-1 py-px text-[0.85em]"
                          style={{ backgroundColor: DISCORD.code }}
                        >
                          {tag}
                        </code>
                      ))}
                    </span>
                  </EmbedField>
                )}
              </div>

              <LiveThumbnail live={live} />

              <p className="mt-2 text-xs" style={{ color: DISCORD.muted }}>
                chzzk.junah.dev • {timestampLabel}
              </p>
            </div>
          )}

          {!disableButton && (
            <div className="mt-1 py-0.5">
              <span
                className="inline-flex h-8 items-center gap-2 rounded-[3px] px-4 text-sm font-medium text-white"
                style={{ backgroundColor: DISCORD.button }}
              >
                바로가기
                <ExternalLink className="size-4" />
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function EmbedField({
  name,
  children,
}: {
  name: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <p className="font-semibold" style={{ color: DISCORD.header }}>
        {name}
      </p>
      <div>{children}</div>
    </div>
  );
}

function MessageContent({
  content,
  channelNames,
}: {
  content: string;
  channelNames?: Record<string, string>;
}) {
  return content.split(MENTION_PATTERN).map((part, index) => {
    if (index % 2 === 0) return <Fragment key={index}>{part}</Fragment>;

    let label = part;
    if (part.startsWith("<@&")) label = "@역할";
    else if (part.startsWith("<@")) label = "@사용자";
    else if (part.startsWith("<#")) {
      label = `#${channelNames?.[part.slice(2, -1)] ?? "채널"}`;
    }

    return (
      <span
        key={index}
        className="rounded-[3px] px-0.5 font-medium"
        style={{ backgroundColor: "rgba(88, 101, 242, 0.3)", color: "#c9cdfb" }}
      >
        {label}
      </span>
    );
  });
}

/** 방송 썸네일. 실제 이미지가 없으면 방송 화면 느낌의 자리표시자를 그림 */
function LiveThumbnail({ live }: { live: NotificationPreviewLive }) {
  if (live.thumbnailUrl) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={live.thumbnailUrl}
        alt=""
        className="mt-4 aspect-video w-full rounded-[4px] object-cover"
      />
    );
  }

  return (
    <div
      className="relative mt-4 aspect-video w-full overflow-hidden rounded-[4px]"
      style={{
        background:
          "radial-gradient(120% 90% at 50% 110%, rgba(0,229,112,0.35), transparent 60%), linear-gradient(160deg, #10241a 0%, #0b0d12 70%)",
      }}
    >
      {/* 방송 화면의 주사선 질감 */}
      <div
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, rgba(255,255,255,0.05) 0 1px, transparent 1px 3px)",
        }}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={getChzzkChannelImageUrl(live.channelImageUrl)}
          alt=""
          className="size-14 rounded-full object-cover ring-2 ring-[#00e570]/60 ring-offset-4 ring-offset-transparent"
        />
      </div>
      <span className="absolute top-2 left-2 rounded-[3px] bg-[#e5172d] px-1.5 py-0.5 text-[10px] font-bold tracking-wider text-white">
        LIVE
      </span>
    </div>
  );
}
