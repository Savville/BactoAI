import { Award } from "lucide-react";
import award from "@/assets/award-ceremony.jpg";

export function Research() {
  const awards = [
    {
      t: "Second Place — KU × Lancaster Workshop",
      d: "Science, Engineering & Technology Innovation Workshop.",
    },
    { t: "CDIE Catalyst Grant", d: "Awarded for translational health-tech impact." },
    { t: "East Africa Biodesign", d: "Cohort recognized for clinical design innovation." },
    { t: "GEES Bootcamp", d: "Where we first pitched the BactoAI project." },
  ];
  return (
    <section id="research" className="py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid lg:grid-cols-2 gap-16 items-start">
          <div>
            <div className="text-sm font-semibold text-primary uppercase tracking-widest">
              Research & Recognition
            </div>
            <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
              Recognized by leading innovation programs.
            </h2>
            <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
              BactoAI has been selected and supported by multiple research, biodesign, and
              entrepreneurship programs across East Africa and the UK.
            </p>
            <div className="mt-8 rounded-3xl overflow-hidden border border-border shadow-soft">
              <img src={award} alt="BactoAI receiving award" className="w-full h-72 object-cover" />
            </div>
          </div>
          <div className="space-y-4">
            {awards.map((a) => (
              <div
                key={a.t}
                className="rounded-2xl border border-border bg-card p-6 flex gap-4 shadow-soft"
              >
                <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
                  <Award size={18} />
                </div>
                <div>
                  <div className="font-semibold text-foreground">{a.t}</div>
                  <p className="mt-1 text-sm text-muted-foreground">{a.d}</p>
                </div>
              </div>
            ))}
            <div className="rounded-2xl border border-dashed border-border p-6 text-sm text-muted-foreground">
              Peer-reviewed publications and conference presentations coming soon.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
