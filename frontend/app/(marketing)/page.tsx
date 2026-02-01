import { Features } from "./components/features";
import { Hero } from "./components/hero";
import { Metrics } from "./components/metrics";

export default function Home() {
  return (
    <div>
      <div
        className="fixed inset-0 z-0 pointer-events-none"
        style={{
          maskImage:
            "linear-gradient(to bottom, transparent 0px, transparent 64px, black 200px, black 80%, transparent 100%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, transparent 0px, transparent 64px, black 200px, black 80%, transparent 100%)",
        }}
      >
        {/* Grid Pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-size-[4rem_4rem]" />
      </div>
      <div className="flex-1">
        <Hero />
        <Features />
        <Metrics />
      </div>
    </div>
  );
}
