import { Plus } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import routeMap from "@/constants/route-map";

const faqs: { question: string; answer: ReactNode }[] = [
  {
    question: "슬롯은 무엇인가요?",
    answer:
      "알림 1개를 등록할 수 있는 자리입니다. 치지직 채널 하나를 디스코드 채널 한 곳에 보내는 알림이 슬롯 1개를 씁니다. 같은 스트리머를 두 채널에 보내면 2개를 씁니다.",
  },
  {
    question: "1회 구매하면 슬롯이 몇 개가 되나요?",
    answer:
      "기본 5개에 더해집니다. 슬롯 추가 5개는 총 10개, 슬롯 추가 10개는 총 15개가 되고, 기간 제한 없이 계속 쓸 수 있습니다.",
  },
  {
    question: "구독 중에도 슬롯을 더 살 수 있나요?",
    answer: (
      <>
        구독 중에는 슬롯을 따로 살 수 없습니다. 구독하면 이미 250개를 쓸 수
        있고, 그보다 더 필요하면{" "}
        <Link
          href={routeMap.REDIRECTS.SUPPORT_SERVER}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary underline underline-offset-4 transition-colors hover:text-primary/80"
        >
          서포트 서버
        </Link>
        로 문의해 주세요.
      </>
    ),
  },
  {
    question: "구독 기간은 얼마나 되나요?",
    answer:
      "결제가 확인된 날부터 한 달입니다. 끝나기 전에 다시 결제하면 남은 기간에 한 달이 더해집니다.",
  },
  {
    question: "구독이 끝나면 어떻게 되나요?",
    answer:
      "슬롯 수가 구독 전으로 돌아가고, 커스텀 웹훅, 임베드 색상, 공지 채널 자동 게시는 더 이상 적용되지 않습니다. 알림은 치직 봇이 기본 형식으로 보냅니다.",
  },
];

export default function PricingFaq() {
  return (
    <section
      aria-labelledby="pricing-faq-heading"
      className="grid gap-8 border-t border-border pt-12 md:grid-cols-[1fr_1.4fr]"
    >
      <h2
        id="pricing-faq-heading"
        className="text-2xl font-bold tracking-tight"
      >
        자주 묻는 질문
      </h2>
      <div className="border-t border-border">
        {faqs.map((faq) => (
          <details key={faq.question} className="group border-b border-border">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-5 font-medium transition-colors hover:text-primary [&::-webkit-details-marker]:hidden">
              {faq.question}
              <Plus className="size-4 shrink-0 text-muted-foreground transition-transform duration-200 group-open:rotate-45" />
            </summary>
            <p className="pb-5 text-sm leading-relaxed text-muted-foreground">
              {faq.answer}
            </p>
          </details>
        ))}
      </div>
    </section>
  );
}
