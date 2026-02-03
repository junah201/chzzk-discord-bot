// components/policy/PolicyLayout.tsx
"use client";

import { motion } from "motion/react";
import { ChevronRight, AlertCircle } from "lucide-react";
import { useScrollSpy } from "@/hooks/use-scroll-spy";
import { GridPattern } from "@/components/ui/grid-pattern";
import { GlowEffect } from "@/components/ui/glow-effect";
import { cn } from "@/lib/utils";

interface Section {
  id: string;
  title: string;
}

interface PolicyLayoutProps {
  title: string;
  lastUpdated: string;
  notice: {
    title: React.ReactNode;
    description: string;
  };
  sections: Section[];
  children: React.ReactNode;
}

export function PolicyLayout({
  title,
  lastUpdated,
  notice,
  sections,
  children,
}: PolicyLayoutProps) {
  // useScrollSpy에서 activeId만 가져옵니다.
  const activeId = useScrollSpy(sections.map((s) => s.id));

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
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 h-auto">
            <aside className="lg:col-span-3 lg:sticky lg:top-32 self-start">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
                className="bg-card border border-border rounded-2xl p-6"
              >
                <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                  <ChevronRight className="w-5 h-5 text-primary" />
                  목차
                </h3>
                <nav className="space-y-2">
                  {sections.map((section) => (
                    <a
                      key={section.id}
                      href={`#${section.id}`}
                      className={cn(
                        "block w-full text-left px-4 py-2 rounded-lg transition-all text-sm font-medium",
                        {
                          "bg-primary/10 text-primary border-l-4 border-primary translate-x-1":
                            activeId === section.id,
                          "text-muted-foreground hover:text-foreground hover:bg-secondary":
                            activeId !== section.id,
                        },
                      )}
                    >
                      {section.title}
                    </a>
                  ))}
                </nav>
              </motion.div>
            </aside>

            {/* --- 메인 콘텐츠 --- */}
            <main className="lg:col-span-9">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                {/* 페이지 헤더 */}
                <div className="mb-12">
                  <h1 className="text-4xl sm:text-5xl font-bold mb-8 bg-linear-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
                    {title}
                  </h1>
                  <div className="bg-linear-to-br from-primary/10 to-emerald-500/5 border-l-4 border-primary rounded-xl p-6 flex gap-4">
                    <AlertCircle className="w-6 h-6 text-primary shrink-0 mt-1" />
                    <div>
                      <p className="text-lg font-semibold mb-2">
                        {notice.title}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {notice.description}
                      </p>
                    </div>
                  </div>
                </div>

                {/* 약관 본문 영역 */}
                <div className="prose prose-invert max-w-none">
                  {children}

                  {/* 푸터 (최종 수정일) */}
                  <div className="mt-16 bg-linear-to-br from-secondary to-secondary/50 border border-border rounded-xl p-8 text-center">
                    <p className="text-muted-foreground mb-2">최종 수정일</p>
                    <p className="text-lg font-semibold">{lastUpdated}</p>
                  </div>
                </div>
              </motion.div>
            </main>
          </div>
        </div>
      </div>
    </section>
  );
}
