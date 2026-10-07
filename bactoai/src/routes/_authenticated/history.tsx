import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Download, FileJson, Loader2, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";
import { AmrSummaryView, riskStyles } from "@/components/site/AmrSummaryView";
import type { AmrSummary } from "@/lib/amr-summary.functions";

export const Route = createFileRoute("/_authenticated/history")({
  head: () => ({
    meta: [
      { title: "Prediction history — BactoAI" },
      {
        name: "description",
        content: "Review, filter, and download your previous BactoAI genome analyses.",
      },
      { property: "og:title", content: "Prediction history — BactoAI" },
      { property: "og:description", content: "Your previous genome AMR risk analyses on BactoAI." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: HistoryPage,
});

function download(name: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
const csvCell = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;

function HistoryPage() {
  const qc = useQueryClient();
  const {
    data = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["genome_analyses"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("genome_analyses")
        .select("*")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  });
  const [q, setQ] = useState("");
  const [organism, setOrganism] = useState("");
  const [risk, setRisk] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [open, setOpen] = useState<string | null>(null);

  const organisms = useMemo(() => [...new Set(data.map((r) => r.organism))].sort(), [data]);
  const rows = useMemo(
    () =>
      data.filter((r) => {
        const t =
          `${r.isolate_label} ${r.file_name} ${r.specimen_source} ${r.location ?? ""}`.toLowerCase();
        const d = r.created_at.slice(0, 10);
        return (
          (!q || t.includes(q.toLowerCase())) &&
          (!organism || r.organism === organism) &&
          (!risk || r.overall_risk === risk) &&
          (!from || d >= from) &&
          (!to || d <= to)
        );
      }),
    [data, q, organism, risk, from, to],
  );

  const exportCsv = () => {
    const head = [
      "Date",
      "Isolate",
      "Organism",
      "Specimen",
      "Collection date",
      "Location",
      "File",
      "Overall risk",
      "Headline",
      "Drug risks",
    ];
    const lines = rows.map((r) => {
      const s = r.summary as unknown as AmrSummary;
      return [
        r.created_at,
        r.isolate_label,
        r.organism,
        r.specimen_source,
        r.collection_date,
        r.location,
        r.file_name,
        r.overall_risk,
        s.headline,
        s.drug_risks.map((d) => `${d.drug}: ${d.risk} (${d.confidence}%)`).join("; "),
      ]
        .map(csvCell)
        .join(",");
    });
    download(
      `bactoai-history-${new Date().toISOString().slice(0, 10)}.csv`,
      [head.join(","), ...lines].join("\n"),
      "text/csv",
    );
  };

  const remove = async (id: string) => {
    const { error } = await supabase.from("genome_analyses").delete().eq("id", id);
    if (error) return toast.error("Couldn't delete this record.");
    toast.success("Record deleted");
    qc.invalidateQueries({ queryKey: ["genome_analyses"] });
  };

  const input = "rounded-lg border border-border bg-background px-3 py-2 text-sm";
  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="pt-32 pb-24 mx-auto max-w-6xl px-6">
        <div className="text-sm font-semibold text-primary uppercase tracking-widest">
          Your workspace
        </div>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-foreground">
          Prediction history
        </h1>
        <p className="mt-3 text-muted-foreground">
          Review, filter, and download your previous genome analyses.
        </p>

        <div className="mt-8 flex flex-wrap gap-3 items-end">
          <input
            className={`${input} flex-1 min-w-48`}
            placeholder="Search isolate, file, specimen…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <select className={input} value={organism} onChange={(e) => setOrganism(e.target.value)}>
            <option value="">All organisms</option>
            {organisms.map((o) => (
              <option key={o}>{o}</option>
            ))}
          </select>
          <select className={input} value={risk} onChange={(e) => setRisk(e.target.value)}>
            <option value="">All risk levels</option>
            {["low", "moderate", "high", "critical"].map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
          <input
            type="date"
            className={input}
            value={from}
            onChange={(e) => setFrom(e.target.value)}
            aria-label="From date"
          />
          <input
            type="date"
            className={input}
            value={to}
            onChange={(e) => setTo(e.target.value)}
            aria-label="To date"
          />
          <button
            onClick={exportCsv}
            disabled={!rows.length}
            className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-50"
          >
            <Download size={14} /> Export CSV ({rows.length})
          </button>
        </div>

        <div className="mt-6 space-y-3">
          {isLoading && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="animate-spin" size={16} /> Loading…
            </div>
          )}
          {error && (
            <div className="text-resistant text-sm">
              Couldn't load your history. Please refresh.
            </div>
          )}
          {!isLoading && !error && rows.length === 0 && (
            <div className="rounded-2xl border border-dashed border-border p-10 text-center text-muted-foreground">
              {data.length ? (
                "No analyses match these filters."
              ) : (
                <>
                  No analyses yet.{" "}
                  <Link to="/" hash="demo" className="text-primary font-semibold">
                    Run your first one
                  </Link>
                  .
                </>
              )}
            </div>
          )}
          {rows.map((r) => {
            const s = r.summary as unknown as AmrSummary;
            return (
              <div key={r.id} className="rounded-2xl border border-border bg-card">
                <button
                  className="w-full text-left p-4 flex flex-wrap items-center gap-3"
                  onClick={() => setOpen(open === r.id ? null : r.id)}
                >
                  <span
                    className={`text-[11px] font-semibold uppercase rounded-full border px-2.5 py-0.5 ${riskStyles[r.overall_risk]}`}
                  >
                    {r.overall_risk}
                  </span>
                  <span className="font-semibold text-foreground">{r.isolate_label}</span>
                  <span className="text-sm italic text-muted-foreground">{r.organism}</span>
                  <span className="text-xs text-muted-foreground">{r.specimen_source}</span>
                  <span className="ml-auto text-xs text-muted-foreground">
                    {new Date(r.created_at).toLocaleString()}
                  </span>
                </button>
                {open === r.id && (
                  <div className="border-t border-border p-5 space-y-4">
                    <div className="text-xs text-muted-foreground font-mono">
                      {r.file_name} · {(r.file_size_bytes / 1048576).toFixed(2)} MB
                    </div>
                    <AmrSummaryView summary={s} />
                    <div className="flex gap-2">
                      <button
                        onClick={() =>
                          download(
                            `${r.isolate_label}-amr-summary.json`,
                            JSON.stringify(r, null, 2),
                            "application/json",
                          )
                        }
                        className="inline-flex items-center gap-1.5 rounded-full border border-border px-4 py-1.5 text-xs font-semibold"
                      >
                        <FileJson size={12} /> Download JSON
                      </button>
                      <button
                        onClick={() => remove(r.id)}
                        className="inline-flex items-center gap-1.5 rounded-full border border-resistant/40 text-resistant px-4 py-1.5 text-xs font-semibold"
                      >
                        <Trash2 size={12} /> Delete
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </main>
      <Footer />
    </div>
  );
}
