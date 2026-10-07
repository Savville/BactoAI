import { createFileRoute } from "@tanstack/react-router";
import { BookOpen, Linkedin, FileText, Newspaper } from "lucide-react";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";
import { BlogPreview } from "@/components/site/BlogPreview";

export const Route = createFileRoute("/resources")({
  head: () => ({
    meta: [
      { title: "Resources — BactoAI" },
      {
        name: "description",
        content: "AMR education, press mentions, and downloadable materials from the BactoAI team.",
      },
      { property: "og:title", content: "Resources — BactoAI" },
      {
        property: "og:description",
        content: "AMR education, press mentions, and downloadable materials from the BactoAI team.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/resources" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/resources" }],
  }),
  component: ResourcesPage,
});

const resources = [
  {
    icon: Linkedin,
    title: "AMR Awareness Weekly",
    tag: "LinkedIn series",
    body: "A short weekly series on antimicrobial resistance — the science, the numbers, and what precision diagnostics can change. Coming soon on our LinkedIn.",
    href: "https://www.linkedin.com/in/bactoai-model-32303335a",
    external: true,
    cta: "Follow on LinkedIn",
  },
  {
    icon: FileText,
    title: "BactoAI one-pager",
    tag: "PDF · Coming soon",
    body: "A concise overview of the platform, our validation approach, and current pilot opportunities. Email us for early access.",
    href: "mailto:info@bactoai.co.ke?subject=BactoAI%20one-pager%20request",
    cta: "Request one-pager",
  },
  {
    icon: Newspaper,
    title: "Press & mentions",
    tag: "Updated periodically",
    body: "KUTV Kenya's AMR interview, BIK Ventures Hub coverage, our press kit, brand assets, and a direct media contact — all on the press page.",
    href: "/press",
    cta: "Visit the press page",
  },
  {
    icon: BookOpen,
    title: "AMR primer for founders & clinicians",
    tag: "Reading list",
    body: "A curated set of WHO, CDC, and peer-reviewed references we return to when explaining why AMR is a slow-moving global crisis. In preparation.",
    cta: "In preparation",
  },
];

function ResourcesPage() {
  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="pt-32 pb-24">
        <div className="mx-auto max-w-5xl px-6">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Resources
          </div>
          <h1 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Education, press, and materials on the AMR problem we work on.
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl">
            We publish short-form education about antimicrobial resistance and share downloadable
            materials for hospitals, researchers, and partners.
          </p>

          <div className="mt-14 grid sm:grid-cols-2 gap-6">
            {resources.map((r) => {
              const Icon = r.icon;
              const isLink = Boolean(r.href);
              const Wrapper = (isLink ? "a" : "div") as "a" | "div";
              return (
                <Wrapper
                  key={r.title}
                  {...(isLink
                    ? {
                        href: r.href,
                        target: r.external ? "_blank" : undefined,
                        rel: r.external ? "noopener noreferrer" : undefined,
                      }
                    : {})}
                  className={`group block rounded-2xl border border-border bg-card p-6 shadow-soft transition ${
                    isLink ? "hover:border-primary/40 hover:shadow-elegant" : "opacity-90"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 text-primary inline-flex items-center justify-center">
                      <Icon size={18} />
                    </div>
                    <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
                      {r.tag}
                    </span>
                  </div>
                  <h2 className="mt-5 text-lg font-bold text-foreground">{r.title}</h2>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{r.body}</p>
                  <div
                    className={`mt-4 text-sm font-semibold ${isLink ? "text-primary group-hover:opacity-80" : "text-muted-foreground"}`}
                  >
                    {r.cta} {isLink && "→"}
                  </div>
                </Wrapper>
              );
            })}
          </div>
        </div>
        <BlogPreview />
      </main>
      <Footer />
    </div>
  );
}
