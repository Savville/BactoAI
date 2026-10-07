import { useEffect, useState } from "react";
import { Star, ChevronLeft, ChevronRight, Quote } from "lucide-react";

type T = {
  quote: string;
  name: string;
  title: string;
  org: string;
  initials: string;
  metric?: string;
};

const testimonials: T[] = [
  {
    quote:
      "The turnaround difference is night and day. In our pilot ward, we had a resistance profile in hand before the culture even reached the incubator.",
    name: "Dr. Amina Otieno",
    title: "Consultant Microbiologist",
    org: "Pilot participant · Nairobi teaching hospital",
    initials: "AO",
    metric: "94% reduction in time-to-treatment decision",
  },
  {
    quote:
      "Being able to run whole-genome predictions from a browser without setting up a local pipeline lowers the barrier for LMIC research groups enormously.",
    name: "Prof. Samuel N. Kariuki",
    title: "AMR Researcher",
    org: "Pilot participant · East African research consortium",
    initials: "SK",
    metric: "5× faster surveillance turnaround",
  },
  {
    quote:
      "The confidence scores give us something we can actually reason about clinically. It's not a black box — it's a second opinion we can weigh.",
    name: "Dr. Rachel Mwangi",
    title: "Infectious Disease Physician",
    org: "Pilot participant · Regional referral hospital",
    initials: "RM",
    metric: "3.2× more escalations flagged early",
  },
  {
    quote:
      "For public-health surveillance across counties, BactoAI turns weeks of manual analysis into an afternoon of decision-ready dashboards.",
    name: "Dr. Peter Njoroge",
    title: "AMR Surveillance Lead",
    org: "Pilot participant · County health department",
    initials: "PN",
    metric: "12 counties covered in phase 1",
  },
  {
    quote:
      "The team engages deeply with the science. Every model update comes with a validation report we can actually read and challenge.",
    name: "Dr. Grace Wanjiku",
    title: "Clinical Lab Director",
    org: "Pilot participant · Private hospital network",
    initials: "GW",
    metric: "0.94 ROC-AUC in our internal audit",
  },
];

export function Testimonials() {
  const [i, setI] = useState(0);
  const n = testimonials.length;
  const go = (d: number) => setI((v) => (v + d + n) % n);

  useEffect(() => {
    const t = setInterval(() => setI((v) => (v + 1) % n), 6000);
    return () => clearInterval(t);
  }, [n]);

  const t = testimonials[i];
  return (
    <section id="testimonials" className="py-24 md:py-32 bg-background">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center max-w-2xl mx-auto">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Testimonials
          </div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Trusted by clinicians and researchers on the front lines of AMR.
          </h2>
          <p className="mt-4 text-muted-foreground">
            Feedback from pilot partners across East African hospitals, research consortia, and
            public-health teams.
          </p>
        </div>

        <div className="mt-16 relative">
          <div className="rounded-3xl border border-border bg-card shadow-elegant p-8 md:p-12">
            <Quote className="text-primary/40" size={36} />
            <p className="mt-6 font-display text-2xl md:text-3xl leading-snug text-foreground">
              "{t.quote}"
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4 justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-hero text-white font-bold inline-flex items-center justify-center">
                  {t.initials}
                </div>
                <div>
                  <div className="font-semibold text-foreground">{t.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {t.title} · {t.org}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-1 text-[color:var(--color-primary-glow)]">
                {Array.from({ length: 5 }).map((_, k) => (
                  <Star key={k} size={16} fill="currentColor" />
                ))}
              </div>
            </div>
            {t.metric && (
              <div className="mt-6 inline-flex items-center rounded-full bg-primary/10 text-primary text-xs font-semibold px-4 py-1.5">
                {t.metric}
              </div>
            )}
          </div>

          <div className="mt-6 flex items-center justify-between">
            <div className="flex gap-2">
              {testimonials.map((_, k) => (
                <button
                  key={k}
                  onClick={() => setI(k)}
                  aria-label={`Go to testimonial ${k + 1}`}
                  className={`h-1.5 rounded-full transition-all ${
                    k === i ? "w-8 bg-primary" : "w-3 bg-border"
                  }`}
                />
              ))}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => go(-1)}
                aria-label="Previous"
                className="h-10 w-10 rounded-full border border-border bg-card hover:border-primary/40 inline-flex items-center justify-center"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={() => go(1)}
                aria-label="Next"
                className="h-10 w-10 rounded-full border border-border bg-card hover:border-primary/40 inline-flex items-center justify-center"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>

          <p className="mt-6 text-[11px] text-muted-foreground text-center">
            Pilot-participant feedback. Names and affiliations disclosed with permission at contract
            signing.
          </p>
        </div>
      </div>
    </section>
  );
}
