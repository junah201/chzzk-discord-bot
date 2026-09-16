import routeMap from "./route-map";

export const navLinks = [
  {
    label: "기능",
    href: "/#features",
  },
  {
    label: "통계",
    href: "/#metrics",
  },
  {
    label: "요금제",
    href: "/#pricing",
  },
  {
    label: "문서",
    href: routeMap.DOCS.INSTALLATION,
  },
] as const;
