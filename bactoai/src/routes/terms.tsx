import { createFileRoute } from "@tanstack/react-router";
import { LegalLayout } from "@/components/site/LegalLayout";

export const Route = createFileRoute("/terms")({
  head: () => ({
    meta: [
      { title: "Terms of Service — BactoAI" },
      {
        name: "description",
        content:
          "Terms governing use of the BactoAI website and platform, including acceptable use and decision-support limitations.",
      },
      { property: "og:title", content: "Terms of Service — BactoAI" },
      {
        property: "og:description",
        content: "Terms governing use of the BactoAI website and genomic AMR prediction platform.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:url", content: "https://bactoai.co.ke/terms" },
    ],
    links: [{ rel: "canonical", href: "https://bactoai.co.ke/terms" }],
  }),
  component: TermsPage,
});

function TermsPage() {
  return (
    <LegalLayout title="Terms of Service" updated="July 2026">
      <p>
        These terms govern your use of the BactoAI website and, where applicable, our AMR prediction
        platform ("Services"). By using the Services you agree to these terms.
      </p>

      <h2>1. Acceptable use</h2>
      <ul>
        <li>Do not use the Services to violate any applicable law or third-party right.</li>
        <li>Do not upload data you are not authorized to share.</li>
        <li>
          Do not attempt to reverse engineer, disrupt, or gain unauthorized access to the Services.
        </li>
      </ul>

      <h2>2. Decision-support only — not a substitute for laboratory confirmation</h2>
      <p>
        BactoAI's AMR predictions are intended as <strong>clinical decision support</strong> for
        qualified microbiologists, clinicians, and researchers. They are not a diagnosis and{" "}
        <strong>do not replace</strong> phenotypic antimicrobial susceptibility testing or the
        professional judgement of a licensed healthcare provider. Treatment decisions remain the
        responsibility of the treating clinician.
      </p>

      <h2>3. Research / early access status</h2>
      <p>
        The platform is provided for research, evaluation, and pilot use unless we have signed a
        separate clinical-use agreement with your institution. Results may be inaccurate,
        incomplete, or unavailable at any time.
      </p>

      <h2>4. Intellectual property</h2>
      <p>
        BactoAI, its models, code, documentation, branding, and website content are the property of
        BactoAI and its contributors. You retain ownership of data you provide; you grant us a
        limited licence to process it solely to deliver the Services you requested and, where agreed
        in writing, to support model improvement in de-identified form.
      </p>

      <h2>5. Warranty disclaimer</h2>
      <p>
        The Services are provided "as is" without warranties of any kind, express or implied,
        including merchantability, fitness for a particular purpose, and non-infringement.
      </p>

      <h2>6. Limitation of liability</h2>
      <p>
        To the maximum extent permitted by law, BactoAI and its team will not be liable for any
        indirect, incidental, special, consequential, or punitive damages, or any loss of profits or
        revenues, arising out of or related to your use of the Services.
      </p>

      <h2>7. Changes</h2>
      <p>
        We may update these terms as the product evolves. Material changes will be reflected by an
        updated date at the top of this page.
      </p>

      <h2>8. Contact</h2>
      <p>
        Questions: <a href="mailto:info@bactoai.co.ke">info@bactoai.co.ke</a>.
      </p>
    </LegalLayout>
  );
}
