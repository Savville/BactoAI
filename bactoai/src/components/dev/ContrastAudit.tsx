import { useEffect } from "react";
import {
  TOKEN_PAIRS,
  contrastRatio,
  formatRatio,
  requiredRatio,
  type AuditResult,
} from "@/lib/contrast";

/** Audits a theme by mounting a detached probe element carrying the theme class. */
export function auditTheme(themeClass: "dark" | "light"): AuditResult[] {
  const probe = document.createElement("div");
  probe.className = themeClass;
  probe.style.position = "absolute";
  probe.style.opacity = "0";
  probe.style.pointerEvents = "none";
  document.body.appendChild(probe);
  const styles = getComputedStyle(probe);
  const results = TOKEN_PAIRS.map((pair) => {
    const fgValue = styles.getPropertyValue(pair.fg).trim();
    const bgValue = styles.getPropertyValue(pair.bg).trim();
    const ratio = contrastRatio(fgValue, bgValue);
    const required = requiredRatio(pair.kind);
    return {
      ...pair,
      fgValue,
      bgValue,
      ratio,
      required,
      passes: ratio !== null && ratio >= required,
    };
  });
  probe.remove();
  return results;
}

/** Dev-only: logs a WCAG AA report for every theme token pair. */
export function ContrastAudit() {
  useEffect(() => {
    if (!import.meta.env.DEV) return;
    const themes: Array<"dark" | "light"> = ["dark", "light"];
    for (const theme of themes) {
      const results = auditTheme(theme);
      const failures = results.filter((r) => !r.passes);
      if (failures.length === 0) {
        console.info(`[contrast] ${theme} theme: all ${results.length} token pairs pass WCAG AA.`);
        continue;
      }
      console.warn(
        `[contrast] ${theme} theme: ${failures.length}/${results.length} token pairs fail WCAG AA`,
      );
      console.table(
        failures.map((f) => ({
          pair: f.label,
          fg: f.fgValue,
          bg: f.bgValue,
          ratio: formatRatio(f.ratio),
          required: `${f.required}:1`,
        })),
      );
    }
  }, []);

  return null;
}
