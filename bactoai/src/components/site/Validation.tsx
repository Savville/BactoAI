export function Validation() {
  const stats = [
    { k: "1,800+", v: "Training bacterial genomes" },
    { k: "3", v: "Antibiotics currently modeled" },
    { k: "0.952", v: "ROC-AUC — Meropenem (internal)" },
  ];
  return (
    <section id="validation" className="py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <div className="text-sm font-semibold text-primary uppercase tracking-widest">
              Validation
            </div>
            <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
              Evidence-based development.
            </h2>
            <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
              Our machine learning models are developed on curated bacterial genomes and rigorously
              evaluated. Prospective clinical validation is ongoing with partner laboratories.
            </p>
            <ul className="mt-6 space-y-2 text-sm text-muted-foreground list-disc pl-5">
              <li>Trained on curated public bacterial genome datasets</li>
              <li>Internal cross-validated performance metrics</li>
              <li>Clinical validation studies in progress</li>
            </ul>
          </div>
          <div className="grid gap-4">
            {stats.map((s) => (
              <div
                key={s.k}
                className="rounded-2xl border border-border bg-card p-8 shadow-soft flex items-center justify-between"
              >
                <div>
                  <div className="text-4xl md:text-5xl font-bold text-gradient tracking-tight">
                    {s.k}
                  </div>
                  <div className="mt-1 text-sm text-muted-foreground">{s.v}</div>
                </div>
              </div>
            ))}
            <p className="text-xs text-muted-foreground/70">
              Reported figures reflect internal model development. Performance on prospective
              clinical isolates will be reported upon completion of ongoing validation.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
