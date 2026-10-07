import { defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env["PW_PORT"] ?? 8080);
const baseURL = process.env["PW_BASE_URL"] ?? `http://localhost:${PORT}`;

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env["CI"],
  retries: process.env["CI"] ? 1 : 0,
  workers: process.env["CI"] ? 2 : undefined,
  reporter: process.env["CI"] ? [["github"], ["html", { open: "never" }]] : [["list"]],
  snapshotPathTemplate: "tests/__screenshots__/{testFilePath}/{arg}-{projectName}{ext}",
  expect: {
    // Small anti-aliasing differences are tolerated; layout/copy shifts are not.
    toHaveScreenshot: { maxDiffPixelRatio: 0.01, animations: "disabled" },
  },
  use: {
    baseURL,
    viewport: { width: 1280, height: 1800 },
    colorScheme: "dark",
    trace: "retain-on-failure",
    // Escape hatch for environments that ship their own Chromium build.
    launchOptions: process.env["PW_CHROMIUM_PATH"]
      ? { executablePath: process.env["PW_CHROMIUM_PATH"] }
      : {},
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "bun run dev",
    url: baseURL,
    reuseExistingServer: true,
    timeout: 180_000,
  },
});
