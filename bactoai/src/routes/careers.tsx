import { createFileRoute } from "@tanstack/react-router";
import { Mail, ArrowRight } from "lucide-react";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";

export const Route = createFileRoute("/careers")({
  head: () => ({
    meta: [
      { title: "Careers — BactoAI" },
      {
        name: "description",
        content:
          "BactoAI isn't actively hiring, but we're always interested in scientists, engineers, and clinicians who want to work on AMR.",
      },
      { property: "og:title", content: "Careers — BactoAI" },
      {
        property: "og:description",
        content:
          "Explore opportunities to work with BactoAI on genomic antimicrobial resistance prediction.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/careers" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/careers" }],
  }),
  component: CareersPage,
});

function CareersPage() {
  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="pt-32 pb-24">
        <div className="mx-auto max-w-3xl px-6">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Careers
          </div>
          <h1 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Help us push antimicrobial resistance out of the dark.
          </h1>
          <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
            BactoAI is a small, focused team building precision AMR diagnostics from bacterial
            genomes. We're not running an active hiring round right now — but we're always
            interested in hearing from exceptional scientists, ML engineers, bioinformaticians,
            clinicians, and operators who want to work on this problem.
          </p>

          <div className="mt-10 rounded-2xl border border-border bg-card p-8 shadow-soft">
            <h2 className="text-xl font-bold text-foreground">Areas we care about</h2>
            <ul className="mt-4 grid sm:grid-cols-2 gap-3 text-sm text-muted-foreground">
              <li>· Machine learning for genomics</li>
              <li>· Bioinformatics pipelines</li>
              <li>· Clinical microbiology & AMR</li>
              <li>· Full-stack / platform engineering</li>
              <li>· Regulatory & clinical validation</li>
              <li>· Partnerships & operations</li>
            </ul>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <a
                href="mailto:info@bactoai.co.ke?subject=BactoAI%20-%20Expression%20of%20interest"
                className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-elegant hover:opacity-95 transition"
              >
                <Mail size={16} /> Send us an expression of interest <ArrowRight size={14} />
              </a>
              <span className="text-xs text-muted-foreground">
                We read every message and reply within 2 weeks.
              </span>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
