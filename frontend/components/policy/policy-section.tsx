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

        [&_p]:mb-4 [&_p:last-child]:mb-0

        [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-2 [&_ol]:mb-4 [&_ol]:marker:text-muted-foreground
        [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-2 [&_ul]:mb-4 [&_ul]:marker:text-muted-foreground

        [&_li_ul]:mt-1
        [&_li_ul]:mb-1
        [&_li_ul]:space-y-1
        [&_li_ul]:text-sm
        [&_li_ul]:text-muted-foreground

        [&_a]:text-primary [&_a]:underline [&_a]:underline-offset-4 hover:[&_a]:text-primary/80
        [&_strong]:font-semibold [&_strong]:text-foreground
      "
      >
        {children}
      </div>
    </section>
  );
}
