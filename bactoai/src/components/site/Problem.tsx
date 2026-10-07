import { AlertTriangle, Clock, Users } from "lucide-react";

export function Problem() {
  const stats = [
    {
      icon: AlertTriangle,
      k: "1.27M+",
      v: "Deaths directly attributable to AMR each year worldwide.",
    },
    {
      icon: Clock,
      k: "48–72 hrs",
      v: "Traditional antimicrobial susceptibility testing turnaround.",
    },
    {
      icon: Users,
      k: "Millions",
      v: "Patients receive empirical antibiotics before lab confirmation.",
    },
  ];
  return (
    <section id="problem" className="py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            The Problem
          </div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight leading-tight text-foreground">
            Antimicrobial resistance is one of the greatest global health threats.
          </h2>
          <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
            Traditional culture-based diagnostics delay clinical decisions, contributing to
            inappropriate antibiotic use, prolonged hospital stays, and increasing antimicrobial
            resistance.
          </p>
        </div>
        <div className="mt-16 grid gap-6 md:grid-cols-3">
          {stats.map((s) => (
            <div
              key={s.k}
              className="rounded-2xl border border-border bg-card p-8 shadow-soft hover:shadow-elegant hover:-translate-y-1 transition-all"
            >
              <s.icon className="text-primary" size={28} />
              <div className="mt-6 text-5xl font-bold text-foreground tracking-tight">{s.k}</div>
              <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{s.v}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
