/**
 * Single source of truth for the public site URL and the set of
 * publicly indexable routes.
 *
 * The route list is derived automatically from the route files in
 * `src/routes` (the same files TanStack Router registers), so a new page
 * can't be missed by the sitemap or the SEO audit. Non-public routes are
 * filtered out by the rules below.
 */
export const SITE_URL = "https://bactoai.co.ke";

/** Routes that exist but must never appear in the sitemap. */
const EXCLUDED_PATHS = new Set([
  "/auth", // sign-in
  "/theme-tokens", // internal design-system preview
  "/mcp", // machine endpoint
  "/sitemap.xml", // the sitemap itself
  "/robots.txt",
]);

/** Per-path sitemap hints; everything else uses sane defaults. */
const HINTS: Record<string, { changefreq?: string; priority?: string }> = {
  "/": { changefreq: "weekly", priority: "1.0" },
  "/technology": { changefreq: "monthly", priority: "0.9" },
  "/research": { changefreq: "monthly", priority: "0.9" },
  "/about": { changefreq: "monthly", priority: "0.8" },
  "/pricing": { changefreq: "monthly", priority: "0.8" },
  "/contact": { changefreq: "yearly", priority: "0.7" },
  "/blog": { changefreq: "weekly", priority: "0.7" },
  "/resources": { changefreq: "monthly", priority: "0.6" },
  "/press": { changefreq: "monthly", priority: "0.6" },
  "/careers": { changefreq: "yearly", priority: "0.4" },
  "/privacy": { changefreq: "yearly", priority: "0.3" },
  "/terms": { changefreq: "yearly", priority: "0.3" },
};

/** Convert a route-file path (relative to src/routes) into a URL path. */
export function routeFileToPath(relative: string): string | null {
  const withoutExt = relative.replace(/\.tsx?$/, "");
  const segments = withoutExt.split("/").flatMap((s) => s.split("."));

  // Skip the root layout, generated/served-only files and non-page routes.
  if (segments.some((s) => s === "" || s === "__root")) return null;
  // Pathless layouts (_authenticated), dynamic params ($slug), escaped
  // segments ([.well-known], sitemap[.]xml) and splats are never static
  // public HTML pages.
  if (
    segments.some(
      (s) => s.startsWith("_") || s.startsWith("$") || s.includes("[") || s.includes("]"),
    )
  ) {
    return null;
  }
  if (relative.startsWith("api/")) return null;

  const path = "/" + segments.filter((s) => s !== "index").join("/");
  return path === "/" ? "/" : path.replace(/\/$/, "");
}

export interface SitemapEntry {
  path: string;
  changefreq?: string;
  priority?: string;
}

/**
 * Every publicly indexable route, derived from the registered route files.
 * Uses `import.meta.glob` so the list is computed at build time from the
 * filesystem rather than hand-maintained.
 */
export function publicRoutes(): SitemapEntry[] {
  const files = import.meta.glob("/src/routes/**/*.{ts,tsx}", { eager: false });
  const paths = new Set<string>();

  for (const key of Object.keys(files)) {
    const relative = key.replace("/src/routes/", "");
    const path = routeFileToPath(relative);
    if (!path) continue;
    if (EXCLUDED_PATHS.has(path)) continue;
    paths.add(path);
  }

  return [...paths]
    .sort((a, b) => (a === "/" ? -1 : b === "/" ? 1 : a.localeCompare(b)))
    .map((path) => ({ path, ...(HINTS[path] ?? { changefreq: "monthly", priority: "0.5" }) }));
}
