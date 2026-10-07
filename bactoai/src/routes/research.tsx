import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";
import { Research } from "@/components/site/Research";
import { Impact } from "@/components/site/Impact";
import { PartnerLabs } from "@/components/site/PartnerLabs";
import { ScrollProgressBar } from "@/components/site/ScrollProgressBar";
import { useAutoReveal } from "@/hooks/use-auto-reveal";

export const Route = createFileRoute("/research")({
  head: () => ({
    meta: [
      { title: "Research & Impact — BactoAI · Evidence and partner labs" },
      {
        name: "description",
        content:
          "BactoAI research output, clinical and public-health impact, and target clinical sites for planned validation.",
      },
      { property: "og:title", content: "Research & Impact — BactoAI" },
      {
        property: "og:description",
        content: "Research, measured impact, and target clinical settings for future validation.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/research" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/research" }],
  }),
  component: ResearchPage,
});

function ResearchPage() {
  useAutoReveal();
  return (
    <div className="min-h-screen bg-background">
      <ScrollProgressBar />
      <Nav />
      <main className="pt-32">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Research &amp; Impact
          </div>
          <h1 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Evidence, outcomes, and target validation sites.
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl">
            Research progress, measured impact, and intended clinical validation settings — not
            confirmed partnerships.
          </p>
        </div>
        <Research />
        <Impact />
        <PartnerLabs />
      </main>
      <Footer />
    </div>
  );
}
