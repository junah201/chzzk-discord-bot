import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "서버 관리 - 치직 대시보드",
};

export default function ServerLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
