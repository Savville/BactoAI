import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";
import { Technology } from "@/components/site/Technology";
import { Features } from "@/components/site/Features";
import { WhyBactoAI } from "@/components/site/WhyBactoAI";
import { FAQ } from "@/components/site/FAQ";
import { ScrollProgressBar } from "@/components/site/ScrollProgressBar";
import { useAutoReveal } from "@/hooks/use-auto-reveal";

export const Route = createFileRoute("/technology")({
  head: () => ({
    meta: [
      { title: "Technology — BactoAI · Genomic AI for resistance prediction" },
      {
        name: "description",
        content:
          "How BactoAI turns a bacterial genome into a clinician-ready resistance prediction: feature extraction, machine-learning models, and validated reporting.",
      },
      { property: "og:title", content: "Technology — BactoAI" },
      {
        property: "og:description",
        content:
          "Inside the BactoAI prediction engine: genomic feature extraction, ML models, and clinician-ready resistance reports.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/technology" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/technology" }],
  }),
  component: TechnologyPage,
});

function TechnologyPage() {
  useAutoReveal();
  return (
    <div className="min-h-screen bg-background">
      <ScrollProgressBar />
      <Nav />
      <main className="pt-32">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Technology
          </div>
          <h1 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            From genome to resistance prediction.
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl">
            The models, pipeline, and platform capabilities behind every BactoAI prediction.
          </p>
        </div>
        <Technology />
        <Features />
        <WhyBactoAI />
        <FAQ />
        <p className="mx-auto max-w-5xl px-6 pb-16 text-sm leading-relaxed text-muted-foreground">
          BactoAI provides genomic antimicrobial resistance predictions to support clinical and
          research decision-making. Results are intended to complement, not replace, conventional
          laboratory testing and professional clinical judgment.
        </p>
      </main>
      <Footer />
    </div>
  );
}
