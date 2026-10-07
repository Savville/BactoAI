/**
 * WCAG contrast utilities for the design-system tokens.
 * Values are read from the live CSS custom properties so light/dark
 * themes are both auditable at runtime.
 */

export type Rgb = { r: number; g: number; b: number };

export function parseColor(input: string): Rgb | null {
  const value = input.trim();
  if (!value) return null;

  const rgbMatch = value.match(/^rgba?\(([^)]+)\)$/i);
  if (rgbMatch) {
    const parts = rgbMatch[1]
      .split(/[\s,/]+/)
      .filter(Boolean)
      .map(Number);
    if (parts.length >= 3 && parts.slice(0, 3).every((n) => Number.isFinite(n))) {
      return { r: parts[0], g: parts[1], b: parts[2] };
    }
    return null;
  }

  const hex = value.replace("#", "");
  if (/^[0-9a-f]{3}$/i.test(hex)) {
    return {
      r: parseInt(hex[0] + hex[0], 16),
      g: parseInt(hex[1] + hex[1], 16),
      b: parseInt(hex[2] + hex[2], 16),
    };
  }
  if (/^[0-9a-f]{6}$/i.test(hex)) {
    return {
      r: parseInt(hex.slice(0, 2), 16),
      g: parseInt(hex.slice(2, 4), 16),
      b: parseInt(hex.slice(4, 6), 16),
    };
  }
  return null;
}

function channel(c: number) {
  const s = c / 255;
  return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
}

export function relativeLuminance({ r, g, b }: Rgb) {
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

export function contrastRatio(a: string | Rgb, b: string | Rgb): number | null {
  const c1 = typeof a === "string" ? parseColor(a) : a;
  const c2 = typeof b === "string" ? parseColor(b) : b;
  if (!c1 || !c2) return null;
  const l1 = relativeLuminance(c1);
  const l2 = relativeLuminance(c2);
  const [hi, lo] = l1 >= l2 ? [l1, l2] : [l2, l1];
  return (hi + 0.05) / (lo + 0.05);
}

/** Token pairs that must satisfy WCAG AA. */
export type TokenPair = {
  label: string;
  fg: string;
  bg: string;
  /** "text" = 4.5:1, "large"/"ui" = 3:1, "decorative" = informational only */
  kind: "text" | "large" | "ui" | "decorative";
};

export const TOKEN_PAIRS: TokenPair[] = [
  { label: "foreground on background", fg: "--foreground", bg: "--background", kind: "text" },
  {
    label: "muted-foreground on background",
    fg: "--muted-foreground",
    bg: "--background",
    kind: "text",
  },
  { label: "card-foreground on card", fg: "--card-foreground", bg: "--card", kind: "text" },
  {
    label: "popover-foreground on popover",
    fg: "--popover-foreground",
    bg: "--popover",
    kind: "text",
  },
  {
    label: "primary-foreground on primary",
    fg: "--primary-foreground",
    bg: "--primary",
    kind: "text",
  },
  {
    label: "secondary-foreground on secondary",
    fg: "--secondary-foreground",
    bg: "--secondary",
    kind: "text",
  },
  { label: "accent-foreground on accent", fg: "--accent-foreground", bg: "--accent", kind: "text" },
  {
    label: "destructive-foreground on destructive",
    fg: "--destructive-foreground",
    bg: "--destructive",
    kind: "text",
  },
  { label: "resistant on background", fg: "--resistant", bg: "--background", kind: "text" },
  { label: "susceptible on background", fg: "--susceptible", bg: "--background", kind: "text" },
  { label: "resistant on card", fg: "--resistant", bg: "--card", kind: "text" },
  { label: "susceptible on card", fg: "--susceptible", bg: "--card", kind: "text" },
  {
    label: "primary-glow on background (large text)",
    fg: "--primary-glow",
    bg: "--background",
    kind: "large",
  },
  {
    label: "border on background (decorative)",
    fg: "--border",
    bg: "--background",
    kind: "decorative",
  },
  { label: "ring on background (UI)", fg: "--ring", bg: "--background", kind: "ui" },
];

export function requiredRatio(kind: TokenPair["kind"]) {
  if (kind === "text") return 4.5;
  if (kind === "decorative") return 1;
  return 3;
}

export type AuditResult = TokenPair & {
  fgValue: string;
  bgValue: string;
  ratio: number | null;
  required: number;
  passes: boolean;
};

export function readToken(name: string, el?: Element): string {
  if (typeof window === "undefined") return "";
  const target = el ?? document.documentElement;
  return getComputedStyle(target).getPropertyValue(name).trim();
}

export function auditTokens(pairs: TokenPair[] = TOKEN_PAIRS): AuditResult[] {
  return pairs.map((pair) => {
    const fgValue = readToken(pair.fg);
    const bgValue = readToken(pair.bg);
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
}

export function formatRatio(ratio: number | null) {
  return ratio === null ? "n/a" : `${ratio.toFixed(2)}:1`;
}
