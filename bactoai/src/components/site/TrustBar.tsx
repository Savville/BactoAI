export function TrustBar() {
  const items = [
    { label: "Grant", name: "CDIE Catalyst" },
    { label: "Program", name: "East Africa Biodesign" },
    { label: "First project pitch", name: "GEES Bootcamp" },
  ];
  return (
    <section className="border-y border-border bg-card/60 backdrop-blur">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="text-center text-xs uppercase tracking-[0.2em] text-muted-foreground mb-6">
          Research and entrepreneurship journey
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {items.map((it) => (
            <div key={it.name} className="text-center">
              <div className="text-[10px] uppercase tracking-widest text-muted-foreground/70">
                {it.label}
              </div>
              <div className="mt-1 text-sm md:text-base font-semibold text-foreground">
                {it.name}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
