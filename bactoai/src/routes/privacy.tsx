import { createFileRoute } from "@tanstack/react-router";
import { LegalLayout } from "@/components/site/LegalLayout";

export const Route = createFileRoute("/privacy")({
  head: () => ({
    meta: [
      { title: "Privacy Policy — BactoAI" },
      {
        name: "description",
        content:
          "How BactoAI collects, stores, and protects information provided through our website and platform.",
      },
      { property: "og:title", content: "Privacy Policy — BactoAI" },
      {
        property: "og:description",
        content:
          "How BactoAI collects, stores, and protects information provided through our website and platform.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/privacy" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/privacy" }],
  }),
  component: PrivacyPage,
});

function PrivacyPage() {
  return (
    <LegalLayout title="Privacy Policy" updated="July 2026">
      <p>
        BactoAI ("we", "us", "our") is an early-stage research and technology group building
        AI-driven diagnostics for antimicrobial resistance (AMR). This policy explains what
        information we collect through <a href="https://bactoai.co.ke">our website</a> and, when
        applicable, our platform — and how we handle it.
      </p>

      <h2>Data protection</h2>
      <p>
        BactoAI is designed to comply with the Kenya Data Protection Act, 2019. We do not accept
        identifiable patient data in the demo. Pilot data handling is governed by a data-processing
        agreement agreed with each partner.
      </p>

      <h2>1. Information we collect</h2>
      <h3>Contact and inquiry data</h3>
      <p>
        When you submit our demo, partner, or contact forms we collect the fields you provide —
        typically your name, work email, organization, role, and the content of your message. We use
        this only to respond to your inquiry and, with your consent, to keep you informed about
        BactoAI updates.
      </p>
      <h3>Genomic and clinical data (platform users)</h3>
      <p>
        Our AMR prediction platform is under active development and pilot testing. In production
        deployments the platform processes bacterial whole-genome sequencing (WGS) data provided by
        partner laboratories. We treat this data as sensitive and do not use it for advertising,
        resale, or any purpose outside the analysis you requested.
      </p>
      <h3>Basic web analytics</h3>
      <p>
        We may collect standard, aggregated technical information (page views, referrer, device
        type) to improve the site. We do not sell this information.
      </p>

      <h2>2. How data is stored and secured</h2>
      <ul>
        <li>Form submissions are stored in an access-controlled managed database.</li>
        <li>
          Transport between your browser and our servers uses TLS/HTTPS. Data at rest in the managed
          cloud is encrypted by the underlying infrastructure provider.
        </li>
        <li>
          For genomic and clinical data we support <strong>on-premises deployment</strong> so
          patient data can remain inside your institution's network and never leaves your control.
        </li>
        <li>
          Access to internal systems is restricted to authorized BactoAI team members on a
          need-to-know basis.
        </li>
      </ul>
      <p className="text-sm text-muted-foreground">
        No system is perfectly secure. We describe our current controls honestly and continue to
        strengthen them as the product matures.
      </p>

      <h2>3. Data retention</h2>
      <ul>
        <li>
          Inquiry submissions are retained for as long as needed to respond and keep a record of our
          correspondence, and are removed on request.
        </li>
        <li>
          Platform data retention for pilots and deployments is defined per data-sharing agreement
          with the partner institution.
        </li>
      </ul>

      <h2>4. Sharing</h2>
      <p>
        We do not sell personal information. We share information only with (a) service providers
        strictly necessary to operate the site and platform, and (b) research collaborators
        specifically named in a signed agreement.
      </p>

      <h2>5. Your choices</h2>
      <p>
        You may request access to, correction of, or deletion of information you have provided to us
        by emailing <a href="mailto:info@bactoai.co.ke">info@bactoai.co.ke</a>.
      </p>

      <h2>6. Contact</h2>
      <p>
        Questions about this policy or our data practices:{" "}
        <a href="mailto:info@bactoai.co.ke">info@bactoai.co.ke</a> — BactoAI, Nairobi, Kenya.
      </p>
    </LegalLayout>
  );
}
