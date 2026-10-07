import { Link } from "@tanstack/react-router";
import { ArrowUpRight } from "lucide-react";
import { posts } from "@/content/posts";

export function BlogPreview() {
  const featured = posts.slice(0, 3);
  return (
    <section id="blog" className="py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex items-end justify-between flex-wrap gap-4">
          <div className="max-w-2xl">
            <div className="text-sm font-semibold text-primary uppercase tracking-widest">
              Resources
            </div>
            <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
              Ideas from the AMR frontier.
            </h2>
            <p className="mt-4 text-muted-foreground">
              Research notes, clinical perspectives, and public-health analysis from the BactoAI
              team and partners.
            </p>
          </div>
          <Link
            to="/blog"
            className="inline-flex items-center gap-1 rounded-full border border-border bg-card px-5 py-2.5 text-sm font-semibold hover:border-primary/40 transition"
          >
            All articles <ArrowUpRight size={14} />
          </Link>
        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {featured.map((p) => (
            <Link
              key={p.slug}
              to="/blog"
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
                <h3 className="mt-3 text-lg font-bold text-foreground group-hover:text-primary transition">
                  {p.title}
                </h3>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed line-clamp-3">
                  {p.excerpt}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
