// Server-only audit trail writer. Uses the service role so audit rows cannot be
// tampered with or blocked by the caller's own RLS permissions.
export type AuditEntry = {
  actorId: string | null;
  actorEmail?: string | null;
  action: string;
  targetTable?: string | null;
  targetId?: string | null;
  details?: Record<string, unknown> | null;
};

export async function recordAuditEvent(entry: AuditEntry): Promise<void> {
  try {
    const { supabaseAdmin } = await import("@/integrations/supabase/client.server");
    const { error } = await supabaseAdmin.from("admin_audit_log").insert({
      actor_id: entry.actorId,
      actor_email: entry.actorEmail ?? null,
      action: entry.action,
      target_table: entry.targetTable ?? null,
      target_id: entry.targetId ?? null,
      details: (entry.details ?? null) as never,
    });
    if (error) console.error("audit log insert failed", error.message);
  } catch (err) {
    // Auditing must never break the request it is observing.
    console.error("audit log insert threw", err);
  }
}
