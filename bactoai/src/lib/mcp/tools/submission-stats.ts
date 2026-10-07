import { defineTool } from "@lovable.dev/mcp-js";
import { supabaseForUser } from "../supabase";

export default defineTool({
  name: "submission_stats",
  title: "Submission stats",
  description:
    "Summarize BactoAI website submissions by form type, with the most recent submission date. Requires an admin account.",
  inputSchema: {},
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
  handler: async (_input, ctx) => {
    if (!ctx.isAuthenticated())
      return { content: [{ type: "text", text: "Not authenticated" }], isError: true };
    const supabase = supabaseForUser(ctx);
    const { data, error } = await supabase
      .from("contact_submissions")
      .select("form_type, created_at")
      .order("created_at", { ascending: false })
      .limit(1000);
    if (error) return { content: [{ type: "text", text: error.message }], isError: true };
    const rows = data ?? [];
    const byType: Record<string, number> = {};
    for (const row of rows) {
      const key = String(row.form_type ?? "unknown");
      byType[key] = (byType[key] ?? 0) + 1;
    }
    const stats = {
      total: rows.length,
      by_form_type: byType,
      latest: rows[0]?.created_at ?? null,
    };
    const { recordAuditEvent } = await import("@/lib/audit.server");
    await recordAuditEvent({
      actorId: ctx.getUserId() ?? null,
      action: "submission_stats_viewed_mcp",
      targetTable: "contact_submissions",
      details: { source: "mcp", rows_scanned: rows.length },
    });
    return {
      content: [{ type: "text", text: JSON.stringify(stats, null, 2) }],
      structuredContent: stats,
    };
  },
});
