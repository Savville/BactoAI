import { Link } from "@tanstack/react-router";
import logoAsset from "@/assets/bactoai-logo-wordmark.png.asset.json";
import { Newsletter } from "./Newsletter";
import { Linkedin, Mail, MapPin, ArrowUpRight } from "lucide-react";

const productLinks = [
  { label: "Technology", href: "/technology#technology" },
  { label: "Platform capabilities", href: "/technology#product" },
  { label: "Validation", href: "/#validation" },
  { label: "Roadmap", href: "/about#roadmap" },
  { label: "FAQ", href: "/technology#faq" },
];

const companyLinks: { label: string; href: string; route?: boolean }[] = [
  { label: "The problem", href: "/#problem" },
  { label: "Our team", href: "/about#team" },
  { label: "Research & awards", href: "/research#research" },
  { label: "Partners", href: "/about#partners" },
  { label: "Careers", href: "/careers", route: true },
  { label: "Resources", href: "/resources", route: true },
];

const actionLinks: { label: string; href: string; external?: boolean }[] = [
  { label: "Request a demo", href: "/contact" },
  { label: "Partner with us", href: "/about#partner-inquiry" },
  {
    label: "LinkedIn",
    href: "https://www.linkedin.com/in/bactoai-model-32303335a",
    external: true,
  },
  { label: "Email us", href: "mailto:info@bactoai.co.ke" },
];

const legalLinks: { label: string; href: string; route?: boolean }[] = [
  { label: "Privacy Policy", href: "/privacy", route: true },
  { label: "Terms of Service", href: "/terms", route: true },
];

export function Footer() {
  return (
    <footer className="bg-dark text-white/80">
      <div className="mx-auto max-w-7xl px-6 pt-4">
        <Newsletter />
      </div>
      <div className="mx-auto max-w-7xl px-6 py-16 grid gap-12 md:grid-cols-4">
        <div className="md:col-span-1">
          <img
            src={logoAsset.url}
            alt="BactoAI — Resistance. Predicted."
            className="h-20 md:h-24 w-auto rounded-xl"
          />
          <p className="mt-4 text-sm leading-relaxed text-white/60">
            AI-powered antimicrobial resistance prediction from bacterial genomes.
          </p>
          <ul className="mt-6 space-y-2 text-sm text-white/70">
            <li className="flex items-center gap-2">
              <Mail size={14} className="text-primary-glow" />
              <a href="mailto:info@bactoai.co.ke" className="hover:text-white transition">
                info@bactoai.co.ke
              </a>
            </li>
            <li className="flex items-center gap-2">
              <Linkedin size={14} className="text-primary-glow" />
              <a
                href="https://www.linkedin.com/in/bactoai-model-32303335a"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-white transition"
              >
                LinkedIn
              </a>
            </li>
            <li className="flex items-start gap-2">
              <MapPin size={14} className="text-primary-glow mt-0.5" />
              <span>Nairobi, Kenya</span>
            </li>
          </ul>
        </div>
        <div>
          <div className="text-sm font-semibold text-white mb-4">Product</div>
          <ul className="space-y-2 text-sm text-white/60">
            {productLinks.map((l) => (
              <li key={l.href}>
                <a href={l.href} className="hover:text-white transition">
                  {l.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <div className="text-sm font-semibold text-white mb-4">Company</div>
          <ul className="space-y-2 text-sm text-white/60">
            {companyLinks.map((l) => (
              <li key={l.href}>
                {l.route ? (
                  <Link to={l.href} className="hover:text-white transition">
                    {l.label}
                  </Link>
                ) : (
                  <a href={l.href} className="hover:text-white transition">
                    {l.label}
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <div className="text-sm font-semibold text-white mb-4">Get involved</div>
          <ul className="space-y-2 text-sm text-white/60">
            {actionLinks.map((l) => (
              <li key={l.href}>
                <a
                  href={l.href}
                  target={l.external ? "_blank" : undefined}
                  rel={l.external ? "noopener noreferrer" : undefined}
                  className="inline-flex items-center gap-1 hover:text-white transition"
                >
                  {l.label}
                  {l.external && <ArrowUpRight size={12} />}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="border-t border-white/10">
        <div className="mx-auto max-w-7xl px-6 py-6 flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-white/50">
          <div>© {new Date().getFullYear()} BactoAI. All rights reserved.</div>
          <div className="flex flex-wrap justify-center items-center gap-5">
            {legalLinks.map((l) => (
              <Link key={l.href} to={l.href} className="hover:text-white transition">
                {l.label}
              </Link>
            ))}
            <span className="hidden md:inline text-white/30">·</span>
            <span>Nairobi, Kenya</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
