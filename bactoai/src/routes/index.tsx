import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";
import { Hero } from "@/components/site/Hero";
import { Stakes } from "@/components/site/Stakes";
import { TrustBar } from "@/components/site/TrustBar";
import { Problem } from "@/components/site/Problem";
import { Solution } from "@/components/site/Solution";
import { ProductDemo } from "@/components/site/ProductDemo";
import { Validation } from "@/components/site/Validation";
import { PreFooterCTA } from "@/components/site/PreFooterCTA";
import { ScrollProgressBar } from "@/components/site/ScrollProgressBar";
import { useAutoReveal } from "@/hooks/use-auto-reveal";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "BactoAI — Predict antibiotic resistance from bacterial genomes" },
      {
        name: "description",
        content:
          "BactoAI is a genomic AI prediction engine that turns bacterial whole-genome sequences into clinician-ready antimicrobial resistance predictions in minutes.",
      },
      { property: "og:title", content: "BactoAI — Genomic AI for antimicrobial resistance" },
      {
        property: "og:description",
        content:
          "Predict antibiotic resistance from a bacterial genome in minutes, and act on precision treatment decisions sooner.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/" }],
  }),
  component: Index,
});

function Index() {
  useAutoReveal();
  return (
    <div className="min-h-screen bg-background">
      <ScrollProgressBar />
      <Nav />
      <main>
        <Hero />
        <Stakes />
        <TrustBar />
        <Problem />
        <Solution />
        <ProductDemo />
        <Validation />
        <PreFooterCTA />
      </main>
      <Footer />
    </div>
  );
}
