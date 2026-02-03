import { GlowEffect } from "@/components/ui/glow-effect";
import { GridPattern } from "@/components/ui/grid-pattern";

export default function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <main className="flex min-h-screen bg-background text-foreground">
      <GridPattern position="fixed" mask="fade" className="z-0" />
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {/* 왼쪽 상단: Primary Color */}
        <GlowEffect
          variant="breathing"
          duration={10}
          className="top-1/4 left-1/4 w-96 h-96 bg-primary/10"
        />
        {/* 오른쪽 하단: Emerald Color */}
        <GlowEffect
          variant="breathing"
          duration={12}
          delay={2}
          className="bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/10"
        />
      </div>
      <div className="flex-1">{children}</div>
    </main>
  );
}
