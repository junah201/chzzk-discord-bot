import routeMap from "@/constants/route-map";
import Link from "next/link";

export const pricingPlans = [
  {
    name: "Free",
    price: "₩0",
    period: "무료",
    slotsText: "알림 슬롯 5개",
    description: "작은 서버에 알맞은 기본 플랜",
    icon: "zap" as const,
    features: ["슬롯 5개", "실시간 알림", "기본 알림 전송"],
    badge: "처음 써 본다면",
    buttonVariant: "outline" as const,
    isPopular: false,
    isRecommended: false,
  },
  {
    name: "₩3,000 단일 구매",
    price: "₩3,000",
    period: "1회 구매",
    slotsText: "슬롯 5개 추가 (총 10개)",
    description: "한 번만 결제하면 되는 플랜",
    icon: "star" as const,
    features: ["슬롯 10개", "실시간 알림", "기본 알림 전송"],
    badge: "알림이 조금 더 필요하다면",
    buttonVariant: "primary" as const,
    isPopular: true,
    isRecommended: false,
  },
  {
    name: "₩5,000 단일 구매",
    price: "₩5,000",
    period: "1회 구매",
    slotsText: "슬롯 10개 추가 (총 15개)",
    description: "알림이 많은 중간 규모 서버를 위한 플랜",
    icon: "shield" as const,
    features: ["슬롯 15개", "실시간 알림", "기본 알림 전송"],
    badge: "중간 규모 서버라면",
    buttonVariant: "outline" as const,
    isPopular: false,
    isRecommended: false,
  },
  {
    name: "월 ₩2,000 정기 구독",
    price: "월 ₩2,000",
    period: "정기 구독",
    slotsText: "슬롯 250개와 구독자 전용 기능",
    description: "큰 서버를 위한 프리미엄 플랜",
    icon: "crown" as const,
    features: [
      "슬롯 250개",
      "실시간 알림",
      <>
        <Link
          href={routeMap.DOCS.CUSTOM_WEBHOOK}
          className="underline hover:text-primary transition-colors "
        >
          커스텀 웹훅
        </Link>{" "}
        기능 지원
      </>,
      "임베드 색상 변경",
      "고급 필터링 기능 (지원 예정)",
    ],
    badge: "부가 기능까지 모두",
    buttonVariant: "primary" as const,
    isPopular: false,
    isRecommended: true,
  },
] as const;
