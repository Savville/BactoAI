import { useMemo, useState } from "react";
import { MapPin, Search, Clock, FlaskConical, ArrowRight } from "lucide-react";

type Lab = {
  name: string;
  location: string;
  city: string;
  turnaround: string;
  services: string[];
};

const labs: Lab[] = [
  {
    name: "Kenyatta National Hospital — Microbiology Lab",
    location: "Upper Hill, Nairobi",
    city: "Nairobi",
    turnaround: "48–72 hrs",
    services: ["Culture & sensitivity", "Blood cultures"],
  },
  {
    name: "KEMRI Centre for Microbiology Research",
    location: "Mbagathi Road, Nairobi",
    city: "Nairobi",
    turnaround: "72 hrs",
    services: ["Reference testing", "WGS sequencing"],
  },
  {
    name: "Aga Khan University Hospital Laboratory",
    location: "Parklands, Nairobi",
    city: "Nairobi",
    turnaround: "24–48 hrs",
    services: ["Culture & sensitivity", "MIC panels"],
  },
  {
    name: "Kenyatta University Teaching & Referral Hospital",
    location: "Kahawa, Nairobi",
    city: "Nairobi",
    turnaround: "48 hrs",
    services: ["Culture & sensitivity", "Research collaboration"],
  },
  {
    name: "Moi Teaching & Referral Hospital Lab",
    location: "Nandi Road, Eldoret",
    city: "Eldoret",
    turnaround: "72 hrs",
    services: ["Culture & sensitivity", "AMR surveillance"],
  },
  {
    name: "Coast General Teaching & Referral Hospital",
    location: "Kisauni Road, Mombasa",
    city: "Mombasa",
    turnaround: "72 hrs",
    services: ["Culture & sensitivity"],
  },
];

export function PartnerLabs() {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return labs;
    return labs.filter((l) =>
      [l.name, l.location, l.city, ...l.services].join(" ").toLowerCase().includes(q),
    );
  }, [query]);

  return (
    <section id="labs" className="py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">
            Clinical validation
          </div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Target clinical sites for validation
          </h2>
          <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
            Sites listed are intended validation settings, not confirmed partners.
          </p>
        </div>

        <div className="mt-8 flex flex-col sm:flex-row items-stretch sm:items-center gap-3 max-w-xl">
          <div className="relative flex-1">
            <Search
              size={16}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Search target clinical sites by city or service"
              placeholder="Search by city, hospital or service (e.g. Nairobi)"
              className="w-full rounded-full border border-border bg-card pl-11 pr-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>
          <span className="text-xs text-muted-foreground sm:whitespace-nowrap">
            {filtered.length} lab{filtered.length === 1 ? "" : "s"} listed
          </span>
        </div>

        <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((lab) => (
            <div
              key={lab.name}
              className="rounded-3xl border border-border bg-card p-6 shadow-soft hover:shadow-elegant transition-shadow flex flex-col"
            >
              <div className="flex items-center justify-center w-11 h-11 rounded-2xl bg-primary/10 text-primary">
                <FlaskConical size={20} />
              </div>
              <h3 className="mt-5 text-lg font-bold text-foreground leading-snug">{lab.name}</h3>
              <div className="mt-3 flex items-start gap-2 text-sm text-muted-foreground">
                <MapPin size={15} className="mt-0.5 text-primary shrink-0" />
                {lab.location}
              </div>
              <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                <Clock size={15} className="text-primary shrink-0" />
                Typical turnaround today: {lab.turnaround}
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {lab.services.map((s) => (
                  <span
                    key={s}
                    className="rounded-full border border-border px-3 py-1 text-[11px] font-medium text-muted-foreground"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="md:col-span-2 lg:col-span-3 rounded-3xl border border-dashed border-border p-10 text-center text-sm text-muted-foreground">
              No target clinical sites match that search —{" "}
              <a href="/contact" className="text-primary font-semibold hover:underline">
                tell us where you need coverage
              </a>
              .
            </div>
          )}
        </div>

        <div className="mt-10 rounded-3xl border border-border bg-card/60 p-6 md:p-8 flex flex-col md:flex-row md:items-center gap-6">
          <p className="text-sm text-muted-foreground leading-relaxed flex-1">
            <span className="font-semibold text-foreground">Complementary, not a replacement.</span>{" "}
            BactoAI aims for under 10 minutes from genome to result. Conventional laboratory testing
            and professional clinical judgment remain essential. Contact us to discuss a supervised
            validation pilot.
          </p>
          <a
            href="/contact"
            className="inline-flex items-center justify-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-soft hover:shadow-elegant transition-shadow shrink-0"
          >
            Request a Pilot <ArrowRight size={16} />
          </a>
        </div>
      </div>
    </section>
  );
}
