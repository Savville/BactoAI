import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { auditTheme } from "@/components/dev/ContrastAudit";
import { formatRatio, type AuditResult } from "@/lib/contrast";

export const Route = createFileRoute("/theme-tokens")({
  head: () => ({
    meta: [
      { title: "Theme Tokens — BactoAI Design System" },
      {
        name: "description",
        content:
          "Preview BactoAI's base, text, and accent design tokens in light and dark mode with live WCAG AA contrast checks.",
      },
      { property: "og:title", content: "Theme Tokens — BactoAI Design System" },
      {
        property: "og:description",
        content:
          "Base, text, accent and result-state tokens with live WCAG AA contrast validation for both themes.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: ThemeTokensPage,
});

const GROUPS: Array<{ title: string; tokens: string[] }> = [
  {
    title: "Base surfaces",
    tokens: [
      "--background",
      "--card",
      "--popover",
      "--secondary",
      "--muted",
      "--dark",
      "--border",
      "--input",
    ],
  },
  {
    title: "Text",
    tokens: ["--foreground", "--card-foreground", "--muted-foreground", "--secondary-foreground"],
  },
  {
    title: "Accents",
    tokens: ["--primary", "--primary-glow", "--accent", "--cyan", "--ring"],
  },
  {
    title: "Result states",
    tokens: ["--susceptible", "--resistant", "--destructive"],
  },
];

function Swatch({ token, theme }: { token: string; theme: "dark" | "light" }) {
  return (
    <div className="rounded-xl border border-border overflow-hidden">
      <div className="h-16 w-full" style={{ background: `var(${token})` }} />
      <div className={`${theme} bg-background px-3 py-2`}>
        <div className="font-mono text-[11px] text-foreground">{token}</div>
        <div className="font-mono text-[10px] text-muted-foreground">
          <TokenValue token={token} />
        </div>
      </div>
    </div>
  );
}

function TokenValue({ token }: { token: string }) {
  const [value, setValue] = useState("");
  useEffect(() => {
    setValue(getComputedStyle(document.documentElement).getPropertyValue(token).trim());
  }, [token]);
  return <>{value || "—"}</>;
}

function ThemePanel({ theme }: { theme: "dark" | "light" }) {
  return (
    <section className={`${theme} rounded-2xl border border-border bg-background p-6`}>
      <h2 className="text-lg font-semibold text-foreground capitalize">{theme} mode</h2>
      <p className="mt-1 text-sm text-muted-foreground">Body text sample · muted secondary text.</p>
      <div className="mt-5 space-y-6">
        {GROUPS.map((g) => (
          <div key={g.title}>
            <h3 className="text-xs uppercase tracking-widest text-muted-foreground">{g.title}</h3>
            <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-3">
              {g.tokens.map((t) => (
                <Swatch key={t} token={t} theme={theme} />
              ))}
            </div>
          </div>
        ))}
        <div className="flex flex-wrap gap-3">
          <button className="rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground">
            Primary action
          </button>
          <span className="rounded-full border border-border px-4 py-2 text-sm text-susceptible">
            Susceptible
          </span>
          <span className="rounded-full border border-border px-4 py-2 text-sm text-resistant">
            Resistant
          </span>
        </div>
      </div>
    </section>
  );
}

function ContrastTable({ theme }: { theme: "dark" | "light" }) {
  const results = useMemo<AuditResult[]>(
    () => (typeof window === "undefined" ? [] : auditTheme(theme)),
    [theme],
  );
  const failures = results.filter((r) => !r.passes).length;

  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-card-foreground capitalize">{theme} contrast</h3>
        <span
          className={`text-xs font-semibold ${failures ? "text-resistant" : "text-susceptible"}`}
        >
          {failures ? `${failures} failing` : "all pass"}
        </span>
      </div>
      <ul className="mt-4 space-y-2">
        {results.map((r) => (
          <li key={r.label} className="flex items-center justify-between gap-3 text-xs">
            <span className="text-muted-foreground">{r.label}</span>
            <span className={r.passes ? "text-susceptible" : "text-resistant"}>
              {formatRatio(r.ratio)} / {r.required}:1
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ThemeTokensPage() {
  return (
    <main className="min-h-dvh bg-background px-6 py-16">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold text-foreground">Theme tokens</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          Live preview of every design token in both themes, with WCAG AA contrast validation.
          Failing pairs are also logged to the console in development.
        </p>
        <div className="mt-10 grid gap-6 lg:grid-cols-2">
          <ThemePanel theme="dark" />
          <ThemePanel theme="light" />
        </div>
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <ContrastTable theme="dark" />
          <ContrastTable theme="light" />
        </div>
      </div>
    </main>
  );
}
