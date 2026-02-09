import type { Metadata } from "next";
import "./globals.css";
import Providers from "./providers";
import { GoogleAnalytics } from "@next/third-parties/google";
import { GoogleAdSense } from "./google-adsense";

export const metadata: Metadata = {
  title: "치직 - 놓치지 않는 방송 알림, 치직",
  description:
    "좋아하는 스트리머의 방송 시작을 디스코드로 실시간 알림받으세요. 간편한 설정, 빠른 알림, 완벽한 통합.",
  keywords: [
    "치지직",
    "치직",
    "CHZZK",
    "치지직 방송 알림",
    "치지직 알림 봇",
    "디스코드 방송 알림",
    "디스코드 봇",
    "디스코드 치지직 알림",
    "스트리머 알림",
    "방송 시작 알림",
    "치지직 연동",
    "실시간 알림 봇",
  ],
  icons: {
    icon: [
      { url: "https://chzzk.junah.dev/favicon-16.png", sizes: "16x16" },
      { url: "https://chzzk.junah.dev/favicon-32.png", sizes: "32x32" },
      { url: "https://chzzk.junah.dev/favicon-48.png", sizes: "48x48" },
      { url: "https://chzzk.junah.dev/favicon-96x96.png", sizes: "96x96" },
      { url: "https://chzzk.junah.dev/favicon-192.png", sizes: "192x192" },
      { url: "https://chzzk.junah.dev/favicon-512.png", sizes: "512x512" },
    ],
    apple: {
      url: "https://chzzk.junah.dev/favicon-180.png",
      sizes: "180x180",
    },
  },
  openGraph: {
    title: "치직 - 놓치지 않는 방송 알림, 치직",
    siteName: "치직",
    description:
      "좋아하는 스트리머의 방송 시작을 디스코드로 실시간 알림받으세요. 간편한 설정, 빠른 알림, 완벽한 통합.",
    locale: "ko_KR",
    type: "website",
  },
  twitter: {
    title: "치직 - 놓치지 않는 방송 알림, 치직",
    description:
      "좋아하는 스트리머의 방송 시작을 디스코드로 실시간 알림받으세요. 간편한 설정, 빠른 알림, 완벽한 통합.",
    card: "summary_large_image",
  },
  other: {
    "google-adsense-account":
      process.env.NEXT_PUBLIC_GOOGLE_ADSENSE_CLIENT_ID || "",
  },
};

export const viewport = {
  themeColor: "#00e570",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <GoogleAnalytics gaId={process.env.NEXT_PUBLIC_GA_ID || ""} />
      <GoogleAdSense />
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
