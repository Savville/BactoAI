import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { useMemo } from "react";
import { Loader2, LogOut, ShieldAlert, Download, TrendingUp } from "lucide-react";
import { listContactSubmissions, type ContactSubmissionRow } from "@/lib/submissions.functions";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/admin/dashboard")({
  head: () => ({
    meta: [
      { title: "Weekly enquiries dashboard — BactoAI Admin" },
      {
        name: "description",
        content:
          "Weekly breakdown of BactoAI demo requests, partner leads and team enquiries, with CSV export.",
      },
      { name: "robots", content: "noindex,nofollow" },
    ],
  }),
  component: AdminDashboard,
  errorComponent: ({ error }) => (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="max-w-md text-center">
        <ShieldAlert className="mx-auto text-destructive" size={32} />
        <h2 className="mt-3 text-lg font-semibold">Access denied</h2>
        <p className="mt-2 text-sm text-muted-foreground">{(error as Error).message}</p>
      </div>
    </div>
  ),
});

const CATEGORIES = [
  { key: "demo", label: "Demo requests" },
  { key: "partner", label: "Partner leads" },
  { key: "general", label: "Team enquiries" },
  { key: "newsletter", label: "Newsletter" },
] as const;

type WeekBucket = {
  weekStart: Date;
  label: string;
  total: number;
  counts: Record<string, number>;
};

function startOfWeek(input: Date) {
  const d = new Date(input);
  d.setHours(0, 0, 0, 0);
  const day = (d.getDay() + 6) % 7; // Monday = 0
  d.setDate(d.getDate() - day);
  return d;
}

function buildWeeks(rows: ContactSubmissionRow[], weeks = 8): WeekBucket[] {
  const thisWeek = startOfWeek(new Date());
  const buckets: WeekBucket[] = [];
  for (let i = weeks - 1; i >= 0; i--) {
    const start = new Date(thisWeek);
    start.setDate(start.getDate() - i * 7);
    buckets.push({
      weekStart: start,
      label: start.toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      total: 0,
      counts: Object.fromEntries(CATEGORIES.map((c) => [c.key, 0])),
    });
  }
  for (const row of rows) {
    const start = startOfWeek(new Date(row.created_at)).getTime();
    const bucket = buckets.find((b) => b.weekStart.getTime() === start);
    if (!bucket) continue;
    bucket.total += 1;
    const key = CATEGORIES.some((c) => c.key === row.form_type) ? row.form_type : "general";
    bucket.counts[key] = (bucket.counts[key] ?? 0) + 1;
  }
  return buckets;
}

function csvCell(value: string | null) {
  const v = value ?? "";
  return /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
}

function exportCsv(rows: ContactSubmissionRow[]) {
  const header = [
    "received_at",
    "week_starting",
    "type",
    "full_name",
    "email",
    "organization",
    "message",
    "metadata",
  ];
  const lines = [header.join(",")];
  for (const row of rows) {
    lines.push(
      [
        csvCell(new Date(row.created_at).toISOString()),
        csvCell(startOfWeek(new Date(row.created_at)).toISOString().slice(0, 10)),
        csvCell(row.form_type),
        csvCell(row.full_name),
        csvCell(row.email),
        csvCell(row.organization),
        csvCell(row.message),
        csvCell(row.metadata),
      ].join(","),
    );
  }
  const blob = new Blob([`\uFEFF${lines.join("\r\n")}`], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `bactoai-enquiries-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  toast.success(`Exported ${rows.length} enquir${rows.length === 1 ? "y" : "ies"}.`);
}

function AdminDashboard() {
  const fetchSubmissions = useServerFn(listContactSubmissions);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ["contact-submissions"],
    queryFn: () => fetchSubmissions(),
  });

  const weeks = useMemo(() => buildWeeks(data ?? []), [data]);
  const peak = Math.max(1, ...weeks.map((w) => w.total));
  const current = weeks[weeks.length - 1];
  const previous = weeks[weeks.length - 2];
  const delta = current && previous ? current.total - previous.total : 0;

  async function handleSignOut() {
    await queryClient.cancelQueries();
    queryClient.clear();
    await supabase.auth.signOut();
    toast.success("Signed out.");
    navigate({ to: "/auth", replace: true });
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card/40">
        <div className="mx-auto max-w-7xl px-6 py-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <Link to="/" className="text-xs font-semibold text-primary uppercase tracking-widest">
              BactoAI
            </Link>
            <h1 className="text-xl font-bold text-foreground">Weekly enquiries</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => data && exportCsv(data)}
              disabled={!data || data.length === 0}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground transition hover:opacity-90 disabled:opacity-50"
            >
              <Download size={14} /> Export CSV
            </button>
            <Link
              to="/admin/submissions"
              className="rounded-full border border-border px-4 py-2 text-xs font-semibold hover:bg-card transition"
            >
              All submissions
            </Link>
            <Link
              to="/admin/audit"
              className="rounded-full border border-border px-4 py-2 text-xs font-semibold hover:bg-card transition"
            >
              Audit log
            </Link>
            <button
              onClick={handleSignOut}
              className="inline-flex items-center gap-2 rounded-full border border-border px-4 py-2 text-xs font-semibold hover:bg-card transition"
            >
              <LogOut size={14} /> Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-10 space-y-8">
        {isLoading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="animate-spin" size={16} /> Loading enquiries…
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-destructive/40 bg-destructive/5 p-6 text-sm">
            <div className="font-semibold text-foreground">Unable to load enquiries</div>
            <p className="mt-1 text-muted-foreground">
              {error instanceof Error ? error.message : "Unknown error"}
            </p>
          </div>
        )}

        {data && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {CATEGORIES.map((c) => (
                <div key={c.key} className="rounded-2xl border border-border bg-card p-5">
                  <div className="text-xs uppercase tracking-widest text-muted-foreground">
                    {c.label}
                  </div>
                  <div className="mt-2 text-3xl font-bold text-foreground">
                    {current?.counts[c.key] ?? 0}
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    this week ·{" "}
                    {
                      data.filter(
                        (r) =>
                          (CATEGORIES.some((x) => x.key === r.form_type)
                            ? r.form_type
                            : "general") === c.key,
                      ).length
                    }{" "}
                    all time
                  </div>
                </div>
              ))}
            </div>

            <div className="rounded-2xl border border-border bg-card p-6">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h2 className="text-sm font-semibold text-foreground">Last 8 weeks</h2>
                  <p className="text-xs text-muted-foreground">
                    {current?.total ?? 0} enquiries this week
                    {previous ? (
                      <span className={delta >= 0 ? "text-primary" : "text-destructive"}>
                        {" "}
                        ({delta >= 0 ? "+" : ""}
                        {delta} vs last week)
                      </span>
                    ) : null}
                  </p>
                </div>
                <TrendingUp className="text-primary" size={18} />
              </div>

              <div className="mt-6 flex items-end gap-3 h-40">
                {weeks.map((w) => (
                  <div
                    key={w.weekStart.toISOString()}
                    className="flex-1 flex flex-col items-center gap-2"
                  >
                    <div className="text-xs font-semibold text-foreground">{w.total || ""}</div>
                    <div
                      className="w-full rounded-t-md bg-primary/70 transition-all"
                      style={{
                        height: `${Math.round((w.total / peak) * 100)}%`,
                        minHeight: w.total ? "6px" : "2px",
                      }}
                      title={`Week of ${w.label}: ${w.total}`}
                    />
                    <div className="text-[10px] text-muted-foreground whitespace-nowrap">
                      {w.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="overflow-hidden rounded-2xl border border-border">
              <table className="w-full text-sm">
                <thead className="bg-card/60 text-xs uppercase tracking-widest text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold">Week starting</th>
                    {CATEGORIES.map((c) => (
                      <th key={c.key} className="px-4 py-3 text-left font-semibold">
                        {c.label}
                      </th>
                    ))}
                    <th className="px-4 py-3 text-left font-semibold">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {[...weeks].reverse().map((w) => (
                    <tr key={w.weekStart.toISOString()}>
                      <td className="px-4 py-3 whitespace-nowrap text-xs text-muted-foreground">
                        {w.weekStart.toLocaleDateString()}
                      </td>
                      {CATEGORIES.map((c) => (
                        <td key={c.key} className="px-4 py-3 text-foreground">
                          {w.counts[c.key] ?? 0}
                        </td>
                      ))}
                      <td className="px-4 py-3 font-semibold text-foreground">{w.total}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
