import { useEffect, useRef, useState } from "react";
import { Clock, Skull, Globe2, Quote } from "lucide-react";

function useCountUp(target: number, duration = 1800, decimals = 0) {
  const [val, setVal] = useState(0);
  const ref = useRef<HTMLSpanElement | null>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            const start = performance.now();
            const step = (t: number) => {
              const p = Math.min(1, (t - start) / duration);
              const eased = 1 - Math.pow(1 - p, 3);
              setVal(target * eased);
              if (p < 1) requestAnimationFrame(step);
            };
            requestAnimationFrame(step);
            io.disconnect();
          }
        });
      },
      { threshold: 0.5 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [target, duration]);
  return { ref, val: val.toFixed(decimals) };
}

function BigCount() {
  const { ref, val } = useCountUp(1.27, 2200, 2);
  return (
    <div className="text-center">
      <span
        ref={ref}
        className="font-stat font-bold text-6xl sm:text-8xl lg:text-9xl leading-none text-hero-gradient"
      >
        {val}M+
      </span>
      <div className="mt-4 text-sm md:text-base uppercase tracking-[0.25em] text-white/60">
        Deaths from antimicrobial resistance every year
      </div>
    </div>
  );
}

const cards = [
  { icon: Clock, k: "48–72h", label: "Traditional lab turnaround", tone: "text-resistant" },
  {
    icon: Skull,
    k: "10M",
    label: "Projected annual AMR deaths by 2050",
    tone: "text-resistant/80",
  },
  {
    icon: Globe2,
    k: "$100T",
    label: "Cumulative global economic cost by 2050",
    tone: "text-accent",
  },
];

export function Stakes() {
  return (
    <section id="stakes" className="relative bg-ink text-white py-24 md:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-ink-mesh opacity-90" />
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[520px] h-[520px] rounded-full bg-[color:var(--color-teal-glow)]/10 blur-3xl" />
        <div className="absolute -bottom-32 -right-32 w-[520px] h-[520px] rounded-full bg-accent/10 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-6xl px-6">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-widest text-white/70">
            The Stakes
          </div>
          <h2 className="mt-6 text-3xl md:text-5xl font-bold tracking-tight text-white max-w-3xl mx-auto">
            A silent pandemic is outpacing the drugs we have to fight it.
          </h2>
        </div>

        <div className="mt-16">
          <BigCount />
        </div>

        <div className="mt-16 grid md:grid-cols-3 gap-4">
          {cards.map((c) => (
            <div key={c.k} className="glass-dark rounded-2xl p-6">
              <c.icon className={c.tone} size={22} />
              <div className={`mt-4 font-stat text-4xl font-bold ${c.tone}`}>{c.k}</div>
              <div className="mt-2 text-sm text-white/70">{c.label}</div>
            </div>
          ))}
        </div>

        <div className="mt-16 grid md:grid-cols-[1fr_auto_1fr] items-center gap-8 max-w-4xl mx-auto">
          <div className="glass-dark rounded-2xl p-6 text-center">
            <div className="text-xs uppercase tracking-widest text-white/50">Today</div>
            <div className="mt-2 font-stat text-5xl font-bold text-resistant">48–72h</div>
            <div className="mt-2 text-sm text-white/60">Culture + susceptibility testing</div>
          </div>
          <div className="text-4xl text-white/40 text-center">→</div>
          <div className="glass-dark rounded-2xl p-6 text-center border-[color:var(--color-teal-glow)]/40 shadow-glow-teal">
            <div className="text-xs uppercase tracking-widest text-white/50">With BactoAI</div>
            <div className="mt-2 font-stat text-5xl font-bold text-hero-gradient">&lt;10</div>
            <div className="mt-2 text-sm text-white/70">under 10 minutes from genome to result</div>
          </div>
        </div>

        <figure className="mt-20 max-w-3xl mx-auto text-center">
          <Quote className="mx-auto text-[color:var(--color-teal-glow)]/60" size={28} />
          <blockquote className="mt-4 text-xl md:text-2xl font-display italic text-white/85 leading-snug">
            "Antimicrobial resistance is one of the top ten global public health threats facing
            humanity."
          </blockquote>
          <figcaption className="mt-4 text-xs uppercase tracking-widest text-white/50">
            — World Health Organization
          </figcaption>
        </figure>

        <div className="mt-14 text-center">
          <a
            href="#solution"
            className="inline-flex items-center gap-2 rounded-full bg-[color:var(--color-teal-glow)] px-7 py-3.5 text-sm font-semibold text-[color:var(--color-ink)] shadow-glow-teal hover:brightness-110 transition"
          >
            See how BactoAI changes this →
          </a>
        </div>
      </div>
    </section>
  );
}
