import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";
import { Pricing } from "@/components/site/Pricing";
import { FAQ } from "@/components/site/FAQ";

export const Route = createFileRoute("/pricing")({
  head: () => ({
    meta: [
      { title: "Pilot access — BactoAI · Research, clinical and partnership" },
      {
        name: "description",
        content:
          "Explore Research Access, supervised Clinical Pilots, and Partnerships for co-development and data collaboration.",
      },
      { property: "og:title", content: "Pilot access — BactoAI" },
      {
        property: "og:description",
        content: "Research Access, Clinical Pilot, and Partnership options, by agreement.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/pricing" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/pricing" }],
  }),
  component: PricingPage,
});

function PricingPage() {
  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="pt-24">
        <Pricing />
        <FAQ />
      </main>
      <Footer />
    </div>
  );
}
