import { ReactNode } from "react";
import { Toaster } from "@/components/ui/sonner";
import ReactQueryProvider from "./react-query-provider";
import { TooltipProvider } from "@/components/ui/tooltip";

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <ReactQueryProvider>
      <TooltipProvider>
        {children}
        <Toaster />
      </TooltipProvider>
    </ReactQueryProvider>
  );
}
