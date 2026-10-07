import { Mail, Linkedin, MapPin, ArrowRight, Loader2, CheckCircle2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";

type Status = "idle" | "loading" | "success" | "error";

export function Contact() {
  const [status, setStatus] = useState<Status>("idle");
  const [form, setForm] = useState({ name: "", email: "", organization: "", message: "" });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (status === "loading" || status === "success") return;
    setStatus("loading");
    const { error } = await supabase.from("contact_submissions").insert({
      form_type: "general",
      full_name: form.name.trim(),
      email: form.email.trim(),
      organization: form.organization.trim() || null,
      message: form.message.trim() || null,
    });
    if (error) {
      console.error("Contact submission failed", error);
      setStatus("error");
      toast.error("We couldn't send your message. Please email info@bactoai.co.ke.");
      return;
    }
    setStatus("success");
    toast.success("Thanks — we'll be in touch within 2 business days.");
  }

  return (
    <section id="contact" className="py-24 md:py-32 bg-card/40">
      <div className="mx-auto max-w-7xl px-6">
        <div className="rounded-3xl bg-gradient-hero p-1 shadow-elegant">
          <div className="rounded-[calc(theme(borderRadius.3xl)-4px)] bg-background p-4 sm:p-8 md:p-14 grid lg:grid-cols-2 gap-12">
            <div>
              <div className="text-sm font-semibold text-primary uppercase tracking-widest">
                Request a Demo
              </div>
              <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
                Request a technical demo for your laboratory.
              </h2>
              <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
                Partner with BactoAI to accelerate AMR diagnostics through AI and genomics. Tell us about your hospital or laboratory, and we'll schedule a technical demonstration with your isolates.
              </p>
              <ul className="mt-8 space-y-3 text-sm">
                <li className="flex items-center gap-3">
                  <Mail size={16} className="text-primary" />
                  <a href="mailto:info@bactoai.co.ke" className="hover:text-primary transition">
                    info@bactoai.co.ke
                  </a>
                </li>
                <li className="flex items-center gap-3">
                  <Linkedin size={16} className="text-primary" />
                  <a
                    href="https://www.linkedin.com/in/bactoai-model-32303335a"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-primary transition"
                  >
                    linkedin.com/in/bactoai-model
                  </a>
                </li>
                <li className="flex items-center gap-3">
                  <MapPin size={16} className="text-primary" /> Nairobi, Kenya
                </li>
              </ul>
            </div>
            <form
              onSubmit={handleSubmit}
              className="rounded-2xl border border-border bg-card p-4 sm:p-6 md:p-8 space-y-4"
            >
              <div>
                <label
                  htmlFor="contact-name"
                  className="text-xs font-semibold text-muted-foreground"
                >
                  Full name
                </label>
                <input
                  id="contact-name"
                  required
                  maxLength={100}
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  disabled={status === "success"}
                  className="mt-1 w-full rounded-lg border border-border bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                />
              </div>
              <div>
                <label
                  htmlFor="contact-email"
                  className="text-xs font-semibold text-muted-foreground"
                >
                  Work email
                </label>
                <input
                  id="contact-email"
                  type="email"
                  required
                  maxLength={255}
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  disabled={status === "success"}
                  className="mt-1 w-full rounded-lg border border-border bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                />
              </div>
              <div>
                <label
                  htmlFor="contact-org"
                  className="text-xs font-semibold text-muted-foreground"
                >
                  Hospital / Laboratory
                </label>
                <input
                  id="contact-org"
                  maxLength={150}
                  value={form.organization}
                  onChange={(e) => setForm({ ...form, organization: e.target.value })}
                  disabled={status === "success"}
                  className="mt-1 w-full rounded-lg border border-border bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                />
              </div>
              <div>
                <label
                  htmlFor="contact-message"
                  className="text-xs font-semibold text-muted-foreground"
                >
                  Reason for demo request & technical needs
                </label>
                <textarea
                  id="contact-message"
                  rows={4}
                  maxLength={1000}
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                  disabled={status === "success"}
                  className="mt-1 w-full rounded-lg border border-border bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                />
              </div>
              <button
                type="submit"
                disabled={status === "loading" || status === "success"}
                className="w-full inline-flex items-center justify-center gap-2 rounded-full bg-primary py-3 text-sm font-semibold text-primary-foreground shadow-elegant hover:opacity-95 transition disabled:opacity-70"
              >
                {status === "loading" && (
                  <>
                    <Loader2 size={16} className="animate-spin" /> Sending…
                  </>
                )}
                {status === "success" && (
                  <>
                    <CheckCircle2 size={16} /> Message received
                  </>
                )}
                {(status === "idle" || status === "error") && (
                  <>
                    Request a Demo <ArrowRight size={16} />
                  </>
                )}
              </button>
              {status === "error" && (
                <p className="text-[11px] text-destructive text-center">
                  Something went wrong. Please try again or email us directly.
                </p>
              )}
              <p className="text-[11px] text-muted-foreground text-center">
                We respond within 2 business days. Your information stays private.
              </p>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
