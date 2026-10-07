import { useState } from "react";
import { ChevronDown } from "lucide-react";

const faqs = [
  {
    q: "What is BactoAI?",
    a: "BactoAI is an AI-powered platform that predicts antimicrobial resistance from bacterial whole-genome sequences to support faster, precision antibiotic decisions.",
  },
  {
    q: "Does BactoAI replace laboratory testing?",
    a: "No. BactoAI is a decision-support tool that complements laboratory workflows by providing rapid predictive insights while conventional testing is completed.",
  },
  {
    q: "What sequencing files are supported?",
    a: "BactoAI accepts standard bacterial whole-genome sequencing inputs including FASTA and FASTQ files from short- and long-read platforms (Illumina and Oxford Nanopore).",
  },
  {
    q: "How accurate are predictions?",
    a: "Performance varies by antibiotic and organism. Our Meropenem model reports 0.952 ROC-AUC on internal validation. Prospective clinical validation is ongoing and results are published transparently.",
  },
  {
    q: "How is patient data protected?",
    a: "BactoAI is built with strict access control, encryption in transit and at rest, and supports on-premises deployment for restricted environments. We follow HIPAA and GDPR principles by design.",
  },
  {
    q: "Can BactoAI integrate with our LIMS?",
    a: "LIMS integration can be explored through a Clinical Pilot or Partnership, by agreement.",
  },
  {
    q: "Is BactoAI regulatory-approved?",
    a: "BactoAI is currently offered as decision-support software. We are actively engaging with regulators (FDA, CE-IVD, PPB) as prospective clinical validation matures.",
  },
  {
    q: "How do pilot programs work?",
    a: "Pilots are 8–12 weeks, include onboarding for your lab, model validation against your isolates, and a joint outcomes review. Pilot pricing is available for LMIC academic and public-health partners.",
  },
  {
    q: "Which antibiotics do you support today?",
    a: "The current panel covers 3 antibiotics currently modeled, with more planned: Meropenem, Ciprofloxacin, and Cefotaxime.",
  },
  {
    q: "How is BactoAI different from lab-booking apps or prescribing-guideline chatbots?",
    a: "Lab-booking and sample-logistics apps get a specimen to a laboratory faster, but the answer still waits on a completed culture — typically 48–72 hours. Prescribing-guideline chatbots apply WHO or national decision trees to reported symptoms, but they have no organism-specific resistance evidence to work from. BactoAI predicts per-antibiotic resistance directly from the bacterial genome in under 10 minutes from genome to result, producing a data point that simply doesn't exist in those systems. We see them as complementary infrastructure rather than rivals: a lab-booking platform could route a case to a BactoAI prediction, and a prescribing assistant could take that prediction as an input.",
  },
  {
    q: "Is BactoAI a competitor to existing AMR digital-health platforms?",
    a: "No. BactoAI is the diagnostic layer underneath them. We do not book samples, route couriers, or enforce prescribing protocols; we generate the genomic resistance prediction that logistics platforms, stewardship dashboards, and clinical decision-support tools can consume through our API.",
  },
  {
    q: "Who founded BactoAI?",
    a: "BactoAI was developed in Nairobi, Kenya by Samwel Elegwa, alongside a team of clinical microbiologists, AI researchers, and public-health advisors from Kenya and the UK.",
  },
];

export function FAQ() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section id="faq" className="py-24 md:py-32">
      <div className="mx-auto max-w-4xl px-6">
        <div className="text-center">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">FAQ</div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Frequently asked questions
          </h2>
        </div>
        <div className="mt-12 space-y-3">
          {faqs.map((f, i) => (
            <div key={f.q} className="rounded-2xl border border-border bg-card overflow-hidden">
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="w-full flex items-center justify-between text-left px-6 py-5"
              >
                <span className="font-semibold text-foreground">{f.q}</span>
                <ChevronDown
                  size={18}
                  className={`text-muted-foreground transition-transform ${open === i ? "rotate-180" : ""}`}
                />
              </button>
              {open === i && (
                <div className="px-6 pb-5 text-sm text-muted-foreground leading-relaxed">{f.a}</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
