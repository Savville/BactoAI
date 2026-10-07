import { FlaskConical, Dna, BrainCircuit, FileCheck, Pill, User } from "lucide-react";

const steps = [
  { icon: User, title: "Patient", desc: "Clinical presentation & bacterial infection identified." },
  { icon: FlaskConical, title: "Sample", desc: "Bacterial isolate collected from the patient." },
  { icon: Dna, title: "Sequencing", desc: "Whole genome sequence generated (FASTA / FASTQ)." },
  { icon: BrainCircuit, title: "BactoAI", desc: "ML models analyze genomic features." },
  { icon: FileCheck, title: "Prediction", desc: "Resistance profile & confidence per antibiotic." },
  { icon: Pill, title: "Treatment", desc: "Clinician makes an informed prescribing decision." },
];

export function Solution() {
  return (
    <section id="solution" className="py-24 md:py-32 bg-card/40">
      <div className="mx-auto max-w-7xl px-6">
        <div className="max-w-3xl mx-auto text-center">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Our Solution
          </div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Meet <span className="text-gradient">BactoAI</span>
          </h2>
          <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
            BactoAI analyzes bacterial genomic data using machine learning to predict antibiotic
            resistance before conventional laboratory testing is completed.
          </p>
        </div>

        <div className="journey-timeline mt-12 md:mt-20 grid gap-0 md:gap-4 md:grid-cols-3 lg:grid-cols-6">
          {steps.map((s, i) => (
            <div
              key={s.title}
              className="relative border-l-2 border-primary/40 pl-6 pb-6 md:border-0 md:pl-0 md:pb-0"
            >
              <div className="rounded-lg border border-border bg-background p-5 h-full shadow-soft hover:border-primary/30 transition">
                <span
                  className="absolute -left-2 top-7 h-3.5 w-3.5 rounded-full bg-primary md:hidden"
                  aria-hidden
                />
                <div className="flex items-center justify-center w-11 h-11 rounded-xl bg-primary/10 text-primary">
                  <s.icon size={20} />
                </div>
                <div className="mt-4 text-xs font-semibold text-muted-foreground">STEP {i + 1}</div>
                <div className="mt-1 text-base font-semibold text-foreground">{s.title}</div>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
              </div>
              {i < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-2 w-4 h-px bg-gradient-to-r from-primary/40 to-transparent" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
