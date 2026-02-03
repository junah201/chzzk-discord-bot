import { ReactNode } from "react";
import { Toaster } from "@/components/ui/sonner";
import ReactQueryProvider from "./react-query-provider";

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <ReactQueryProvider>
      {children}
      <Toaster />
    </ReactQueryProvider>
  );
}
