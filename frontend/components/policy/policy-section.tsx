interface PolicySectionProps {
  id: string;
  index: number;
  title: string;
  children: React.ReactNode;
}

export function PolicySection({
  id,
  index,
  title,
  children,
}: PolicySectionProps) {
  return (
    <section id={id} className="mb-16 scroll-mt-32">
      <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
        <span className="text-primary">{String(index).padStart(2, "0")}.</span>
        {title}
      </h2>

      <div
        className="bg-card border border-border rounded-xl p-6 shadow-sm
        text-foreground/90 leading-relaxed

        /* 1. 기본 텍스트 스타일 */
        [&_p]:mb-4 [&_p:last-child]:mb-0

        /* 2. 메인 리스트 스타일 (ol, ul) */
        [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-2 [&_ol]:mb-4 [&_ol]:marker:text-muted-foreground
        [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-2 [&_ul]:mb-4 [&_ul]:marker:text-muted-foreground

        /* 3. ✨ 중첩 리스트 (Nested List) 스타일 추가 ✨ */
        /* li 안에 있는 ul은 간격을 좁히고, 글씨를 작고 연하게 만듭니다. */
        [&_li_ul]:mt-1
        [&_li_ul]:mb-1
        [&_li_ul]:space-y-1
        [&_li_ul]:text-sm
        [&_li_ul]:text-muted-foreground

        /* 링크, 강조 스타일 등 */
        [&_a]:text-primary [&_a]:underline [&_a]:underline-offset-4 hover:[&_a]:text-primary/80
        [&_strong]:font-semibold [&_strong]:text-foreground
      "
      >
        {children}
      </div>
    </section>
  );
}
