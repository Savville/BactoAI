import { createFileRoute, Link } from "@tanstack/react-router";
import { ExternalLink, Mail, Image as ImageIcon, Download } from "lucide-react";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";
import { ScrollProgressBar } from "@/components/site/ScrollProgressBar";
import { useAutoReveal } from "@/hooks/use-auto-reveal";
import { Reveal } from "@/components/site/Reveal";
import { Media } from "@/components/site/Media";
import logoWordmark from "@/assets/bactoai-logo-wordmark.png.asset.json";

export const Route = createFileRoute("/press")({
  head: () => ({
    meta: [
      { title: "Press & media — BactoAI coverage and press kit" },
      {
        name: "description",
        content:
          "BactoAI in the media: KUTV Kenya's AMR interview, BIK Ventures Hub coverage, plus our press kit, brand assets, and media contact.",
      },
      { property: "og:title", content: "Press & media — BactoAI" },
      {
        property: "og:description",
        content:
          "Coverage of BactoAI's work on genome-driven antimicrobial resistance prediction, with press kit and media contact.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/press" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/press" }],
    scripts: [
      {
        type: "application/ld+json",
        children: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "CollectionPage",
          name: "BactoAI press & media",
          url: "https://bactoai.co.ke/press",
          about:
            "Media coverage of BactoAI, a genomic antimicrobial resistance prediction platform.",
        }),
      },
    ],
  }),
  component: PressPage,
});

const kit = [
  {
    icon: ImageIcon,
    title: "Logo & wordmark",
    body: "The BactoAI wordmark with the bacterial emblem, for use in articles and event material. Please keep clear space around it and don't recolour it.",
    href: logoWordmark.url,
    cta: "Download logo (PNG)",
    download: true,
  },
  {
    icon: Download,
    title: "Company one-pager",
    body: "A concise overview of the platform, our validation approach, and current pilot opportunities. Available on request while we finalise the public version.",
    href: "mailto:info@bactoai.co.ke?subject=BactoAI%20press%20one-pager%20request",
    cta: "Request one-pager",
  },
  {
    icon: Mail,
    title: "Interviews & expert comment",
    body: "Our founder and team are available for interviews and background briefings on antimicrobial resistance, genomic diagnostics, and health innovation in East Africa.",
    href: "mailto:info@bactoai.co.ke?subject=BactoAI%20interview%20request",
    cta: "Request an interview",
  },
];

const boilerplate =
  "BactoAI is a Kenyan health-technology company building an AMR intelligence platform that predicts antimicrobial resistance directly from bacterial genomes, helping clinicians and laboratories reach the right treatment decision faster. The platform is built and owned by BactoAI as a company, combining biotechnology, software engineering, machine learning, operations, and partnerships expertise.";

function PressPage() {
  useAutoReveal();
  return (
    <div className="min-h-screen bg-background">
      <ScrollProgressBar />
      <Nav />
      <main className="pt-32 pb-24">
        <div className="mx-auto max-w-6xl px-6">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Press & media
          </div>
          <h1 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            BactoAI in the media.
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl">
            Coverage of our work on antimicrobial resistance, plus a press kit and a direct media
            contact for journalists, event organisers, and partners.
          </p>
        </div>

        <Media />

        <div className="mx-auto max-w-6xl px-6">
          <Reveal>
            <div className="rounded-3xl border border-dashed border-border p-6 md:p-8 text-sm text-muted-foreground">
              More mentions will be listed here as they are published. Writing about AMR in Kenya or
              East Africa?{" "}
              <a
                href="mailto:info@bactoai.co.ke?subject=BactoAI%20media%20enquiry"
                className="font-semibold text-primary hover:underline"
              >
                Get in touch
              </a>{" "}
              — we're happy to share data, context, and expert comment.
            </div>
          </Reveal>

          <section id="press-kit" className="mt-24">
            <Reveal className="max-w-2xl">
              <div className="text-sm font-semibold text-primary uppercase tracking-widest">
                Press kit
              </div>
              <h2 className="mt-3 text-3xl md:text-4xl font-bold tracking-tight text-foreground">
                Everything you need to write about us.
              </h2>
            </Reveal>
            <div className="mt-10 grid md:grid-cols-3 gap-6">
              {kit.map((k, i) => {
                const Icon = k.icon;
                return (
                  <Reveal key={k.title} delay={i * 100}>
                    <div className="h-full rounded-3xl border border-border bg-card p-6 shadow-soft flex flex-col">
                      <Icon className="text-primary" size={22} />
                      <h3 className="mt-4 text-lg font-bold text-foreground">{k.title}</h3>
                      <p className="mt-2 text-sm text-muted-foreground leading-relaxed flex-1">
                        {k.body}
                      </p>
                      <a
                        href={k.href}
                        {...(k.download ? { download: "bactoai-logo.png" } : {})}
                        className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline"
                      >
                        {k.cta} <ExternalLink size={13} />
                      </a>
                    </div>
                  </Reveal>
                );
              })}
            </div>

            <Reveal delay={150}>
              <div className="mt-8 rounded-3xl border border-border bg-card p-6 md:p-8 shadow-soft">
                <div className="text-xs font-semibold text-primary uppercase tracking-widest">
                  Company boilerplate
                </div>
                <p className="mt-3 text-foreground leading-relaxed">{boilerplate}</p>
              </div>
            </Reveal>
          </section>

          <section id="media-contact" className="mt-24">
            <Reveal>
              <div className="rounded-3xl border border-border bg-gradient-hero p-8 md:p-12 text-white shadow-elegant">
                <div className="text-xs font-semibold uppercase tracking-widest text-white/80">
                  Media contact
                </div>
                <h2 className="mt-3 text-3xl md:text-4xl font-bold tracking-tight">
                  Talk to the BactoAI team.
                </h2>
                <p className="mt-3 max-w-2xl text-white/85 leading-relaxed">
                  For interviews, event invitations, data requests, or fact-checking, email us
                  directly — we usually reply within two working days.
                </p>
                <div className="mt-7 flex flex-wrap items-center gap-3">
                  <a
                    href="mailto:info@bactoai.co.ke?subject=BactoAI%20media%20enquiry"
                    className="inline-flex items-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-semibold text-primary shadow-soft hover:opacity-95 transition"
                  >
                    <Mail size={15} /> info@bactoai.co.ke
                  </a>
                  <Link
                    to="/contact"
                    className="inline-flex items-center gap-2 rounded-full border border-white/40 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10 transition"
                  >
                    Use the contact form
                  </Link>
                  <a
                    href="https://www.linkedin.com/in/bactoai-model-32303335a"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 rounded-full border border-white/40 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10 transition"
                  >
                    LinkedIn <ExternalLink size={14} />
                  </a>
                </div>
              </div>
            </Reveal>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
