import { Play, ExternalLink, Quote, Newspaper } from "lucide-react";
import { Reveal } from "./Reveal";
import kutvPoster from "@/assets/kutv-poster.jpg.asset.json";
import kutvStudio from "@/assets/kutv-studio.jpg.asset.json";
import bikMagazine from "@/assets/bik-magazine.jpg.asset.json";
import bikFeedback from "@/assets/bik-feedback.mp4.asset.json";

export function Media() {
  return (
    <section id="media" className="py-24 md:py-32 bg-background">
      <div className="mx-auto max-w-7xl px-6">
        <Reveal className="max-w-3xl">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            In the media
          </div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Bringing the AMR conversation to national television.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground leading-relaxed">
            BactoAI founder Samwel Elegwa joined KUTV Kenya’s Art & Culture Monday to talk about
            antimicrobial resistance and why faster, genome-driven diagnostics matter for patients,
            clinicians, and public health systems.
          </p>
        </Reveal>

        <div className="mt-14 grid lg:grid-cols-[1.25fr_0.75fr] gap-6 items-start">
          <Reveal variant="left">
            <a
              href="https://youtu.be/ENvEk0a0CHs?si=NITn5aXnJfv1HucC"
              target="_blank"
              rel="noopener noreferrer"
              className="group block relative rounded-3xl border border-border bg-card overflow-hidden shadow-soft hover:shadow-elegant transition"
            >
              <div className="relative aspect-[4/5] md:aspect-[16/10]">
                <img
                  src={kutvPoster.url}
                  alt="Samwel Elegwa, Founder of BactoAI, featured on KUTV Kenya Art & Culture Monday"
                  className="absolute inset-0 w-full h-full object-cover object-top"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-16 h-16 rounded-full bg-white/90 text-primary flex items-center justify-center shadow-elegant group-hover:scale-110 transition-transform">
                    <Play size={24} fill="currentColor" />
                  </div>
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-6 md:p-8">
                  <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 text-primary px-3 py-1 text-[11px] font-semibold uppercase tracking-widest">
                    Watch the interview
                  </div>
                  <h3 className="mt-3 text-xl md:text-2xl font-bold text-white leading-snug">
                    KUTV Kenya — Art & Culture Monday
                  </h3>
                  <p className="mt-2 text-sm text-white/80">
                    Monday 31st August 2026 · Rise Today segment
                  </p>
                </div>
              </div>
            </a>
          </Reveal>

          <div className="space-y-6">
            <Reveal variant="right" delay={120}>
              <div className="rounded-3xl border border-border bg-card p-6 shadow-soft">
                <Quote className="text-primary/40" size={28} />
                <blockquote className="mt-4 text-lg md:text-xl font-display italic text-foreground leading-snug">
                  “AMR is not just a lab problem — it is a public health emergency that needs to be
                  part of everyday conversation.”
                </blockquote>
                <div className="mt-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-hero text-white flex items-center justify-center font-bold text-sm">
                    SE
                  </div>
                  <div>
                    <div className="font-semibold text-foreground text-sm">Samwel Elegwa</div>
                    <div className="text-xs text-muted-foreground">Founder & CEO, BactoAI</div>
                  </div>
                </div>
              </div>
            </Reveal>

            <Reveal variant="right" delay={200}>
              <div className="rounded-3xl border border-border bg-card overflow-hidden shadow-soft">
                <div className="aspect-[4/3]">
                  <img
                    src={kutvStudio.url}
                    alt="Samwel Elegwa with Hassan Lewa at the KUTV Kenya studio"
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                </div>
                <div className="p-5">
                  <div className="text-xs font-semibold text-primary uppercase tracking-widest">
                    Behind the scenes
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                    Samwel with Hassan Lewa at the KUTV studio after the Art & Culture Monday
                    interview.
                  </p>
                </div>
              </div>
            </Reveal>

            <Reveal variant="right" delay={280}>
              <a
                href="https://youtu.be/ENvEk0a0CHs?si=NITn5aXnJfv1HucC"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-elegant hover:opacity-95 transition"
              >
                Watch on YouTube <ExternalLink size={14} />
              </a>
            </Reveal>
          </div>
        </div>

        <div className="mt-20 md:mt-24 border-t border-border pt-16">
          <Reveal className="max-w-3xl">
            <div className="inline-flex items-center gap-2 text-sm font-semibold text-primary uppercase tracking-widest">
              <Newspaper size={16} /> On the ecosystem stage
            </div>
            <h3 className="mt-4 text-3xl md:text-4xl font-bold tracking-tight text-foreground">
              Representing BactoAI at the BIK Ventures Hub pitch event.
            </h3>
            <p className="mt-4 text-lg text-muted-foreground leading-relaxed">
              In May 2026, Samwel Elegwa and William Otieno represented BactoAI at the BIK Ventures
              Hub startup pitch event at Kenyatta University — a landmark competition bringing
              together founders, investors, and industry leaders. The event was covered in print and
              on BIK’s YouTube channel.
            </p>
          </Reveal>

          <div className="mt-12 grid lg:grid-cols-[1.1fr_0.9fr] gap-6 items-start">
            <Reveal variant="left">
              <div className="rounded-3xl border border-border bg-card overflow-hidden shadow-soft">
                <img
                  src={bikMagazine.url}
                  alt="Newspaper coverage of the BIK Ventures Hub startup pitch event at Kenyatta University"
                  className="w-full h-auto"
                  loading="lazy"
                />
                <div className="p-5">
                  <div className="text-xs font-semibold text-primary uppercase tracking-widest">
                    In print · 16 May 2026
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                    Press coverage of the BIK Ventures Hub pitch event at Kenyatta University, where
                    BactoAI took the stage among East Africa’s emerging startups.
                  </p>
                </div>
              </div>
            </Reveal>

            <div className="space-y-6">
              <Reveal variant="right" delay={120}>
                <div className="rounded-3xl border border-border bg-card overflow-hidden shadow-soft">
                  <video
                    src={bikFeedback.url}
                    controls
                    preload="metadata"
                    playsInline
                    className="w-full aspect-[9/16] max-h-[520px] object-cover bg-black mx-auto"
                  />
                  <div className="p-5">
                    <div className="text-xs font-semibold text-primary uppercase tracking-widest">
                      Founder reflections
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                      Samwel shares his feedback on the BIK Ventures experience and what it means
                      for startups building in East Africa.
                    </p>
                  </div>
                </div>
              </Reveal>

              <Reveal variant="right" delay={200}>
                <a
                  href="https://youtu.be/SOSCWDj7mYk?si=u_VqEoI7-uq0WgCv"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-6 py-3 text-sm font-semibold text-foreground shadow-soft hover:shadow-elegant transition"
                >
                  Watch BIK’s event coverage <ExternalLink size={14} />
                </a>
                <p className="mt-3 text-xs text-muted-foreground">
                  BIK’s recap video features the event’s innovations, including BactoAI.
                </p>
              </Reveal>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
