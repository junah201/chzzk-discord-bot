"use client";

import routeMap from "@/constants/route-map";
import Link from "next/link";

const footerLinks = [
  {
    title: "제품",
    links: [
      { name: "기능", href: "#features" },
      { name: "통계", href: "#metrics" },
      { name: "문서", href: routeMap.DOCS.HOME },
    ],
  },
  {
    title: "법적 고지",
    links: [
      { name: "이용약관", href: routeMap.TERMS_OF_SERVICE },
      { name: "개인정보처리방침", href: routeMap.PRIVACY_POLICY },
      { name: "쿠키 정책", href: routeMap.COOKIE_POLICY },
    ],
  },
  {
    title: "지원",
    links: [
      {
        name: "서포트 서버",
        href: routeMap.REDIRECTS.SUPPORT_SERVER,
        target: "_blank",
      },
      { name: "FAQ", href: routeMap.DOCS.TROUBLESHOOTING },
    ],
  },
] as const;

export const FooterNav = () => {
  return (
    <>
      {footerLinks.map((section) => (
        <div key={section.title}>
          <h3 className="font-semibold mb-4 text-foreground">
            {section.title}
          </h3>
          <ul className="space-y-3">
            {section.links.map((link) => (
              <li key={link.name}>
                <Link
                  href={link.href}
                  className="text-muted-foreground hover:text-primary transition-colors inline-block"
                >
                  {link.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </>
  );
};
