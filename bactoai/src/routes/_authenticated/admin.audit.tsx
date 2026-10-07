import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { Loader2, LogOut, ShieldAlert, ScrollText } from "lucide-react";
import { listAuditLog } from "@/lib/submissions.functions";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/admin/audit")({
  head: () => ({
    meta: [
      { title: "Audit log — BactoAI Admin" },
      {
        name: "description",
        content: "Immutable record of admin access to contact submissions and admin role changes.",
      },
      { name: "robots", content: "noindex,nofollow" },
    ],
  }),
  component: AdminAudit,
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

const ACTION_LABEL: Record<string, string> = {
  contact_submissions_viewed: "Viewed contact submissions",
  contact_submissions_viewed_mcp: "Viewed contact submissions (assistant)",
  submission_stats_viewed_mcp: "Viewed submission stats (assistant)",
  role_granted: "Role granted",
  role_updated: "Role changed",
  role_revoked: "Role revoked",
};

function AdminAudit() {
  const fetchAudit = useServerFn(listAuditLog);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ["admin-audit-log"],
    queryFn: () => fetchAudit(),
  });

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
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div>
            <Link to="/" className="text-xs font-semibold text-primary uppercase tracking-widest">
              BactoAI
            </Link>
            <h1 className="text-xl font-bold text-foreground">Audit log</h1>
          </div>
          <div className="flex items-center gap-2">
            <Link
              to="/admin/submissions"
              className="rounded-full border border-border px-4 py-2 text-xs font-semibold hover:bg-card transition"
            >
              Submissions
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

      <main className="mx-auto max-w-7xl px-6 py-10">
        <p className="mb-6 flex items-start gap-2 text-xs text-muted-foreground">
          <ScrollText size={14} className="mt-0.5 shrink-0" />
          Every admin view of contact submissions and every admin role change is recorded here.
          Entries are written server-side and cannot be edited or deleted from the app.
        </p>

        {isLoading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="animate-spin" size={16} /> Loading audit log…
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-destructive/40 bg-destructive/5 p-6 text-sm">
            {error instanceof Error ? error.message : "Unknown error"}
          </div>
        )}

        {data && data.length === 0 && (
          <p className="text-sm text-muted-foreground">No audit entries yet.</p>
        )}

        {data && data.length > 0 && (
          <div className="overflow-hidden rounded-2xl border border-border">
            <table className="w-full text-sm">
              <thead className="bg-card/60 text-xs uppercase tracking-widest text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold">When</th>
                  <th className="px-4 py-3 text-left font-semibold">Action</th>
                  <th className="px-4 py-3 text-left font-semibold">Actor</th>
                  <th className="px-4 py-3 text-left font-semibold">Target</th>
                  <th className="px-4 py-3 text-left font-semibold">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.map((row) => (
                  <tr key={row.id} className="align-top">
                    <td className="px-4 py-3 whitespace-nowrap text-xs text-muted-foreground">
                      {new Date(row.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 font-medium text-foreground">
                      {ACTION_LABEL[row.action] ?? row.action}
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">
                      {row.actor_email ?? row.actor_id ?? "system"}
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">
                      {row.target_table ?? "—"}
                      {row.target_id && (
                        <div className="font-mono text-[10px] opacity-70">{row.target_id}</div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground max-w-md">
                      {row.details ? (
                        <pre className="whitespace-pre-wrap font-mono text-[10px]">
                          {row.details}
                        </pre>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
