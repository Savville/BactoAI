export function Roadmap() {
  const items = [
    {
      t: "BIK Ventures pitch event · May 2026",
      d: "Represented BactoAI at Kenyatta University's startup pitch showcase, with coverage in print and on BIK's channels.",
    },
    { t: "Prototype completed", d: "Working AI pipeline with initial antibiotic models." },
    { t: "Cloud deployment", d: "Secure, scalable, browser-based platform." },
    { t: "Hospital pilots", d: "Deployments with clinical partners in East Africa." },
    { t: "Clinical validation", d: "Prospective studies on real clinical isolates." },
    { t: "Regulatory pathway", d: "Engagement with regulatory bodies for clinical use." },
    { t: "Commercial launch", d: "General availability for laboratories and hospitals." },
    { t: "East Africa expansion", d: "Regional rollout & AMR surveillance partnerships." },
  ];
  return (
    <section id="roadmap" className="py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Roadmap · 2026 →
          </div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            From prototype to regional platform.
          </h2>
        </div>

        <div className="mt-16 relative">
          <div className="absolute left-4 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-primary via-accent to-transparent" />
          <div className="space-y-10">
            {items.map((it, i) => (
              <div
                key={it.t}
                className={`relative md:grid md:grid-cols-2 md:gap-12 ${i % 2 ? "" : ""}`}
              >
                <div
                  className={`pl-12 md:pl-0 ${i % 2 ? "md:col-start-2 md:text-left md:pl-12" : "md:text-right md:pr-12"}`}
                >
                  <div className="inline-block rounded-2xl border border-border bg-card p-5 shadow-soft max-w-md">
                    <div className="text-lg font-semibold text-foreground">{it.t}</div>
                    <p className="mt-1 text-sm text-muted-foreground">{it.d}</p>
                  </div>
                </div>
                <div className="absolute left-4 md:left-1/2 top-3 -translate-x-1/2 w-4 h-4 rounded-full bg-primary ring-4 ring-background" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
