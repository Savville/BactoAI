import {
  Cpu,
  Dna,
  Cloud,
  ShieldCheck,
  FileText,
  LayoutDashboard,
  Plug,
  Server,
  FlaskConical,
  WifiOff,
  Zap,
  Brain,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI-powered prediction",
    desc: "Machine learning models trained on curated bacterial genomes.",
  },
  {
    icon: Dna,
    title: "Whole-genome ready",
    desc: "Compatible with common WGS pipelines and formats.",
  },
  { icon: Cpu, title: "Fast pipeline", desc: "From upload to prediction in minutes, not days." },
  { icon: Cloud, title: "Secure cloud", desc: "Enterprise-grade encryption and access controls." },
  {
    icon: FileText,
    title: "Clinical reports",
    desc: "Downloadable, clinician-friendly PDF reports.",
  },
  {
    icon: LayoutDashboard,
    title: "Web dashboard",
    desc: "Browser-based interface — no local setup.",
  },
  {
    icon: Plug,
    title: "API integration",
    desc: "REST endpoints to connect existing LIMS systems.",
  },
  {
    icon: Server,
    title: "Scalable",
    desc: "Handles single samples to national surveillance loads.",
  },
  {
    icon: FlaskConical,
    title: "Research-ready",
    desc: "Export raw predictions for downstream analysis.",
  },
  {
    icon: WifiOff,
    title: "Offline-capable",
    desc: "On-premises deployment for restricted networks.",
  },
  {
    icon: ShieldCheck,
    title: "Privacy first",
    desc: "Designed with HIPAA / GDPR principles in mind.",
  },
  {
    icon: Zap,
    title: "Continuously improved",
    desc: "Models retrained as new genomic data arrives.",
  },
];

export function Features() {
  return (
    <section id="product" className="py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Platform
          </div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Built for clinical labs, researchers, and public health.
          </h2>
        </div>
        <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="group rounded-2xl border border-border bg-card p-6 hover:border-primary/40 hover:-translate-y-0.5 transition-all"
            >
              <div className="flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-hero text-white shadow-soft">
                <f.icon size={20} />
              </div>
              <div className="mt-5 text-base font-semibold text-foreground">{f.title}</div>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
