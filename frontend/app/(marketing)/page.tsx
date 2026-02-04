import { Features } from "./components/features";
import { Hero } from "./components/hero";
import { Metrics } from "./components/metrics";
import { GridPattern } from "@/components/ui/grid-pattern";

export default function Home() {
  return (
    <div>
      <GridPattern position="fixed" mask="fade" />
      <div className="flex-1">
        <Hero />
        <Features />
        <Metrics />
      </div>
    </div>
  );
}
