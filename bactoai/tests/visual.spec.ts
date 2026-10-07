import { expect, test } from "@playwright/test";

const PAGES = ["/technology", "/research", "/about", "/contact"] as const;

/**
 * Visual regression baselines for the pages split out of the homepage.
 * Update intentionally-changed baselines with:
 *   bun run test:visual:update
 */
for (const path of PAGES) {
  test(`visual: ${path}`, async ({ page }) => {
    await page.goto(path, { waitUntil: "networkidle" });

    // Reveal animations are IntersectionObserver-driven and lower sections use
    // content-visibility:auto (rendered lazily) — force the final state so
    // full-page screenshots are deterministic.
    await page.addStyleTag({
      content: `*,*::before,*::after{animation:none!important;transition:none!important}
                main>section{content-visibility:visible!important;contain-intrinsic-size:none!important}
                [data-reveal],.reveal{opacity:1!important;transform:none!important}`,
    });
    await page.evaluate(() => {
      document
        .querySelectorAll("[data-reveal], .reveal")
        .forEach((el) => el.classList.add("is-visible", "revealed"));
      window.scrollTo(0, document.body.scrollHeight);
    });
    await page.waitForTimeout(600);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(300);

    await expect(page).toHaveScreenshot(`${path.slice(1)}.png`, { fullPage: true });
  });
}
