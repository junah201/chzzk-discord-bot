import { cn } from "@/lib/utils";

interface PolicyTableProps {
  children: React.ReactNode;
  className?: string;
}

export function PolicyTable({ children, className }: PolicyTableProps) {
  return (
    <div className="w-full overflow-x-auto rounded-lg border border-border bg-card">
      <table className={cn("w-full text-sm text-left", className)}>
        {children}
      </table>
    </div>
  );
}

export function PolicyTbody({ children, className }: PolicyTableProps) {
  return (
    <tbody className={cn("divide-y divide-border", className)}>
      {children}
    </tbody>
  );
}

export function PolicyThead({ children, className }: PolicyTableProps) {
  return (
    <thead
      className={cn(
        "text-xs uppercase bg-secondary/50 text-muted-foreground border-b border-border",
        className,
      )}
    >
      <tr>{children}</tr>
    </thead>
  );
}

export function PolicyTh({ children, className }: PolicyTableProps) {
  return (
    <th className={cn("px-4 py-3 whitespace-nowrap font-medium", className)}>
      {children}
    </th>
  );
}

export function PolicyTr({ children, className }: PolicyTableProps) {
  return (
    <tr
      className={cn(
        "bg-card hover:bg-secondary/10 transition-colors border-b border-border last:border-0",
        className,
      )}
    >
      {children}
    </tr>
  );
}

export function PolicyTd({ children, className }: PolicyTableProps) {
  return <td className={cn("px-4 py-3 align-top", className)}>{children}</td>;
}
