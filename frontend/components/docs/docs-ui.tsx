import { cn } from "@/lib/utils";

export function DocsContainer({
  title,
  children,
  className,
}: {
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "animate-in fade-in slide-in-from-bottom-4 duration-500",
        className,
      )}
    >
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-3">
        {title}
      </h1>

      <div
        className="bg-card border border-border rounded-xl p-6 shadow-sm text-foreground/90 leading-relaxed

        /* [Typography] 기본 텍스트 및 리스트 스타일 통합 */
        [&_p]:mb-4 [&_p:last-child]:mb-0

        /* 순서 있는 목록 (Step 1, 2, 3...) */
        [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-3 [&_ol]:mb-6 [&_ol]:marker:text-primary [&_ol]:marker:font-semibold

        /* 순서 없는 목록 (Dot) */
        [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-2 [&_ul]:mb-4 [&_ul]:marker:text-muted-foreground

        /* 중첩 리스트 (Nested) */
        [&_li_ul]:mt-2 [&_li_ul]:mb-2 [&_li_ul]:space-y-1 [&_li_ul]:text-sm [&_li_ul]:text-muted-foreground

        /* 소제목 (Markdown ##) */
        [&_h2]:text-xl [&_h2]:font-bold [&_h2]:text-foreground [&_h2]:my-4 [&_h2:first-child]:mt-0 [&_h2]:flex [&_h2]:items-center [&_h2]:gap-2 [&_h2]:border-b [&_h2]:border-border/50 [&_h2]:pb-2

        /* 인라인 코드 (Highlight) */
        [&_code]:bg-secondary [&_code]:text-primary [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded-md [&_code]:font-mono [&_code]:text-sm

        /* 인용문 */
        [&_blockquote]:border-l-4 [&_blockquote]:border-primary/50 [&_blockquote]:pl-4 [&_blockquote]:italic [&_blockquote]:text-muted-foreground [&_blockquote]:my-4 [&_blockquote]:bg-secondary/10 [&_blockquote]:p-4 [&_blockquote]:rounded-r-lg

        /* 링크 */
        [&_a]:text-primary [&_a]:underline [&_a]:underline-offset-4 hover:[&_a]:text-primary/80
      "
      >
        {children}
      </div>
    </div>
  );
}
