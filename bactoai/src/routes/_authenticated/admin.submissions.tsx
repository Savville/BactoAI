import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { Loader2, LogOut, Mail, Building2, ShieldAlert } from "lucide-react";
import { listContactSubmissions } from "@/lib/submissions.functions";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/admin/submissions")({
  head: () => ({
    meta: [
      { title: "Contact submissions — BactoAI Admin" },
      {
        name: "description",
        content: "Review demo and partnership inquiries submitted through the BactoAI website.",
      },
      { name: "robots", content: "noindex,nofollow" },
    ],
  }),
  component: AdminSubmissions,
  errorComponent: ({ error }) => (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="max-w-md text-center">
        <ShieldAlert className="mx-auto text-destructive" size={32} />
        <h2 className="mt-3 text-lg font-semibold">Access denied</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          {(error as Error).message.includes("Forbidden") ||
          (error as Error).message.includes("permission")
            ? "Your account is signed in, but does not have the admin role required to view contact submissions."
            : (error as Error).message}
        </p>
      </div>
    </div>
  ),
});

function AdminSubmissions() {
  const fetchSubmissions = useServerFn(listContactSubmissions);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ["contact-submissions"],
    queryFn: () => fetchSubmissions(),
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
            <h1 className="text-xl font-bold text-foreground">Contact submissions</h1>
          </div>
          <div className="flex items-center gap-2">
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

      <main className="mx-auto max-w-7xl px-6 py-10">
        {isLoading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="animate-spin" size={16} /> Loading submissions…
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-destructive/40 bg-destructive/5 p-6">
            <div className="flex items-start gap-3">
              <ShieldAlert className="text-destructive shrink-0" size={20} />
              <div>
                <div className="text-sm font-semibold text-foreground">
                  Unable to load submissions
                </div>
                <p className="mt-1 text-sm text-muted-foreground">
                  {error instanceof Error ? (error as Error).message : "Unknown error"}
                </p>
                <p className="mt-2 text-xs text-muted-foreground">
                  You must have the <code className="font-mono">admin</code> role assigned in the
                  database to view this page.
                </p>
              </div>
            </div>
          </div>
        )}

        {data && data.length === 0 && (
          <p className="text-sm text-muted-foreground">No submissions yet.</p>
        )}

        {data && data.length > 0 && (
          <div className="space-y-4">
            <p className="text-xs text-muted-foreground">
              Showing {data.length} most recent submission{data.length === 1 ? "" : "s"}.
            </p>
            <div className="overflow-hidden rounded-2xl border border-border">
              <table className="w-full text-sm">
                <thead className="bg-card/60 text-xs uppercase tracking-widest text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold">Received</th>
                    <th className="px-4 py-3 text-left font-semibold">Type</th>
                    <th className="px-4 py-3 text-left font-semibold">Name</th>
                    <th className="px-4 py-3 text-left font-semibold">Contact</th>
                    <th className="px-4 py-3 text-left font-semibold">Message</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {data.map((row) => (
                    <tr key={row.id} className="align-top">
                      <td className="px-4 py-3 whitespace-nowrap text-xs text-muted-foreground">
                        {new Date(row.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex rounded-full bg-primary/10 text-primary px-2 py-0.5 text-xs font-semibold uppercase tracking-widest">
                          {row.form_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-medium text-foreground">{row.full_name}</td>
                      <td className="px-4 py-3 text-xs">
                        <a
                          href={`mailto:${row.email}`}
                          className="inline-flex items-center gap-1 text-primary hover:underline"
                        >
                          <Mail size={12} /> {row.email}
                        </a>
                        {row.organization && (
                          <div className="mt-1 inline-flex items-center gap-1 text-muted-foreground">
                            <Building2 size={12} /> {row.organization}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-xs text-muted-foreground max-w-md">
                        {row.message || <span className="italic">No message</span>}
                        {row.metadata != null && (
                          <pre className="mt-1 text-[10px] font-mono text-muted-foreground/70 whitespace-pre-wrap">
                            {row.metadata}
                          </pre>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
