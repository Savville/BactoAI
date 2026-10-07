import { useState } from "react";
import { toast } from "sonner";
import { Mail, Loader2, CheckCircle2 } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

export function Newsletter() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success">("idle");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (status !== "idle") return;
    if (!email.trim() || !email.includes("@")) {
      toast.error("Please enter a valid email.");
      return;
    }
    setStatus("loading");
    const { error } = await supabase.from("contact_submissions").insert({
      form_type: "newsletter",
      full_name: "Newsletter subscriber",
      email: email.trim(),
    });
    if (error) {
      setStatus("idle");
      toast.error("Couldn't subscribe. Try again shortly.");
      return;
    }
    setStatus("success");
    toast.success("You're on the list.");
    setEmail("");
  }

  return (
    <section className="py-16">
      <div className="mx-auto max-w-5xl px-6">
        <div className="rounded-3xl border border-border bg-card p-8 md:p-12 grid md:grid-cols-[1fr_auto] gap-8 items-center shadow-soft">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 text-primary text-[11px] font-semibold uppercase tracking-widest px-3 py-1">
              <Mail size={12} /> Newsletter
            </div>
            <h2 className="mt-4 text-2xl md:text-3xl font-bold text-foreground">
              Subscribe for AMR field notes and model updates
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Monthly AMR field notes, model updates, and pilot opportunities. No spam.
            </p>
          </div>
          <form onSubmit={submit} className="flex gap-2 w-full md:w-auto">
            <input
              type="email"
              required
              maxLength={255}
              placeholder="you@hospital.org"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={status !== "idle"}
              className="min-w-0 md:w-72 rounded-full border border-border bg-background px-5 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
            <button
              type="submit"
              disabled={status !== "idle"}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-soft hover:shadow-elegant transition disabled:opacity-70"
            >
              {status === "loading" && <Loader2 size={14} className="animate-spin" />}
              {status === "success" && <CheckCircle2 size={14} />}
              {status === "idle" ? "Subscribe" : status === "loading" ? "…" : "Done"}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
