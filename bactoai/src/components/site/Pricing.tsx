import { Check, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

const tiers = [
  {
    name: "Research Access",
    tagline: "For academic and public-health partners.",
    features: [
      "Pilot pricing for LMICs",
      "Research and surveillance collaboration",
      "3 antibiotics currently modeled, with more planned",
    ],
  },
  {
    name: "Clinical Pilot",
    tagline: "A supervised pilot with a partner hospital or lab, by agreement.",
    features: [
      "Supervised evaluation on local isolates",
      "Conventional laboratory confirmation",
      "Joint review of pilot outcomes",
    ],
  },
  {
    name: "Partnership",
    tagline: "Co-development and data collaboration.",
    features: [
      "Collaborative model development",
      "Genomic data collaboration by agreement",
      "Shared research and validation goals",
    ],
  },
];

export function Pricing({ compact = false }: { compact?: boolean }) {
  return (
    <section id="pricing" className={`${compact ? "py-16" : "py-24 md:py-32"} bg-card/30`}>
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Pilot access
          </div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold text-foreground">
            Explore a BactoAI pilot.
          </h2>
          <p className="mt-4 text-muted-foreground">
            Research, supervised clinical evaluation, and collaborative development — by agreement.
          </p>
        </div>
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className="flex min-w-0 flex-col rounded-lg border border-border bg-card p-6 lg:p-8"
            >
              <h3 className="text-2xl font-semibold text-foreground">{tier.name}</h3>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{tier.tagline}</p>
              <ul className="my-8 space-y-4 text-sm text-muted-foreground">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <Check className="mt-0.5 shrink-0 text-primary" size={16} />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <Button asChild className="mt-auto min-h-12 w-full">
                <a href="/contact">
                  Request a Pilot <ArrowRight size={16} />
                </a>
              </Button>
            </div>
          ))}
        </div>
        <p className="mt-8 text-center text-sm text-muted-foreground">
          Current modeled scope: Meropenem, Ciprofloxacin, and Cefotaxime.
        </p>
      </div>
    </section>
  );
}
