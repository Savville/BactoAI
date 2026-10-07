import { createServerFn } from "@tanstack/react-start";
import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";

export type Prediction = {
  drug: string;
  status: "Resistant" | "Susceptible";
  confidence: number;
  /** True when the backend flagged the call as low confidence (lab confirmation advised). */
  uncertain?: boolean;
};

export type AnalysisSuccess = {
  ok: true;
  organism: string | null;
  predictions: Prediction[];
  fileName: string;
  fileSizeKb: number;
};

export type AnalysisFailure = {
  ok: false;
  code: "not_configured" | "invalid_file" | "upstream";
  message: string;
};

export type AnalysisResponse = AnalysisSuccess | AnalysisFailure;

const MAX_BYTES = 25 * 1024 * 1024; // 25 MB
const ALLOWED_EXTENSIONS = [
  ".fasta",
  ".fa",
  ".fna",
  ".fastq",
  ".fq",
  ".fasta.gz",
  ".fastq.gz",
  ".fq.gz",
  ".fa.gz",
];

function hasAllowedExtension(name: string): boolean {
  const lower = name.toLowerCase();
  return ALLOWED_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

function fail(code: AnalysisFailure["code"], message: string): AnalysisFailure {
  return { ok: false, code, message };
}

export const analyzeGenome = createServerFn({ method: "POST" })
  .inputValidator((data: unknown) => {
    if (!(data instanceof FormData)) throw new Error("Expected multipart form data");
    return data;
  })
  .handler(async ({ data }): Promise<AnalysisResponse> => {
    const file = data.get("file");
    if (!(file instanceof File)) {
      return fail("invalid_file", "No genome file was received. Choose a FASTA or FASTQ file.");
    }
    if (!hasAllowedExtension(file.name)) {
      return fail(
        "invalid_file",
        "Unsupported file type. Upload a .fasta, .fa, .fna, .fastq or .fq file (optionally gzipped).",
      );
    }
    if (file.size === 0) {
      return fail("invalid_file", "The uploaded file is empty.");
    }
    if (file.size > MAX_BYTES) {
      return fail("invalid_file", "The file is larger than 25 MB. Upload a smaller genome file.");
    }

    // Basic FASTA/FASTQ sanity check on the first bytes (skipped for gzipped files).
    if (!file.name.toLowerCase().endsWith(".gz")) {
      const head = await file.slice(0, 4096).text();
      const first = head.trimStart().charAt(0);
      if (first !== ">" && first !== "@") {
        return fail(
          "invalid_file",
          "This doesn't look like a FASTA or FASTQ file — the first character should be '>' or '@'.",
        );
      }
    }

    const apiUrl = process.env["MODEL_API_URL"];
    const apiKey = process.env["MODEL_API_KEY"];
    if (!apiUrl || !apiKey) {
      return fail(
        "not_configured",
        "The live prediction engine isn't connected yet. Our team is deploying it — please check back soon or request a demo below.",
      );
    }

    const form = new FormData();
    form.append("file", file, file.name);

    let res: Response;
    try {
      res = await fetch(`${apiUrl.replace(/\/+$/, "")}/predict`, {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}` },
        body: form,
      });
    } catch {
      return fail(
        "upstream",
        "We couldn't reach the prediction engine. Please try again in a few minutes.",
      );
    }

    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        console.error("[analyze] model API rejected the request", res.status);
        return fail(
          "upstream",
          "The prediction engine rejected the request. Our team has been notified.",
        );
      }
      if (res.status === 400 || res.status === 422) {
        return fail(
          "invalid_file",
          "The prediction engine couldn't read this genome file. Check that it's a complete bacterial whole-genome FASTA/FASTQ.",
        );
      }
      console.error("[analyze] model API error", res.status);
      return fail(
        "upstream",
        "The prediction engine hit an error while analyzing this genome. Please try again shortly.",
      );
    }

    let payload: unknown;
    try {
      payload = await res.json();
    } catch {
      return fail("upstream", "The prediction engine returned an unreadable response.");
    }

    // The Flask API (/api/v1/predict) returns { results: [{ antibiotic, probability,
    // label, status, confidence }] } where status may be "uncertain" and confidence is
    // a HIGH/MEDIUM/LOW level. A legacy { predictions: [{ drug, status, confidence }] }
    // shape is still accepted.
    const raw = payload as {
      organism?: unknown;
      results?: unknown;
      predictions?: unknown;
    };
    const items = Array.isArray(raw.results) ? raw.results : raw.predictions;
    if (!Array.isArray(items) || items.length === 0) {
      return fail("upstream", "The prediction engine returned no predictions for this genome.");
    }

    const predictions: Prediction[] = [];
    for (const p of items as Array<Record<string, unknown>>) {
      const drugRaw = typeof p.antibiotic === "string" ? p.antibiotic : p.drug;
      const drug = typeof drugRaw === "string" ? drugRaw.trim() : "";
      if (!drug) continue;

      const labelRaw = typeof p.label === "string" ? p.label : p.status;
      const label = typeof labelRaw === "string" ? labelRaw.toLowerCase() : "";
      if (label !== "resistant" && label !== "susceptible") {
        // status "uncertain" carries no label; fall back to the probability if present.
        if (typeof p.probability !== "number" || !Number.isFinite(p.probability)) continue;
      }
      const resistant =
        label === "resistant" ||
        (label !== "susceptible" && (p.probability as number) >= 0.5);

      let confidence: number | null = null;
      if (typeof p.probability === "number" && Number.isFinite(p.probability)) {
        const pr = Math.max(0, Math.min(1, p.probability));
        confidence = Math.round((resistant ? pr : 1 - pr) * 100);
      } else if (typeof p.confidence === "number" && Number.isFinite(p.confidence)) {
        confidence = Math.max(0, Math.min(100, Math.round(p.confidence)));
      }
      if (confidence === null) continue;

      predictions.push({
        drug,
        status: resistant ? "Resistant" : "Susceptible",
        confidence,
        uncertain:
          p.status === "uncertain" ||
          (typeof p.confidence === "string" && p.confidence.toUpperCase() === "LOW"),
      });
    }

    if (predictions.length === 0) {
      return fail(
        "upstream",
        "The prediction engine returned predictions in an unexpected format.",
      );
    }

    return {
      ok: true,
      organism:
        typeof raw.organism === "string" && raw.organism.trim() ? raw.organism.trim() : null,
      predictions,
      fileName: file.name,
      fileSizeKb: Math.max(1, Math.round(file.size / 1024)),
    };
  });
