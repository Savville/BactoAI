import { createServerFn } from "@tanstack/react-start";
import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";

export type ContactSubmissionRow = {
  id: string;
  form_type: string;
  full_name: string;
  email: string;
  organization: string | null;
  message: string | null;
  metadata: string | null;
  created_at: string;
};

export const listContactSubmissions = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const { data, error } = await context.supabase
      .from("contact_submissions")
      .select("id, form_type, full_name, email, organization, message, metadata, created_at")
      .order("created_at", { ascending: false })
      .limit(500);

    if (error) {
      throw new Error(error.message || "Forbidden");
    }
    const rows: ContactSubmissionRow[] = (data ?? []).map((r) => ({
      id: r.id,
      form_type: r.form_type,
      full_name: r.full_name,
      email: r.email,
      organization: r.organization,
      message: r.message,
      metadata: r.metadata == null ? null : JSON.stringify(r.metadata),
      created_at: r.created_at,
    }));

    const { recordAuditEvent } = await import("@/lib/audit.server");
    await recordAuditEvent({
      actorId: context.userId,
      actorEmail: (context.claims as { email?: string } | null)?.email ?? null,
      action: "contact_submissions_viewed",
      targetTable: "contact_submissions",
      details: { source: "admin_web", rows_returned: rows.length },
    });

    return rows;
  });

export type AuditLogRow = {
  id: string;
  actor_id: string | null;
  actor_email: string | null;
  action: string;
  target_table: string | null;
  target_id: string | null;
  details: string | null;
  created_at: string;
};

export const listAuditLog = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const { data, error } = await context.supabase
      .from("admin_audit_log")
      .select("id, actor_id, actor_email, action, target_table, target_id, details, created_at")
      .order("created_at", { ascending: false })
      .limit(300);

    if (error) throw new Error(error.message || "Forbidden");

    const rows: AuditLogRow[] = (data ?? []).map((r) => ({
      id: r.id,
      actor_id: r.actor_id,
      actor_email: r.actor_email,
      action: r.action,
      target_table: r.target_table,
      target_id: r.target_id,
      details: r.details == null ? null : JSON.stringify(r.details),
      created_at: r.created_at,
    }));
    return rows;
  });
