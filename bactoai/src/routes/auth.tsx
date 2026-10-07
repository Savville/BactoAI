import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

export const Route = createFileRoute("/auth")({
  ssr: false,
  validateSearch: (s: Record<string, unknown>): { next?: string } =>
    typeof s.next === "string" ? { next: s.next } : {},

  head: () => ({
    meta: [
      { title: "Sign in — BactoAI" },
      {
        name: "description",
        content:
          "Sign in or create a BactoAI account to analyze bacterial genomes and review your results.",
      },
      { name: "robots", content: "noindex,nofollow" },
    ],
  }),
  component: AuthPage,
});

const CUSTOMER_HOME = "/history";
const ADMIN_HOME = "/admin/submissions";

// Only same-origin relative paths are safe redirect targets.
function safeNext(next?: string) {
  return next && next.startsWith("/") && !next.startsWith("//") ? next : null;
}

// UX routing only — admin pages still enforce the role server-side.
async function destinationFor(userId: string, next: string | null) {
  const { data } = await supabase
    .from("user_roles")
    .select("role")
    .eq("user_id", userId)
    .eq("role", "admin")
    .maybeSingle();
  const isAdmin = !!data;
  if (next && (isAdmin || !next.startsWith("/admin"))) return next;
  return isAdmin ? ADMIN_HOME : CUSTOMER_HOME;
}

function AuthPage() {
  const { next } = Route.useSearch();
  const target = safeNext(next);
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Covers returning from the email verification link too.
    supabase.auth.getUser().then(async ({ data }) => {
      if (!data.user) return;
      window.location.replace(await destinationFor(data.user.id, target));
    });
  }, [target]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      if (mode === "signup") {
        const redirect = `${window.location.origin}/auth${target ? `?next=${encodeURIComponent(target)}` : ""}`;
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: { emailRedirectTo: redirect },
        });
        if (error) throw error;
        toast.success("Account created. Check your email to verify, then you can start analyzing.");
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        toast.success("Signed in.");
        window.location.replace(await destinationFor(data.user.id, target));
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Authentication failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-6">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 shadow-elegant">
        <div className="text-center">
          <Link to="/" className="text-xs font-semibold text-primary uppercase tracking-widest">
            BactoAI
          </Link>
          <h1 className="mt-3 text-2xl font-bold text-foreground">
            {mode === "signin" ? "Sign in to BactoAI" : "Create your BactoAI account"}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {mode === "signin"
              ? "Upload genome samples, get AMR risk summaries and review your analysis history."
              : "Free account for labs and researchers to analyze bacterial genomes for antimicrobial resistance."}
          </p>
        </div>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label htmlFor="auth-email" className="text-xs font-semibold text-muted-foreground">
              Email
            </label>
            <input
              id="auth-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>
          <div>
            <label htmlFor="auth-password" className="text-xs font-semibold text-muted-foreground">
              Password
            </label>
            <input
              id="auth-password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full inline-flex items-center justify-center gap-2 rounded-full bg-primary py-3 text-sm font-semibold text-primary-foreground shadow-elegant hover:opacity-95 transition disabled:opacity-70"
          >
            {loading && <Loader2 size={16} className="animate-spin" />}
            {mode === "signin" ? "Sign in" : "Create account"}
          </button>
        </form>
        <button
          onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
          className="mt-4 w-full text-xs text-muted-foreground hover:text-primary transition"
        >
          {mode === "signin"
            ? "New to BactoAI? Create an account"
            : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}
