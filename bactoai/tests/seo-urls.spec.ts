import { expect, test } from "@playwright/test";
import { SITE_URL, routeFileToPath } from "../src/lib/site-routes";
import { readdirSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const ROUTES_DIR = resolve(import.meta.dirname, "../src/routes");
const EXCLUDED = new Set(["/auth", "/theme-tokens", "/mcp", "/sitemap.xml"]);

function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) return walk(p);
    return /\.tsx?$/.test(name) ? [p] : [];
  });
}

/** Public page paths, derived from the route files on disk. */
const publicPaths = [
  ...new Set(
    walk(ROUTES_DIR)
      .map((f) => routeFileToPath(relative(ROUTES_DIR, f)))
      .filter((p): p is string => Boolean(p) && !EXCLUDED.has(p!)),
  ),
].sort();

test("every public route is registered in the sitemap with the canonical origin", async ({
  request,
}) => {
  const res = await request.get("/sitemap.xml");
  expect(res.status()).toBe(200);
  const xml = await res.text();

  const locs = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
  expect(locs.length).toBeGreaterThan(0);

  for (const loc of locs) {
    expect(loc.startsWith(`${SITE_URL}/`), `sitemap entry ${loc} must use ${SITE_URL}`).toBe(true);
  }

  const sitemapPaths = locs.map((l) => l.slice(SITE_URL.length)).sort();
  expect(sitemapPaths).toEqual(publicPaths);
});

for (const path of publicPaths) {
  test(`canonical and og:url on ${path} match ${SITE_URL}`, async ({ page }) => {
    const response = await page.goto(path, { waitUntil: "domcontentloaded" });
    expect(response?.status(), `${path} should render`).toBeLessThan(400);

    const expected = `${SITE_URL}${path}`;

    const canonicals = await page
      .locator('link[rel="canonical"]')
      .evaluateAll((els) => els.map((el) => el.getAttribute("href")));
    expect(canonicals, `${path} must declare exactly one canonical`).toHaveLength(1);
    expect(canonicals[0]).toBe(expected);

    const ogUrls = await page
      .locator('meta[property="og:url"]')
      .evaluateAll((els) => els.map((el) => el.getAttribute("content")));
    expect(ogUrls, `${path} must declare exactly one og:url`).toHaveLength(1);
    expect(ogUrls[0]).toBe(expected);

    const title = await page.title();
    expect(title.length).toBeGreaterThan(10);
    expect(title).not.toContain("Lovable");
  });
}
