CREATE TABLE public.admin_audit_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id uuid,
  actor_email text,
  action text NOT NULL,
  target_table text,
  target_id text,
  details jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX admin_audit_log_created_at_idx ON public.admin_audit_log (created_at DESC);
CREATE INDEX admin_audit_log_actor_idx ON public.admin_audit_log (actor_id);

GRANT SELECT ON public.admin_audit_log TO authenticated;
GRANT ALL ON public.admin_audit_log TO service_role;

ALTER TABLE public.admin_audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can view the audit log"
  ON public.admin_audit_log
  FOR SELECT
  TO authenticated
  USING (private.has_role(auth.uid(), 'admin'));

-- Automatic logging of role grants/changes/revocations
CREATE OR REPLACE FUNCTION private.log_user_role_change()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO public.admin_audit_log (actor_id, action, target_table, target_id, details)
    VALUES (auth.uid(), 'role_granted', 'user_roles', NEW.id::text,
            jsonb_build_object('user_id', NEW.user_id, 'role', NEW.role));
    RETURN NEW;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO public.admin_audit_log (actor_id, action, target_table, target_id, details)
    VALUES (auth.uid(), 'role_updated', 'user_roles', NEW.id::text,
            jsonb_build_object('user_id', NEW.user_id, 'old_role', OLD.role, 'new_role', NEW.role));
    RETURN NEW;
  ELSE
    INSERT INTO public.admin_audit_log (actor_id, action, target_table, target_id, details)
    VALUES (auth.uid(), 'role_revoked', 'user_roles', OLD.id::text,
            jsonb_build_object('user_id', OLD.user_id, 'role', OLD.role));
    RETURN OLD;
  END IF;
END;
$$;

REVOKE ALL ON FUNCTION private.log_user_role_change() FROM PUBLIC, anon, authenticated;

CREATE TRIGGER user_roles_audit
AFTER INSERT OR UPDATE OR DELETE ON public.user_roles
FOR EACH ROW EXECUTE FUNCTION private.log_user_role_change();