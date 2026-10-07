import { useEffect } from "react";

/**
 * Auto-reveal: finds each <section> under <main> and applies a
 * fade-up animation to its top-level content blocks when they scroll
 * into view. This lets us add scroll motion across the entire page
 * without touching every section component.
 */
export function useAutoReveal() {
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (typeof IntersectionObserver === "undefined") return;

    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const sections = document.querySelectorAll<HTMLElement>("main section");
    const targets: HTMLElement[] = [];

    sections.forEach((section) => {
      // Find the primary content container inside each section
      const inner = section.querySelector<HTMLElement>(":scope > div") ?? section;
      const children = Array.from(inner.children) as HTMLElement[];
      const nodes = children.length ? children : [inner];
      nodes.forEach((child, idx) => {
        if (child.dataset.revealApplied === "true") return;
        child.dataset.revealApplied = "true";
        child.classList.add("reveal");
        child.style.transitionDelay = `${Math.min(idx * 80, 320)}ms`;
        targets.push(child);
      });
    });

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            io.unobserve(entry.target);
          }
        });
      },
      // Tall phone workflows can exceed the viewport; reveal as soon as any part enters.
      { threshold: 0, rootMargin: "0px 0px -30px 0px" },
    );

    targets.forEach((t) => io.observe(t));
    return () => {
      io.disconnect();
      targets.forEach((target) => {
        target.classList.remove("reveal", "in-view");
        delete target.dataset.revealApplied;
        target.style.transitionDelay = "";
      });
    };
  }, []);
}
