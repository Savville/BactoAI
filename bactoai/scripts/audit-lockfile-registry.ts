/**
 * Fails CI if bun.lock pins packages to a private/internal registry.
 * The lockfile must resolve against the public npm registry so that
 * GitHub Actions (and any external contributor) can run `bun install`.
 */
import { readFileSync } from "node:fs";

const LOCKFILE = "bun.lock";
const BANNED_PATTERNS = ["europe-west4-npm.pkg.dev", "sandbox-npm-cache", "pkg.dev/lovable"];

const content = readFileSync(LOCKFILE, "utf8");
const hits = BANNED_PATTERNS.filter((p) => content.includes(p));

if (hits.length > 0) {
  console.error(
    `✖ ${LOCKFILE} contains private sandbox registry URLs (${hits.join(", ")}).\n` +
      `  Regenerate it against the public registry: rm bun.lock && bun install`,
  );
  process.exit(1);
}

console.log(`✔ ${LOCKFILE} resolves against the public npm registry.`);
