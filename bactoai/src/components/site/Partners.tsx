import { useState } from "react";
import { ArrowRight, Handshake, Loader2, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";
import { Reveal } from "./Reveal";

const programmes = [
  { name: "CDIE Catalyst Grant", detail: "Grant" },
  { name: "East Africa BioDesign", detail: "Programme" },
  {
    name: "GEES Bootcamp",
    detail: "KU × Lancaster SET Workshop · 2nd place · March 2025",
  },
  { name: "Kenyatta Innovation Centre", detail: "Incubation support" },
];

const partnershipTypes = [
  "Clinical validation study",
  "Sequencing / data partnership",
  "Research collaboration",
  "Pilot deployment",
  "Investment / grant",
  "Other",
];

export function Partners() {
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [form, setForm] = useState({
    name: "",
    email: "",
    organization: "",
    role: "",
    type: partnershipTypes[0],
    message: "",
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim()) return;
    if (status === "loading" || status === "success") return;
    setStatus("loading");
    const { error } = await supabase.from("contact_submissions").insert({
      form_type: "partner",
      full_name: form.name.trim(),
      email: form.email.trim(),
      organization: form.organization.trim() || null,
      message: form.message.trim() || null,
      metadata: { role: form.role || null, partnership_type: form.type },
    });
    if (error) {
      console.error("Partner submission failed", error);
      setStatus("error");
      toast.error("We couldn't send your inquiry. Please email info@bactoai.co.ke.");
      return;
    }
    setStatus("success");
    toast.success("Thanks — we'll be in touch within 2 business days.");
  }

  return (
    <section
      id="partners"
      className="relative py-24 bg-card/40 border-y border-border overflow-hidden"
    >
      <div
        className="absolute inset-0 bg-gradient-mesh opacity-40 pointer-events-none"
        aria-hidden
      />
      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal className="text-center">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Programmes &amp; recognition
          </div>
          <h2 className="mt-4 text-3xl md:text-4xl font-bold tracking-tight text-foreground">
            Recognised through Kenya and East Africa's innovation ecosystem
          </h2>
          <p className="mt-4 text-muted-foreground max-w-2xl mx-auto">
            {
              "Developed through competitive innovation programmes in Kenya and East Africa, and recognised for translational health-tech impacts\n\n"
            }
          </p>
        </Reveal>

        {/* Programmes & recognition grid */}
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {programmes.map((p) => (
            <Reveal key={p.name} delay={80}>
              <div className="h-full rounded-2xl border border-border bg-background px-6 py-6 flex flex-col items-center justify-center gap-3 text-center hover:border-primary/40 transition">
                <div className="text-sm font-semibold text-foreground">{p.name}</div>
                <div className="text-xs text-muted-foreground">{p.detail}</div>
              </div>
            </Reveal>
          ))}
        </div>

        {/* Partner inquiry form */}
        <div id="partner-inquiry" className="mt-20 grid lg:grid-cols-5 gap-8 items-start">
          <Reveal variant="left" className="lg:col-span-2">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 text-primary px-3 py-1 text-xs font-semibold uppercase tracking-widest">
              <Handshake size={14} /> Partner with us
            </div>
            <h3 className="mt-5 text-3xl md:text-4xl font-bold tracking-tight text-foreground">
              Let's build the AMR response of the next decade — together.
            </h3>
            <p className="mt-4 text-muted-foreground leading-relaxed">
              We work with hospitals, sequencing providers, public-health agencies and academic
              groups. Tell us about your work and we'll respond within 2 business days.
            </p>
            <ul className="mt-6 space-y-2 text-sm text-muted-foreground">
              <li>· Access to our validation pipeline</li>
              <li>· Co-authored clinical studies</li>
              <li>· Custom AMR reports for your isolates</li>
              <li>· Deployment support in low-resource labs</li>
            </ul>
          </Reveal>

          <Reveal variant="right" delay={120} className="lg:col-span-3">
            <form
              onSubmit={handleSubmit}
              className="rounded-2xl border border-border bg-background p-6 md:p-8 shadow-soft space-y-4"
            >
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-muted-foreground">Full name</label>
                  <input
                    required
                    maxLength={100}
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-border bg-card px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground">Work email</label>
                  <input
                    type="email"
                    required
                    maxLength={255}
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-border bg-card px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground">
                    Organization
                  </label>
                  <input
                    maxLength={150}
                    value={form.organization}
                    onChange={(e) => setForm({ ...form, organization: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-border bg-card px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground">Role</label>
                  <input
                    maxLength={100}
                    value={form.role}
                    onChange={(e) => setForm({ ...form, role: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-border bg-card px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground">
                  Type of partnership
                </label>
                <select
                  value={form.type}
                  onChange={(e) => setForm({ ...form, type: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-border bg-card px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                >
                  {partnershipTypes.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground">
                  Tell us about your project
                </label>
                <textarea
                  rows={4}
                  maxLength={1000}
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-border bg-card px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
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
                    <CheckCircle2 size={16} /> Inquiry received
                  </>
                )}
                {(status === "idle" || status === "error") && (
                  <>
                    Submit partnership inquiry <ArrowRight size={16} />
                  </>
                )}
              </button>

              <p className="text-[11px] text-muted-foreground text-center">
                Your details stay private. We reply within 2 business days.
              </p>
            </form>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
