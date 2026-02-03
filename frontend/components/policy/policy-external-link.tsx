import { cn } from "@/lib/utils";
import { ExternalLink } from "lucide-react";

interface PolicyExternalLinkProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  description?: string;
  href: string;
  label: string;
}

export function PolicyExternalLink({
  title,
  description,
  href,
  label,
  className,
  ...props
}: PolicyExternalLinkProps) {
  return (
    <div
      {...props}
      className={cn(
        "bg-card border border-border rounded-lg p-4 hover:border-primary/50 transition-colors",
        className,
      )}
    >
      <strong className="block mb-2 text-primary">{title}</strong>
      {description && <p className="text-sm mb-1">{description}</p>}
      <a
        href={href}
        target="_blank"
        rel="noreferrer"
        className="text-xs text-muted-foreground hover:text-primary hover:underline flex items-center gap-1"
      >
        {label} <ExternalLink className="w-3 h-3" />
      </a>
    </div>
  );
}
