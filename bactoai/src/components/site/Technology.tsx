export function Technology() {
  const stack = [
    "Python",
    "Machine Learning",
    "Bioinformatics",
    "Cloud Computing",
    "Genomics",
    "Artificial Intelligence",
  ];
  const flow = [
    "Genome Sequence",
    "Feature Extraction",
    "ML Models",
    "Resistance Prediction",
    "Clinical Report",
  ];
  return (
    <section id="technology" className="py-24 md:py-32 bg-card/40">
      <div className="mx-auto max-w-7xl px-6">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Technology
          </div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            A modern architecture, purpose-built for genomic AI.
          </h2>
        </div>

        <div className="mt-16 rounded-3xl border border-border bg-background p-8 md:p-12 shadow-soft">
          <div className="grid gap-4 md:grid-cols-5">
            {flow.map((f, i) => (
              <div key={f} className="relative">
                <div className="rounded-2xl bg-gradient-hero text-white p-5 h-full text-center shadow-soft">
                  <div className="text-[10px] uppercase tracking-widest opacity-80">
                    Stage {i + 1}
                  </div>
                  <div className="mt-2 font-semibold text-sm md:text-base">{f}</div>
                </div>
                {i < flow.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-2 w-4 h-0.5 bg-primary/40" />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="mt-10 flex flex-wrap justify-center gap-3">
          {stack.map((s) => (
            <span
              key={s}
              className="rounded-full border border-border bg-background px-4 py-2 text-sm font-medium text-muted-foreground"
            >
              {s}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
