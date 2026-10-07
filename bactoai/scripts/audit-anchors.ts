/**
 * Anchor / deep-link audit.
 *
 * Verifies that every internal anchor used in the app resolves to a real
 * element id on the route(s) that actually render it:
 *
 *  - href="#foo"      -> every route that renders this file must contain id="foo"
 *  - href="/path#foo" -> route "/path" must exist and must contain id="foo"
 *
 * Run: bun run scripts/audit-anchors.ts
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, resolve, dirname } from "node:path";

const SRC = resolve(import.meta.dirname, "../src");
const ROUTES_DIR = join(SRC, "routes");

function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) return walk(p);
    return /\.tsx?$/.test(name) ? [p] : [];
  });
}

const allFiles = walk(SRC);
const source = new Map<string, string>();
for (const f of allFiles) source.set(f, readFileSync(f, "utf8"));

function idsIn(file: string): string[] {
  const src = source.get(file) ?? "";
  return [...src.matchAll(/\bid="([^"{}]+)"/g)].map((m) => m[1]);
}

function resolveImport(fromFile: string, spec: string): string | null {
  let base: string;
  if (spec.startsWith("@/")) base = join(SRC, spec.slice(2));
  else if (spec.startsWith(".")) base = resolve(dirname(fromFile), spec);
  else return null;
  for (const cand of [
    base,
    `${base}.tsx`,
    `${base}.ts`,
    join(base, "index.tsx"),
    join(base, "index.ts"),
  ]) {
    if (source.has(cand)) return cand;
  }
  return null;
}

function localImports(file: string): string[] {
  const src = source.get(file) ?? "";
  return [...src.matchAll(/from\s+"([^"]+)"/g)]
    .map((m) => resolveImport(file, m[1]))
    .filter((f): f is string => Boolean(f));
}

/** Files transitively reachable from a route file (its component graph). */
function reachable(entry: string): Set<string> {
  const seen = new Set<string>([entry]);
  const queue = [entry];
  while (queue.length) {
    for (const next of localImports(queue.pop()!)) {
      if (!seen.has(next)) {
        seen.add(next);
        queue.push(next);
      }
    }
  }
  return seen;
}

type RouteInfo = { path: string; file: string; files: Set<string>; ids: Set<string> };

const routes: RouteInfo[] = [];
for (const file of walk(ROUTES_DIR)) {
  const src = source.get(file)!;
  const m = src.match(/createFileRoute\(\s*"([^"]+)"\s*\)/);
  if (!m) continue;
  const files = reachable(file);
  const ids = new Set<string>();
  for (const f of files) for (const id of idsIn(f)) ids.add(id);
  routes.push({ path: m[1], file, files, ids });
}

const problems: string[] = [];

for (const [file, src] of source) {
  if (file.includes("/routeTree.gen.ts") || file.startsWith(join(SRC, "assets"))) continue;
  const hrefs = [...src.matchAll(/href="(\/[^"]*#[^"]+|#[^"]+)"/g)].map((m) => m[1]);
  if (!hrefs.length) continue;
  const owners = routes.filter((r) => r.files.has(file));

  for (const href of hrefs) {
    if (href.startsWith("#")) {
      const id = href.slice(1);
      if (!owners.length) {
        problems.push(`${file}: bare anchor "${href}" in a file no route renders`);
        continue;
      }
      for (const owner of owners) {
        if (!owner.ids.has(id)) {
          problems.push(
            `${file}: bare anchor "${href}" does not exist on route ${owner.path} (which renders this file) — use an absolute deep link instead`,
          );
        }
      }
    } else {
      const [rawPath, id] = [href.slice(0, href.indexOf("#")), href.slice(href.indexOf("#") + 1)];
      const path = rawPath === "" || rawPath === "/" ? "/" : rawPath.replace(/\/$/, "");
      const target = routes.find((r) => r.path === path);
      if (!target) {
        problems.push(`${file}: deep link "${href}" points at unknown route ${path}`);
      } else if (!target.ids.has(id)) {
        const elsewhere = routes.filter((r) => r.ids.has(id)).map((r) => r.path);
        problems.push(
          `${file}: deep link "${href}" — route ${path} has no id="${id}"` +
            (elsewhere.length ? ` (found on: ${elsewhere.join(", ")})` : ""),
        );
      }
    }
  }
}

console.log(`Audited ${routes.length} routes for internal anchors.`);
if (problems.length) {
  console.error(`\n${problems.length} broken anchor(s):`);
  for (const p of problems) console.error(`  - ${p.replace(`${SRC}/`, "src/")}`);
  process.exit(1);
}
console.log("All internal anchors resolve to a real section on their target route.");
