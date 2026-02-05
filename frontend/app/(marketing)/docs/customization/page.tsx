import { DocsContainer } from "@/components/docs/docs-ui";
import {
  PolicyCallout,
  PolicyTable,
  PolicyTbody,
  PolicyTd,
  PolicyTh,
  PolicyThead,
  PolicyTr,
} from "@/components/policy";
import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "메시지 커스텀 - 치직 문서",
};

export default function CustomizationPage() {
  return (
    <DocsContainer title="3. 메시지 커스텀 (멘션)">
      <PolicyCallout className="my-0">
        방송 시작 알림 메시지에 전체 멘션, 특정 유저, 혹은 역할을 지정하여
        알림을 보낼 수 있습니다. 멘션 기능을 정상적으로 사용하기 위해서는{" "}
        <strong>디스코드 권한 설정</strong>이 필수적입니다.
      </PolicyCallout>

      <h2>전체 멘션 (@everyone, @here)</h2>
      <p>
        서버의 모든 인원을 호출하려면 커스텀 메시지에 아래 텍스트를 그대로
        입력하세요. 별도의 ID가 필요하지 않습니다.
      </p>
      <ul>
        <li>
          <code>@everyone</code> : 서버에 있는 <strong>모든 사람</strong>에게
          알림을 보냅니다.
        </li>
        <li>
          <code>@here</code> : 현재 <strong>접속 중(온라인)인 사람</strong>
          에게만 알림을 보냅니다.
        </li>
      </ul>

      {/* ✨ 권한 경고 Callout 추가 ✨ */}
      <PolicyCallout variant="warning" title="멘션이 작동하지 않나요?">
        <p>
          봇이 역할을 멘션하거나 <code>@everyone</code>을 사용하려면, 디스코드
          채널 설정에서 치직 봇에게{" "}
          <strong>‘@everyone, @here 및 모든 역할 멘션하기’</strong> 권한을
          반드시 허용해줘야 합니다.
        </p>
      </PolicyCallout>

      {/* 2. 특정 유저 멘션 */}
      <h2>특정 유저 멘션하기</h2>
      <p>
        특정인의 ID를 알아야 합니다. 디스코드 설정 {`>`} 고급에서{" "}
        <strong>개발자 모드</strong>를 켜주세요.
      </p>
      <ol>
        <li>
          서버의 유저 목록에서 원하는 유저를 우클릭한 후{" "}
          <strong>ID 복사</strong>를 누릅니다.
        </li>
        <li>
          커스텀 메시지에 <code>&lt;@유저ID&gt;</code> 형식으로 입력합니다.
        </li>
      </ol>
      <PolicyCallout title="유저 멘션 예시">
        ID가 <code>123456789</code>라면 👉 <code>&lt;@123456789&gt;</code> 입력
      </PolicyCallout>

      {/* 3. 특정 역할 멘션 */}
      <h2>특정 역할 멘션하기</h2>
      <p>
        특정 역할의 ID를 알아야 합니다. 디스코드 설정 {`>`} 고급에서{" "}
        <strong>개발자 모드</strong>를 켜주세요.
      </p>
      <ol>
        <li>
          서버 설정 {`>`} <strong>역할</strong> 탭으로 이동합니다.
        </li>
        <li>
          멘션할 역할을 우클릭하고 <strong>ID 복사</strong>를 누릅니다.
        </li>
        <li>
          커스텀 메시지에 <code>&lt;@&amp;역할ID&gt;</code> 형식으로 입력합니다.
          <br />
          (중간에 <code>&amp;</code> 기호가 들어가는 점을 주의하세요!)
        </li>
      </ol>
      <PolicyCallout title="역할 멘션 예시">
        ID가 <code>987654321</code>라면 👉 <code>&lt;@&amp;987654321&gt;</code>{" "}
        입력
      </PolicyCallout>

      <h2>텍스트 꾸미기 (Markdown)</h2>
      <p>
        디스코드 채팅에서 사용되는 마크다운 문법을 커스텀 메시지에도 그대로
        적용할 수 있습니다.
      </p>

      <PolicyTable>
        <PolicyThead>
          <PolicyTh className="min-w-[100px]">효과</PolicyTh>
          <PolicyTh className="min-w-[150px]">입력 문법</PolicyTh>
          <PolicyTh className="min-w-[150px]">미리보기</PolicyTh>
        </PolicyThead>
        <PolicyTbody>
          <PolicyTr>
            <PolicyTd>
              <strong>굵게 (Bold)</strong>
            </PolicyTd>
            <PolicyTd>
              <code>**텍스트**</code>
            </PolicyTd>
            <PolicyTd className="font-bold">텍스트</PolicyTd>
          </PolicyTr>
          <PolicyTr>
            <PolicyTd>기울임 (Italic)</PolicyTd>
            <PolicyTd>
              <code>*텍스트*</code>
            </PolicyTd>
            <PolicyTd className="italic">텍스트</PolicyTd>
          </PolicyTr>
          <PolicyTr>
            <PolicyTd>
              <u>밑줄 (Underline)</u>
            </PolicyTd>
            <PolicyTd>
              <code>__텍스트__</code>
            </PolicyTd>
            <PolicyTd className="underline decoration-1">텍스트</PolicyTd>
          </PolicyTr>
          <PolicyTr>
            <PolicyTd>
              <del>취소선 (Strike)</del>
            </PolicyTd>
            <PolicyTd>
              <code>~~텍스트~~</code>
            </PolicyTd>
            <PolicyTd className="line-through">텍스트</PolicyTd>
          </PolicyTr>
          <PolicyTr>
            <PolicyTd>가려짐 (Spoiler)</PolicyTd>
            <PolicyTd>
              <code>||텍스트||</code>
            </PolicyTd>
            <PolicyTd>
              <span className="bg-foreground/20 rounded px-1 cursor-pointer select-none">
                클릭해서 보기
              </span>
            </PolicyTd>
          </PolicyTr>
          <PolicyTr>
            <PolicyTd>인용구 (Quote)</PolicyTd>
            <PolicyTd>
              <code>{`> 텍스트`}</code>
            </PolicyTd>
            <PolicyTd className="border-l-2 border-foreground/50 pl-2 text-muted-foreground">
              텍스트
            </PolicyTd>
          </PolicyTr>
          <PolicyTr>
            <PolicyTd>코드 블록</PolicyTd>
            <PolicyTd>
              <code>`텍스트`</code>
            </PolicyTd>
            <PolicyTd>
              <code className="bg-secondary px-1 py-0.5 rounded text-xs">
                텍스트
              </code>
            </PolicyTd>
          </PolicyTr>
          <PolicyTr>
            <PolicyTd>하이퍼링크</PolicyTd>
            <PolicyTd>
              <code>[치직 대시보드](https://chzzk.junah.dev)</code>
            </PolicyTd>
            <PolicyTd>
              <Link
                href="https://chzzk.junah.dev"
                className="text-primary hover:underline"
              >
                치직 대시보드
              </Link>
            </PolicyTd>
          </PolicyTr>
        </PolicyTbody>
      </PolicyTable>
      <PolicyCallout title="더 많은 디스코드 마크다운 문법 보기">
        <a
          href="https://support.discord.com/hc/ko/articles/210298617"
          target="_blank"
          rel="noreferrer"
        >
          디스코드 공식 마크다운 가이드
        </a>
        에서 전체 문법을 확인할 수 있습니다.
      </PolicyCallout>
    </DocsContainer>
  );
}
