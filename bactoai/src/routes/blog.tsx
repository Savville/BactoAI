import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";
import { posts } from "@/content/posts";

export const Route = createFileRoute("/blog")({
  head: () => ({
    meta: [
      { title: "Blog — BactoAI · AMR research, clinical, and product notes" },
      {
        name: "description",
        content:
          "Research notes, clinical perspectives, and public-health analysis on antimicrobial resistance from the BactoAI team and partners.",
      },
      { property: "og:title", content: "Blog — BactoAI" },
      {
        property: "og:description",
        content: "AMR research, clinical, and product notes from BactoAI.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/blog" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/blog" }],
  }),
  component: BlogPage,
});

const categories = ["All", "Research", "Clinical", "Public Health", "Product"] as const;

function BlogPage() {
  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="pt-32 pb-24">
        <div className="mx-auto max-w-6xl px-6">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">Blog</div>
          <h1 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Ideas from the AMR frontier.
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl">
            Field notes, model deep-dives, and clinical perspectives from the BactoAI team and pilot
            partners.
          </p>

          <div className="mt-8 flex flex-wrap gap-2">
            {categories.map((c) => (
              <span
                key={c}
                className={`rounded-full border px-4 py-1.5 text-xs font-semibold ${
                  c === "All"
                    ? "bg-primary text-primary-foreground border-primary"
                    : "border-border text-foreground/70"
                }`}
              >
                {c}
              </span>
            ))}
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {posts.map((p) => (
              <article
                key={p.slug}
                className="group rounded-2xl border border-border bg-card overflow-hidden hover:border-primary/40 transition"
              >
                <div className={`h-40 bg-gradient-to-br ${p.gradient} relative`}>
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.35),transparent_60%)]" />
                  <div className="absolute bottom-3 left-3 rounded-full bg-white/90 text-primary text-[11px] font-semibold px-3 py-1">
                    {p.category}
                  </div>
                </div>
                <div className="p-6">
                  <div className="text-xs text-muted-foreground">
                    {p.date} · {p.readTime}
                  </div>
                  <h2 className="mt-3 text-lg font-bold text-foreground group-hover:text-primary transition">
                    {p.title}
                  </h2>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{p.excerpt}</p>
                </div>
              </article>
            ))}
          </div>

          <p className="mt-12 text-center text-sm text-muted-foreground">
            More articles are on the way. Subscribe below to get them in your inbox.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
