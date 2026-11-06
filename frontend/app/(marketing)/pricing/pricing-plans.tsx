import routeMap from "@/constants/route-map";
import Link from "next/link";

export const pricingPlans = [
  {
    name: "무료",
    price: "₩0",
    unit: null,
    description: "처음 써 보는 작은 서버에 알맞은 기본 플랜",
    features: ["알림 슬롯 5개", "실시간 알림", "기본 알림 전송"],
    tag: null,
    isRecommended: false,
  },
  {
    name: "슬롯 추가 5개",
    price: "₩3,000",
    unit: "1회 결제",
    description: "알림이 조금 더 필요한 서버를 위한 플랜",
    features: ["알림 슬롯 10개 (5개 추가)", "실시간 알림", "기본 알림 전송"],
    tag: "인기",
    isRecommended: false,
  },
  {
    name: "슬롯 추가 10개",
    price: "₩5,000",
    unit: "1회 결제",
    description: "알림이 많은 중간 규모 서버를 위한 플랜",
    features: ["알림 슬롯 15개 (10개 추가)", "실시간 알림", "기본 알림 전송"],
    tag: null,
    isRecommended: false,
  },
  {
    name: "정기 구독",
    price: "₩2,000",
    unit: "월",
    description: "부가 기능까지 모두 쓰는 큰 서버를 위한 플랜",
    features: [
      "알림 슬롯 250개",
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
    tag: "추천",
    isRecommended: true,
  },
] as const;
