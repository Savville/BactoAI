import { AlertOctagon, CheckCircle2, AlertTriangle, Info } from "lucide-react";
import type { AmrSummary } from "@/lib/amr-summary.functions";

export const riskStyles: Record<string, string> = {
  low: "bg-susceptible/10 text-susceptible border-susceptible/30",
  moderate: "bg-primary/10 text-primary border-primary/30",
  high: "bg-resistant/10 text-resistant border-resistant/30",
  critical: "bg-resistant/20 text-resistant border-resistant/50",
};

export function AmrSummaryView({ summary }: { summary: AmrSummary }) {
  return (
    <div className="space-y-5">
      <div className={`rounded-2xl border p-4 ${riskStyles[summary.overall_risk]}`}>
        <div className="text-[10px] font-semibold uppercase tracking-wider">
          Overall AMR risk · {summary.overall_risk}
        </div>
        <div className="mt-1 text-sm font-semibold text-foreground">{summary.headline}</div>
        <p className="mt-2 text-xs text-muted-foreground leading-relaxed">{summary.summary}</p>
      </div>

      <div>
        <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
          Antibiotic risk estimates
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          {summary.drug_risks.map((d) => {
            const Icon =
              d.risk === "high"
                ? AlertOctagon
                : d.risk === "moderate"
                  ? AlertTriangle
                  : CheckCircle2;
            const color =
              d.risk === "high"
                ? "text-resistant"
                : d.risk === "moderate"
                  ? "text-primary"
                  : "text-susceptible";
            const bar =
              d.risk === "high"
                ? "bg-resistant"
                : d.risk === "moderate"
                  ? "bg-primary"
                  : "bg-susceptible";
            return (
              <div key={d.drug} className="rounded-xl border border-border p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm font-semibold">
                    <Icon size={14} className={color} /> {d.drug}
                  </div>
                  <span className={`text-[11px] font-semibold capitalize ${color}`}>
                    {d.risk} risk
                  </span>
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                    <div className={`h-full ${bar}`} style={{ width: `${d.confidence}%` }} />
                  </div>
                  <span className="text-[11px] font-mono text-muted-foreground">
                    {d.confidence}%
                  </span>
                </div>
                <p className="mt-2 text-[11px] text-muted-foreground leading-snug">{d.rationale}</p>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
            Why — supporting evidence
          </div>
          <ul className="space-y-2">
            {summary.evidence.map((e, i) => (
              <li key={i} className="text-xs">
                <span className="font-semibold text-foreground">{e.finding}</span>
                <span className="text-muted-foreground"> — {e.significance}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
            Recommended next steps
          </div>
          <ul className="space-y-1.5 list-disc pl-4 text-xs text-muted-foreground">
            {summary.recommendations.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="rounded-xl bg-muted/50 p-3 text-[11px] text-muted-foreground">
        <div className="flex items-center gap-1.5 font-semibold text-foreground">
          <Info size={12} /> Limitations
        </div>
        <ul className="mt-1 list-disc pl-4 space-y-0.5">
          {summary.limitations.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
        <p className="mt-2">
          Predicted by the BactoAI model ensemble. Research use only. Confirm with phenotypic susceptibility testing.
        </p>
      </div>
    </div>
  );
}
