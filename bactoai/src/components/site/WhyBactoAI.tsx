import { Hospital, Microscope, Globe2 } from "lucide-react";

const cols = [
  {
    icon: Hospital,
    title: "For Hospitals",
    items: [
      "Earlier antibiotic decisions",
      "Improved antimicrobial stewardship",
      "Reduced treatment failure",
    ],
  },
  {
    icon: Microscope,
    title: "For Researchers",
    items: ["Resistance surveillance", "Genomic analytics", "Dataset exploration"],
  },
  {
    icon: Globe2,
    title: "For Public Health",
    items: ["National AMR monitoring", "Evidence-driven policy", "Population surveillance"],
  },
];

export function WhyBactoAI() {
  return (
    <section className="py-24 md:py-32 bg-card/40">
      <div className="mx-auto max-w-7xl px-6">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Why BactoAI
          </div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            A genomic prediction engine — the diagnostic layer other AMR tools build on.
          </h2>
          <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
            BactoAI predicts antimicrobial resistance directly from a bacterial genome sequence,
            before or without a completed lab culture. We are not a lab-logistics or sample-booking
            marketplace, and not a guideline-based prescribing chatbot. Those tools move samples or
            protocols faster; BactoAI generates the resistance data point they both depend on.
          </p>
        </div>

        <div className="mt-12 grid gap-4 md:grid-cols-3">
          {[
            {
              label: "Lab-booking / logistics tools",
              body: "Route samples to labs faster — but still wait 48–72 hrs for a culture result.",
            },
            {
              label: "Prescribing-guideline chatbots",
              body: "Apply WHO or national decision trees to symptoms — no organism-specific resistance evidence.",
            },
            {
              label: "BactoAI — genomic prediction",
              body: "Predicts per-antibiotic resistance from the genome in under 10 minutes from genome to result. Complementary infrastructure both categories can plug into.",
              highlight: true,
            },
          ].map((c) => (
            <div
              key={c.label}
              className={`rounded-2xl border p-6 ${
                c.highlight ? "border-primary bg-primary/5" : "border-border bg-background"
              }`}
            >
              <div
                className={`text-sm font-semibold ${c.highlight ? "text-primary" : "text-foreground"}`}
              >
                {c.label}
              </div>
              <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{c.body}</p>
            </div>
          ))}
        </div>

        <div className="mt-16 grid gap-6 md:grid-cols-3">
          {cols.map((c) => (
            <div
              key={c.title}
              className="rounded-3xl border border-border bg-background p-8 shadow-soft hover:shadow-elegant transition-shadow"
            >
              <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-primary/10 text-primary">
                <c.icon size={26} />
              </div>
              <h3 className="mt-6 text-2xl font-bold text-foreground">{c.title}</h3>
              <ul className="mt-6 space-y-3">
                {c.items.map((it) => (
                  <li key={it} className="flex items-start gap-3 text-sm text-muted-foreground">
                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                    {it}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
