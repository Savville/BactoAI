import { ArrowRight } from "lucide-react";

export function PreFooterCTA() {
  return (
    <section className="relative overflow-hidden bg-ink text-white py-20 md:py-28">
      <div className="absolute inset-0 bg-ink-mesh" />
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-40 left-1/3 w-[520px] h-[520px] rounded-full bg-[color:var(--color-teal-glow)]/15 blur-3xl" />
      </div>
      <div className="relative mx-auto max-w-4xl px-6 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-widest text-[color:var(--color-teal-glow-soft)]">
          Ready to transform AMR diagnostics?
        </div>
        <h2 className="mt-6 text-3xl md:text-5xl font-bold tracking-tight text-foreground">
          Bring genome-driven decisions into your hospital or lab.
        </h2>
        <p className="mt-5 text-white/70 text-lg max-w-2xl mx-auto">
          See a live demo of BactoAI on your own isolates, or talk to us about launching a pilot in
          your region.
        </p>
        <div className="mt-10 flex flex-wrap gap-3 justify-center">
          <a
            href="/contact"
            className="group inline-flex items-center gap-2 rounded-full bg-[color:var(--color-teal-glow)] px-7 py-3.5 text-sm font-semibold text-[color:var(--color-ink)] shadow-glow-teal hover:brightness-110 transition"
          >
            Request a Demo{" "}
            <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
          </a>
          <a
            href="mailto:info@bactoai.co.ke"
            className="inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/5 px-7 py-3.5 text-sm font-semibold text-white hover:bg-white/10 transition"
          >
            Contact Sales
          </a>
        </div>
      </div>
    </section>
  );
}
