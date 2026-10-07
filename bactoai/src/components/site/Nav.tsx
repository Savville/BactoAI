import { Link } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { Menu, X, ChevronDown } from "lucide-react";
import logoAsset from "@/assets/bactoai-logo-wordmark.png.asset.json";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "./ThemeToggle";

type NavLink = { href: string; label: string; route?: boolean };

const primaryLinks: NavLink[] = [
  { href: "/", label: "Home", route: true },
  { href: "/#demo", label: "Model", route: false },
  { href: "/pricing", label: "Product & Pricing", route: true },
  { href: "/about", label: "About", route: true },
];

const moreLinks: NavLink[] = [
  { href: "/technology", label: "Technology", route: true },
  { href: "/research", label: "Research", route: true },
  { href: "/resources", label: "Resources", route: true },
  { href: "/blog", label: "Blog", route: true },
  { href: "/press", label: "Press & media", route: true },
  { href: "/careers", label: "Careers", route: true },
];

export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const moreRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (moreRef.current && !moreRef.current.contains(e.target as Node)) setMoreOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled ? "glass shadow-soft" : "bg-transparent"
        }`}
      >
        <div className="mx-auto grid grid-cols-[minmax(0,1fr)_auto] lg:flex max-w-7xl items-center justify-between gap-3 px-4 sm:px-6 py-3">
          <Link to="/" className="flex min-w-0 items-center gap-2">
            <img
              src={logoAsset.url}
              alt="BactoAI logo — AI-powered antimicrobial resistance prediction"
              className="h-14 md:h-16 w-auto max-w-full object-contain rounded-xl"
            />
          </Link>
          <nav className="hidden lg:flex items-center gap-7">
            {primaryLinks.map((l) =>
              l.route !== false ? (
                <Link
                  key={l.href}
                  to={l.href}
                  className="text-sm font-medium text-foreground/70 hover:text-primary transition-colors"
                  activeProps={{ className: "text-sm font-medium text-primary" }}
                >
                  {l.label}
                </Link>
              ) : (
                <a
                  key={l.href}
                  href={l.href}
                  className="text-sm font-medium text-foreground/70 hover:text-primary transition-colors"
                >
                  {l.label}
                </a>
              )
            )}
            <div className="relative" ref={moreRef}>
              <button
                onClick={() => setMoreOpen((v) => !v)}
                aria-expanded={moreOpen}
                className="inline-flex items-center gap-1 text-sm font-medium text-foreground/70 hover:text-primary transition-colors"
              >
                More <ChevronDown size={14} />
              </button>
              {moreOpen && (
                <div className="absolute right-0 mt-3 w-56 rounded-2xl border border-border bg-card p-2 shadow-elegant">
                  {moreLinks.map((l) =>
                    l.route !== false ? (
                      <Link
                        key={l.href}
                        to={l.href}
                        onClick={() => setMoreOpen(false)}
                        className="block rounded-xl px-3 py-2 text-sm font-medium text-foreground/80 hover:bg-muted hover:text-primary transition-colors"
                      >
                        {l.label}
                      </Link>
                    ) : (
                      <a
                        key={l.href}
                        href={l.href}
                        onClick={() => setMoreOpen(false)}
                        className="block rounded-xl px-3 py-2 text-sm font-medium text-foreground/80 hover:bg-muted hover:text-primary transition-colors"
                      >
                        {l.label}
                      </a>
                    )
                  )}
                </div>
              )}
            </div>
          </nav>
          <div className="hidden lg:flex items-center gap-3">
            <ThemeToggle />
            <Link
              to="/contact"
              className="rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-soft hover:shadow-elegant transition-shadow"
            >
              Request a Demo
            </Link>
          </div>
          <div className="lg:hidden flex items-center gap-2">
            <ThemeToggle />
            <button
              className="text-foreground p-2"
              onClick={() => setOpen((v) => !v)}
              aria-label="Menu"
            >
              {open ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>
        {open && (
          <div className="lg:hidden max-h-[calc(100dvh-90px)] overflow-y-auto glass border-t border-border px-6 py-4 space-y-3">
            {[...primaryLinks, ...moreLinks].map((l) =>
              l.route !== false ? (
                <Link
                  key={l.href}
                  to={l.href}
                  className="block text-base font-medium text-foreground/80"
                  onClick={() => setOpen(false)}
                >
                  {l.label}
                </Link>
              ) : (
                <a
                  key={l.href}
                  href={l.href}
                  className="block text-base font-medium text-foreground/80"
                  onClick={() => setOpen(false)}
                >
                  {l.label}
                </a>
              )
            )}
            <Link
              to="/contact"
              onClick={() => setOpen(false)}
              className="block text-center rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground"
            >
              Request a Demo
            </Link>
          </div>
        )}
      </header>
      <div className="mobile-pilot-bar fixed inset-x-0 bottom-0 z-50 border-t border-border bg-background p-3 md:hidden">
        <Button asChild className="w-full min-h-12">
          <Link to="/contact">Request a Pilot</Link>
        </Button>
      </div>
    </>
  );
}
