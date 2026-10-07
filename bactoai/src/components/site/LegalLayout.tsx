import type { ReactNode } from "react";
import { Nav } from "./Nav";
import { Footer } from "./Footer";

export function LegalLayout({
  title,
  updated,
  children,
}: {
  title: string;
  updated?: string;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="pt-32 pb-20">
        <div className="mx-auto max-w-3xl px-6">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">Legal</div>
          <h1 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            {title}
          </h1>
          {updated && <p className="mt-3 text-sm text-muted-foreground">Last updated: {updated}</p>}
          <div className="prose prose-invert mt-10 max-w-none text-foreground/85 leading-relaxed [&_h2]:mt-10 [&_h2]:mb-3 [&_h2]:text-xl [&_h2]:font-bold [&_h2]:text-foreground [&_h3]:mt-6 [&_h3]:mb-2 [&_h3]:text-base [&_h3]:font-semibold [&_h3]:text-foreground [&_p]:my-3 [&_ul]:my-3 [&_ul]:list-disc [&_ul]:pl-6 [&_li]:my-1 [&_a]:text-primary [&_a]:underline hover:[&_a]:opacity-80">
            {children}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
