import { auth, defineMcp } from "@lovable.dev/mcp-js";
import listContactSubmissions from "./tools/list-contact-submissions";
import submissionStats from "./tools/submission-stats";
import listArticles from "./tools/list-articles";

// Issuer must be the direct Supabase host (the publish-time proxy URL fails RFC 8414 issuer matching).
const projectRef = import.meta.env["VITE_SUPABASE_PROJECT_ID"] ?? "project-ref-unset";

export default defineMcp({
  name: "bactoai-website-builder",
  title: "BactoAI Website Builder",
  version: "0.1.0",
  instructions:
    "Tools for the BactoAI site. Use `list_contact_submissions` and `submission_stats` to review demo requests, partner inquiries and newsletter signups (admin accounts only), and `list_articles` to browse published BactoAI articles.",
  auth: auth.oauth.issuer({
    issuer: `https://${projectRef}.supabase.co/auth/v1`,
    acceptedAudiences: "authenticated",
  }),
  tools: [listContactSubmissions, submissionStats, listArticles],
});
