import { createServerFn } from "@tanstack/react-start";
import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";
import { z } from "zod";

// The summary shape is kept so saved history rows and AmrSummaryView keep working.
// Every value is now derived from the BactoAI Flask backend's predictions by fixed
// rules. No language model is involved.

const MAX_BYTES = 25 * 1024 * 1024; // 25 MB

const Meta = z.object({
  isolateLabel: z.string().trim().min(1).max(80),
  organism: z.string().trim().min(2).max(120),
  specimenSource: z.string().trim().min(2).max(80),
  collectionDate: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/)
    .nullable(),
  location: z.string().trim().max(120).nullable(),
  clinicalNotes: z.string().trim().max(1000).nullable(),
  stats: z.object({
    format: z.enum(["FASTA", "FASTQ"]),
    records: z.number().int().min(1),
    totalBases: z.number().int().min(100),
    gcPercent: z.number().min(0).max(100),
    nPercent: z.number().min(0).max(100),
    longestRecord: z.number().int(),
    n50: z.number().int(),
    headers: z.array(z.string().max(120)).max(8),
  }),
});

export type AmrSummary = {
  overall_risk: "low" | "moderate" | "high" | "critical";
  headline: string;
  summary: string;
  drug_risks: {
    drug: string;
    risk: "low" | "moderate" | "high";
    confidence: number;
    rationale: string;
  }[];
  evidence: { finding: string; significance: string }[];
  recommendations: string[];
  limitations: string[];
};

export type AmrSummaryResult =
  | { ok: true; id: string; summary: AmrSummary }
  | { ok: false; message: string };

type BackendResult = {
  antibiotic?: unknown;
  probability?: unknown;
  lower_bound?: unknown;
  upper_bound?: unknown;
  label?: unknown;
  status?: unknown;
  confidence?: unknown;
  recommendation?: unknown;
};

const isNum = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const pct = (v: number) => Math.round(Math.max(0, Math.min(1, v)) * 100);

/** Convert Flask /api/v1/predict results into the summary the UI renders. */
function buildSummary(results: BackendResult[], stats: z.infer<typeof Meta>["stats"]): AmrSummary {
  const drug_risks: AmrSummary["drug_risks"] = [];

  for (const r of results) {
    const drug = typeof r.antibiotic === "string" ? r.antibiotic.trim() : "";
    if (!drug || !isNum(r.probability)) continue;

    const status = typeof r.status === "string" ? r.status.toLowerCase() : "";
    const label = typeof r.label === "string" ? r.label.toLowerCase() : "";
    const resistant = label ? label === "resistant" : r.probability >= 0.5;
    const risk: "low" | "moderate" | "high" =
      status === "uncertain" ? "moderate" : resistant ? "high" : "low";

    const interval =
      isNum(r.lower_bound) && isNum(r.upper_bound)
        ? ` (95% interval ${pct(r.lower_bound)}% to ${pct(r.upper_bound)}%)`
        : "";
    const advice = typeof r.recommendation === "string" ? r.recommendation : "";

    drug_risks.push({
      drug,
      risk,
      confidence: pct(resistant ? r.probability : 1 - r.probability),
      rationale: `Resistance probability ${pct(r.probability)}%${interval}. ${advice}`.trim(),
    });
  }

  const resistant = drug_risks.filter((d) => d.risk === "high");
  const uncertain = drug_risks.filter((d) => d.risk === "moderate");
  const susceptible = drug_risks.filter((d) => d.risk === "low");

  const overall_risk: AmrSummary["overall_risk"] =
    resistant.length >= 2
      ? "critical"
      : resistant.length === 1
        ? "high"
        : uncertain.length > 0
          ? "moderate"
          : "low";

  const names = (list: typeof drug_risks) => list.map((d) => d.drug).join(", ");
  const parts: string[] = [];
  if (resistant.length) parts.push(`Predicted resistant to ${names(resistant)}.`);
  if (uncertain.length)
    parts.push(`Low-confidence calls for ${names(uncertain)}; confirm in the laboratory.`);
  if (susceptible.length) parts.push(`Predicted susceptible to ${names(susceptible)}.`);

  const evidence: AmrSummary["evidence"] = [...resistant, ...uncertain].map((d) => ({
    finding: `${d.drug}: ${d.risk === "high" ? "predicted resistant" : "uncertain"}`,
    significance: d.rationale,
  }));
  evidence.push({
    finding: `${stats.format}, ${stats.records.toLocaleString()} record(s), ${(stats.totalBases / 1e6).toFixed(2)} Mb`,
    significance: `GC ${stats.gcPercent}%, N50 ${stats.n50.toLocaleString()}, ${stats.nPercent}% ambiguous bases.`,
  });

  const recommendations: string[] = [];
  if (resistant.length)
    recommendations.push(`Avoid ${names(resistant)} until susceptibility is confirmed.`);
  if (uncertain.length)
    recommendations.push(`Repeat or confirm the low-confidence results for ${names(uncertain)}.`);
  recommendations.push("Confirm every result with phenotypic antimicrobial susceptibility testing.");
  recommendations.push("Follow your facility's antimicrobial stewardship guidance.");

  return {
    overall_risk,
    headline: `${resistant.length} of ${drug_risks.length} antibiotics predicted resistant`,
    summary: parts.join(" "),
    drug_risks,
    evidence,
    recommendations,
    limitations: [
      "Predictions come from an ensemble trained on k-mer and gene-signature features.",
      "Results depend on assembly quality and on the organisms seen in training data.",
      "Research use only. Not a substitute for laboratory susceptibility testing.",
    ],
  };
}

export const generateAmrSummary = createServerFn({ method: "POST" })
  .inputValidator((data: unknown) => {
    if (!(data instanceof FormData)) throw new Error("Expected multipart form data");
    return data;
  })
  .handler(async ({ data, context }): Promise<AmrSummaryResult> => {
    const file = data.get("file");
    if (!(file instanceof File)) return { ok: false, message: "No genome file was received." };
    if (file.size < 1 || file.size > MAX_BYTES)
      return { ok: false, message: "The genome file must be between 1 byte and 25 MB." };

    let meta: z.infer<typeof Meta>;
    try {
      meta = Meta.parse(JSON.parse(String(data.get("meta") ?? "")));
    } catch {
      return { ok: false, message: "The sample details were incomplete or invalid." };
    }

    const apiUrl = process.env["MODEL_API_URL"];
    const apiKey = process.env["MODEL_API_KEY"];
    if (!apiUrl || !apiKey) {
      return {
        ok: false,
        message: "The prediction engine isn't connected yet. Please check back soon.",
      };
    }

    const form = new FormData();
    form.append("file", file, file.name);
    form.append("sample_id", meta.isolateLabel);
    if (meta.clinicalNotes) form.append("notes", meta.clinicalNotes);

    let res: Response;
    try {
      res = await fetch(`${apiUrl.replace(/\/+$/, "")}/predict`, {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}` },
        body: form,
      });
    } catch (err) {
      console.error("[amr] backend unreachable", err);
      return {
        ok: false,
        message: "We couldn't reach the prediction engine. Please try again in a few minutes.",
      };
    }

    if (!res.ok) {
      console.error("[amr] backend error", res.status);
      if (res.status === 401 || res.status === 403)
        return { ok: false, message: "The prediction engine rejected the request." };
      if (res.status === 400 || res.status === 422) {
        const body = (await res.json().catch(() => null)) as { error?: string } | null;
        return {
          ok: false,
          message:
            body?.error ??
            "The prediction engine couldn't read this genome file. Check it is a complete bacterial genome.",
        };
      }
      return {
        ok: false,
        message: "The prediction engine hit an error while analyzing this genome. Please try again.",
      };
    }

    let payload: { results?: unknown };
    try {
      payload = (await res.json()) as { results?: unknown };
    } catch {
      return { ok: false, message: "The prediction engine returned an unreadable response." };
    }
    if (!Array.isArray(payload.results) || payload.results.length === 0)
      return { ok: false, message: "The prediction engine returned no predictions." };

    const summary = buildSummary(payload.results as BackendResult[], meta.stats);
    if (summary.drug_risks.length === 0)
      return { ok: false, message: "The prediction engine returned an unexpected format." };

    let id = "";
    if (context && (context as any).supabase && (context as any).userId) {
      const { data: row, error } = await (context as any).supabase
        .from("genome_analyses")
        .insert({
          user_id: (context as any).userId,
          isolate_label: meta.isolateLabel,
          organism: meta.organism,
          specimen_source: meta.specimenSource,
          collection_date: meta.collectionDate,
          location: meta.location,
          clinical_notes: meta.clinicalNotes,
          file_name: file.name,
          file_size_bytes: file.size,
          sequence_stats: meta.stats,
          overall_risk: summary.overall_risk,
          summary,
        })
        .select("id")
        .single();
      if (error) console.error("[amr] save failed", error);
      if (row) id = row.id;
    }

    return { ok: true, id, summary };
  });
