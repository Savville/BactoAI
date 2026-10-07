import { defineTool } from "@lovable.dev/mcp-js";
import { z } from "zod";
import { supabaseForUser } from "../supabase";

export default defineTool({
  name: "list_contact_submissions",
  title: "List contact submissions",
  description:
    "List BactoAI website submissions (demo requests, partner inquiries, newsletter signups). Requires an admin account; non-admins see no rows.",
  inputSchema: {
    form_type: z
      .enum(["demo", "partner", "newsletter", "contact"])
      .optional()
      .describe("Filter by submission type."),
    limit: z.number().int().optional().describe("Max rows to return (default 25, max 100)."),
  },
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
  handler: async ({ form_type, limit }, ctx) => {
    if (!ctx.isAuthenticated())
      return { content: [{ type: "text", text: "Not authenticated" }], isError: true };
    const supabase = supabaseForUser(ctx);
    const take = Math.min(Math.max(limit ?? 25, 1), 100);
    let query = supabase
      .from("contact_submissions")
      .select("id, form_type, full_name, email, organization, message, metadata, created_at")
      .order("created_at", { ascending: false })
      .limit(take);
    if (form_type) query = query.eq("form_type", form_type);
    const { data, error } = await query;
    if (error) return { content: [{ type: "text", text: error.message }], isError: true };
    const { recordAuditEvent } = await import("@/lib/audit.server");
    await recordAuditEvent({
      actorId: ctx.getUserId() ?? null,
      action: "contact_submissions_viewed_mcp",
      targetTable: "contact_submissions",
      details: { source: "mcp", form_type: form_type ?? null, rows_returned: data?.length ?? 0 },
    });
    if (!data?.length)
      return {
        content: [
          {
            type: "text",
            text: "No submissions visible. If you expected rows, your account may not have the admin role.",
          },
        ],
        structuredContent: { count: 0, submissions: [] },
      };
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
      structuredContent: { count: data.length, submissions: data },
    };
  },
});
