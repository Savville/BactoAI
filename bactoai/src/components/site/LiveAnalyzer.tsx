import { useEffect, useState } from "react";
import { Link } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import {
  AlertOctagon,
  ArrowRight,
  FileUp,
  History,
  Loader2,
  Lock,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { generateAmrSummary, type AmrSummary } from "@/lib/amr-summary.functions";
import {
  ORGANISMS,
  SPECIMENS,
  parseGenome,
  validateGenomeFile,
  type SequenceStats,
} from "@/lib/genome-validation";
import { AmrSummaryView } from "./AmrSummaryView";

type Errors = Partial<
  Record<"file" | "isolate" | "organism" | "organismOther" | "specimen" | "date" | "notes", string>
>;

const inputCls =
  "w-full rounded-lg border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40";

export function LiveAnalyzer() {
  const [authed, setAuthed] = useState<boolean | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [stats, setStats] = useState<SequenceStats | null>(null);
  const [parsing, setParsing] = useState(false);
  const [meta, setMeta] = useState({
    isolate: "",
    organism: "",
    organismOther: "",
    specimen: "",
    date: "",
    location: "",
    notes: "",
  });
  const [errors, setErrors] = useState<Errors>({});
  const [phase, setPhase] = useState<"idle" | "running" | "done" | "error">("idle");
  const [summary, setSummary] = useState<AmrSummary | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);
  const run = useServerFn(generateAmrSummary);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setAuthed(!!data.session));
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_e, s) => setAuthed(!!s));
    return () => subscription.unsubscribe();
  }, []);

  const pickFile = async (f: File | null) => {
    setFile(f);
    setStats(null);
    setPhase("idle");
    const err = validateGenomeFile(f);
    if (err || !f) {
      setErrors((e) => ({ ...e, file: err ?? undefined }));
      return;
    }
    setParsing(true);
    try {
      const s = await parseGenome(f);
      setStats(s);
      setErrors((e) => ({ ...e, file: undefined }));
    } catch (e) {
      setErrors((prev) => ({
        ...prev,
        file: e instanceof Error ? e.message : "Couldn't read this file.",
      }));
    } finally {
      setParsing(false);
    }
  };

  const validate = (): Errors => {
    const e: Errors = {};
    if (!file) e.file = "Choose a genome file to analyze.";
    else if (errors.file) e.file = errors.file;
    else if (!stats) e.file = "The file is still being checked — wait a moment.";
    if (!meta.isolate.trim()) e.isolate = "Isolate ID is required.";
    else if (meta.isolate.trim().length > 80)
      e.isolate = "Keep the isolate ID under 80 characters.";
    if (!meta.organism) e.organism = "Select the organism.";
    if (meta.organism === "Other" && meta.organismOther.trim().length < 2)
      e.organismOther = "Enter the organism name.";
    if (!meta.specimen) e.specimen = "Select the specimen source.";
    if (meta.date && new Date(meta.date) > new Date())
      e.date = "Collection date can't be in the future.";
    if (meta.notes.length > 1000) e.notes = "Notes must be under 1000 characters.";
    return e;
  };

  const submit = async (ev: React.FormEvent) => {
    ev.preventDefault();
    const e = validate();
    setErrors(e);
    if (Object.values(e).some(Boolean) || !file || !stats) return;
    setPhase("running");
    setServerError(null);
    try {
      const { excerpt: _excerpt, ...statsNoExcerpt } = stats;
      const form = new FormData();
      form.append("file", file, file.name);
      form.append(
        "meta",
        JSON.stringify({
          isolateLabel: meta.isolate.trim(),
          organism: meta.organism === "Other" ? meta.organismOther.trim() : meta.organism,
          specimenSource: meta.specimen,
          collectionDate: meta.date || null,
          location: meta.location.trim() || null,
          clinicalNotes: meta.notes.trim() || null,
          stats: statsNoExcerpt,
        }),
      );
      const res = await run({ data: form });
      if (!res.ok) {
        setServerError(res.message);
        setPhase("error");
        return;
      }
      setSummary(res.summary);
      setPhase("done");
    } catch (err) {
      console.error(err);
      setServerError(
        /unauthorized/i.test(String(err))
          ? "Please sign in again."
          : "Something went wrong. Please try again.",
      );
      setPhase("error");
    }
  };

  const fieldErr = (k: keyof Errors) =>
    errors[k] ? (
      <p className="mt-1 text-[11px] text-resistant" role="alert">
        {errors[k]}
      </p>
    ) : null;
  const border = (k: keyof Errors) => (errors[k] ? "border-resistant" : "border-border");

  return (
    <div className="relative">
      <div className="absolute -inset-4 bg-primary opacity-10 blur-3xl rounded-3xl" />
      <div className="relative rounded-3xl border border-border bg-card shadow-elegant overflow-hidden">
        <div className="flex flex-wrap items-center gap-2 px-4 sm:px-5 py-3 border-b border-border bg-muted/40">
          <span className="w-2.5 h-2.5 rounded-full bg-destructive/60" />
          <span className="w-2.5 h-2.5 rounded-full bg-muted-foreground/40" />
          <span className="w-2.5 h-2.5 rounded-full bg-susceptible/60" />
          <div className="min-w-0 text-xs text-muted-foreground font-mono">
            app.bactoai.co.ke/analyze
          </div>
          {authed && (
            <Link
              to="/history"
              className="ml-auto inline-flex items-center gap-1 text-[11px] font-semibold text-primary"
            >
              <History size={12} /> My history
            </Link>
          )}
        </div>

        <div className="p-4 sm:p-6 space-y-5 min-h-[400px] md:min-h-[520px]">
          {false ? (
            <div className="rounded-2xl border border-dashed border-primary/30 bg-primary/5 p-4 sm:p-8 text-center">
              <Lock size={22} className="mx-auto text-primary" />
              <div className="mt-3 text-sm font-semibold text-foreground">
                Sign in to analyze your own genomes
              </div>
              <p className="mt-2 text-xs text-muted-foreground max-w-sm mx-auto">
                Risk predictions for uploaded FASTA/FASTQ files are available to registered lab
                users. Sample isolates remain open to everyone.
              </p>
              <Link
                to="/auth"
                className="mt-5 inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-xs font-semibold text-primary-foreground"
              >
                Sign in or create an account <ArrowRight size={14} />
              </Link>
            </div>
          ) : phase === "done" && summary ? (
            <>
              <AmrSummaryView summary={summary} />
              <div className="grid sm:flex gap-2 justify-center">
                <button
                  type="button"
                  onClick={() => {
                    setPhase("idle");
                    setSummary(null);
                  }}
                  className="inline-flex items-center gap-1.5 rounded-full border border-border px-4 py-1.5 text-xs font-semibold"
                >
                  <RotateCcw size={12} /> Analyze another
                </button>
                <Link
                  to="/history"
                  className="inline-flex items-center gap-1.5 rounded-full bg-primary px-4 py-1.5 text-xs font-semibold text-primary-foreground"
                >
                  <History size={12} /> View history
                </Link>
              </div>
            </>
          ) : (
            <form onSubmit={submit} noValidate className="space-y-4">
              <label
                className={`block rounded-2xl border-2 border-dashed p-5 cursor-pointer transition ${errors.file ? "border-resistant/60 bg-resistant/5" : "border-primary/30 bg-primary/5 hover:border-primary/60"}`}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  pickFile(e.dataTransfer.files?.[0] ?? null);
                }}
              >
                <input
                  type="file"
                  accept=".fasta,.fa,.fna,.fastq,.fq,.gz"
                  className="sr-only"
                  onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
                />
                <div className="grid grid-cols-[auto_minmax(0,1fr)] items-center gap-4">
                  {parsing ? (
                    <Loader2 className="animate-spin text-primary" size={22} />
                  ) : (
                    <FileUp className="text-primary" size={22} />
                  )}
                  <div className="min-w-0 break-words text-sm">
                    <div className="font-semibold text-foreground">
                      {file ? file.name : "Browse or drop a genome file *"}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {parsing
                        ? "Checking file…"
                        : stats
                          ? `${stats.format} · ${stats.records.toLocaleString()} record(s) · ${(stats.totalBases / 1e6).toFixed(2)} Mb · GC ${stats.gcPercent}% · N50 ${stats.n50.toLocaleString()}`
                          : "FASTA / FASTQ (optionally .gz) · up to 25 MB"}
                    </div>
                  </div>
                </div>
              </label>
              {fieldErr("file")}

              <div className="grid sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium">Isolate ID *</label>
                  <input
                    className={`${inputCls} ${border("isolate")}`}
                    value={meta.isolate}
                    maxLength={80}
                    placeholder="e.g. KNH-2026-0142"
                    onChange={(e) => setMeta({ ...meta, isolate: e.target.value })}
                  />
                  {fieldErr("isolate")}
                </div>
                <div>
                  <label className="text-xs font-medium">Organism *</label>
                  <select
                    className={`${inputCls} ${border("organism")}`}
                    value={meta.organism}
                    onChange={(e) => setMeta({ ...meta, organism: e.target.value })}
                  >
                    <option value="">Select…</option>
                    {ORGANISMS.map((o) => (
                      <option key={o}>{o}</option>
                    ))}
                  </select>
                  {fieldErr("organism")}
                </div>
                {meta.organism === "Other" && (
                  <div className="sm:col-span-2">
                    <label className="text-xs font-medium">Organism name *</label>
                    <input
                      className={`${inputCls} ${border("organismOther")}`}
                      value={meta.organismOther}
                      maxLength={120}
                      onChange={(e) => setMeta({ ...meta, organismOther: e.target.value })}
                    />
                    {fieldErr("organismOther")}
                  </div>
                )}
                <div>
                  <label className="text-xs font-medium">Specimen source *</label>
                  <select
                    className={`${inputCls} ${border("specimen")}`}
                    value={meta.specimen}
                    onChange={(e) => setMeta({ ...meta, specimen: e.target.value })}
                  >
                    <option value="">Select…</option>
                    {SPECIMENS.map((o) => (
                      <option key={o}>{o}</option>
                    ))}
                  </select>
                  {fieldErr("specimen")}
                </div>
                <div>
                  <label className="text-xs font-medium">Collection date</label>
                  <input
                    type="date"
                    className={`${inputCls} ${border("date")}`}
                    value={meta.date}
                    onChange={(e) => setMeta({ ...meta, date: e.target.value })}
                  />
                  {fieldErr("date")}
                </div>
                <div className="sm:col-span-2">
                  <label className="text-xs font-medium">Location / facility</label>
                  <input
                    className={`${inputCls} border-border`}
                    value={meta.location}
                    maxLength={120}
                    placeholder="e.g. Nairobi, Kenya"
                    onChange={(e) => setMeta({ ...meta, location: e.target.value })}
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="text-xs font-medium">Clinical / lab notes</label>
                  <textarea
                    rows={2}
                    className={`${inputCls} ${border("notes")}`}
                    value={meta.notes}
                    maxLength={1000}
                    placeholder="Optional — no patient identifiers"
                    onChange={(e) => setMeta({ ...meta, notes: e.target.value })}
                  />
                  {fieldErr("notes")}
                </div>
              </div>

              {phase === "error" && serverError && (
                <div className="rounded-xl border border-resistant/30 bg-resistant/5 p-3 text-xs">
                  <div className="flex items-center gap-2 font-semibold text-resistant">
                    <AlertOctagon size={14} /> Analysis couldn't be completed
                  </div>
                  <p className="mt-1 text-muted-foreground">{serverError}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={phase === "running" || parsing}
                className="w-full inline-flex items-center justify-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground disabled:opacity-60"
              >
                {phase === "running" ? (
                  <>
                    <Loader2 size={14} className="animate-spin" /> Running prediction…
                  </>
                ) : (
                  <>
                    <Sparkles size={14} /> Run resistance prediction
                  </>
                )}
              </button>
              <p className="text-center text-[11px] text-muted-foreground">
                Your genome file is sent securely to the BactoAI prediction engine and is deleted
                after analysis.
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
