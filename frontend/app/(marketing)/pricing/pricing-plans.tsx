import routeMap from "@/constants/route-map";
import Link from "next/link";
import { Fragment } from "react";

export const pricingPlans = [
  {
    id: "free",
    name: "무료",
    shortName: "무료",
    amount: 0,
    slots: 5,
    billing: "무료",
    subscriberFeatures: false,
    price: "₩0",
    unit: null,
    description: "처음 써 보는 작은 서버에 알맞은 기본 플랜",
    features: ["알림 슬롯 5개", "실시간 알림", "기본 알림 전송"],
    tag: null,
    isRecommended: false,
  },
  {
    id: "slot-5",
    name: "슬롯 추가 5개",
    shortName: "+5개",
    amount: 3000,
    slots: 10,
    billing: "1회 결제",
    subscriberFeatures: false,
    price: "₩3,000",
    unit: "1회 결제",
    description: "알림이 조금 더 필요한 서버를 위한 플랜",
    features: ["알림 슬롯 10개 (5개 추가)", "실시간 알림", "기본 알림 전송"],
    tag: "인기",
    isRecommended: false,
  },
  {
    id: "slot-10",
    name: "슬롯 추가 10개",
    shortName: "+10개",
    amount: 5000,
    slots: 15,
    billing: "1회 결제",
    subscriberFeatures: false,
    price: "₩5,000",
    unit: "1회 결제",
    description: "알림이 많은 중간 규모 서버를 위한 플랜",
    features: ["알림 슬롯 15개 (10개 추가)", "실시간 알림", "기본 알림 전송"],
    tag: null,
    isRecommended: false,
  },
  {
    id: "subscription",
    name: "정기 구독",
    shortName: "구독",
    amount: 2000,
    slots: 250,
    billing: "매월 결제",
    subscriberFeatures: true,
    price: "₩2,000",
    unit: "월",
    description: "부가 기능까지 모두 쓰는 큰 서버를 위한 플랜",
    features: [
      "알림 슬롯 250개",
      "실시간 알림",
      <Fragment key="custom-webhook">
        <Link
          href={routeMap.DOCS.CUSTOM_WEBHOOK}
          className="underline hover:text-primary transition-colors "
        >
          커스텀 웹훅
        </Link>{" "}
        기능 지원
      </Fragment>,
      "임베드 색상 변경",
      "고급 필터링 기능 (지원 예정)",
    ],
    tag: "추천",
    isRecommended: true,
  },
] as const;
