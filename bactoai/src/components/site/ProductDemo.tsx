import { CheckCircle2 } from "lucide-react";
import { LiveAnalyzer } from "./LiveAnalyzer";
export function ProductDemo() {

  return (
    <section id="demo" className="py-24 md:py-32 bg-card/30">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid gap-10 lg:grid-cols-[.9fr_1.1fr] items-start [&>div]:min-w-0">
          <div className="lg:sticky lg:top-28">
            <div className="text-sm font-semibold text-primary uppercase tracking-widest">
              Live Product Demo
            </div>
            <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
              Try it yourself. Watch a genome become a treatment recommendation.
            </h2>
            <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
              Upload a FASTA or FASTQ genome file to securely test the BactoAI
              workflow — from pre-processing and model inference to a clinician-ready report.
            </p>
            <ul className="mt-8 space-y-3 text-sm text-muted-foreground">
              {[
                "Drag-and-drop FASTA / FASTQ upload",
                "3 antibiotics currently modeled, with more planned",
                "PDF clinical reports",
                "Audit-ready result history",
              ].map((i) => (
                <li key={i} className="flex items-center gap-3">
                  <CheckCircle2 size={16} className="text-primary" /> {i}
                </li>
              ))}
            </ul>
          </div>

          <div className="space-y-8">
            <LiveAnalyzer />
          </div>
        </div>
        <p className="mt-12 text-sm leading-relaxed text-muted-foreground">
          BactoAI provides genomic antimicrobial resistance predictions to support clinical and
          research decision-making. Results are intended to complement, not replace, conventional
          laboratory testing and professional clinical judgment.
        </p>
        <div className="mt-8 border-t border-border pt-6">
          <h3 className="text-lg font-semibold text-foreground">Data protection</h3>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            BactoAI is designed to comply with the Kenya Data Protection Act, 2019. We do not accept
            identifiable patient data in the demo. Pilot data handling is governed by a
            data-processing agreement agreed with each partner.
          </p>
        </div>
      </div>
    </section>
  );
}
