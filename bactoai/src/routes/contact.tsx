import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";
import { Contact } from "@/components/site/Contact";
import { ScrollProgressBar } from "@/components/site/ScrollProgressBar";
import { useAutoReveal } from "@/hooks/use-auto-reveal";

export const Route = createFileRoute("/contact")({
  head: () => ({
    meta: [
      { title: "Contact BactoAI — Request a demo or join a pilot" },
      {
        name: "description",
        content:
          "Talk to the BactoAI team about a live demo on your own isolates, a clinical pilot, or partnering as a laboratory.",
      },
      { property: "og:title", content: "Contact BactoAI" },
      {
        property: "og:description",
        content:
          "Request a demo, start a pilot, or partner with BactoAI on genomic AMR prediction.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/contact" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/contact" }],
  }),
  component: ContactPage,
});

function ContactPage() {
  useAutoReveal();
  return (
    <div className="min-h-screen bg-background">
      <ScrollProgressBar />
      <Nav />
      <main className="pt-32">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Request a Demo
          </div>
          <h1 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Let's test BactoAI on your isolates.
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl">
            Schedule a technical demo to see how BactoAI can fit into your laboratory workflow and accelerate antimicrobial resistance profiling.
          </p>
        </div>
        <Contact />
      </main>
      <Footer />
    </div>
  );
}
