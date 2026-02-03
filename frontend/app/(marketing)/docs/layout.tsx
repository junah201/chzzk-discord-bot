import { GridPattern } from "@/components/ui/grid-pattern";
import { GlowEffect } from "@/components/ui/glow-effect";
import { DocsSidebar } from "./components/docs-sidebar";
import { BookOpen } from "lucide-react";

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <section className="relative min-h-screen pt-32 pb-20">
      <div className="absolute inset-0 pointer-events-none">
        <GlowEffect
          variant="breathing"
          duration={10}
          className="top-0 left-1/4 w-96 h-96 bg-primary/5"
        />
        <GlowEffect
          variant="breathing"
          duration={12}
          delay={2}
          className="bottom-0 right-1/4 w-96 h-96 bg-emerald-500/5"
        />
        <GridPattern mask="radial" />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10 break-keep">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            <aside className="lg:col-span-3 lg:sticky lg:top-32 self-start">
              <DocsSidebar />
            </aside>

            <main className="lg:col-span-9">
              <div className="bg-linear-to-br from-primary/10 to-emerald-500/5 border-l-4 border-primary rounded-xl p-6 flex gap-4 mb-12">
                <BookOpen className="w-6 h-6 text-primary shrink-0 mt-1" />
                <div>
                  <p className="text-lg font-semibold mb-2">치직 가이드</p>
                  <p className="text-sm text-muted-foreground">
                    치직 봇의 설치부터 고급 기능까지, 서비스 이용을 위한 공식
                    가이드입니다.
                  </p>
                </div>
              </div>
              {children}
            </main>
          </div>
        </div>
      </div>
    </section>
  );
}
