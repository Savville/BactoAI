import { HeartPulse, Stethoscope, Zap, ShieldCheck, TrendingUp, Globe2 } from "lucide-react";

const impact = [
  { icon: Stethoscope, t: "Reduce inappropriate antibiotic use" },
  { icon: HeartPulse, t: "Support clinicians at the point of care" },
  { icon: Zap, t: "Accelerate diagnostics from days to minutes" },
  { icon: TrendingUp, t: "Improve patient outcomes" },
  { icon: ShieldCheck, t: "Strengthen antimicrobial stewardship" },
  { icon: Globe2, t: "Support genomic surveillance globally" },
];

export function Impact() {
  return (
    <section id="impact" className="py-24 md:py-32 bg-card/40">
      <div className="mx-auto max-w-7xl px-6">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">Impact</div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Faster answers. Better antibiotics. Stronger systems.
          </h2>
        </div>
        <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {impact.map((i) => (
            <div
              key={i.t}
              className="rounded-2xl border border-border bg-background p-6 flex items-start gap-4 hover:border-primary/40 transition"
            >
              <div className="w-11 h-11 rounded-xl bg-gradient-hero text-white flex items-center justify-center shrink-0">
                <i.icon size={20} />
              </div>
              <div className="text-base font-semibold text-foreground pt-1.5">{i.t}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
