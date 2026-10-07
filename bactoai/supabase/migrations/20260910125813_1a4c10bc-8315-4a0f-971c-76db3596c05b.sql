alter table public.contact_submissions drop constraint if exists contact_submissions_form_type_check;
alter table public.contact_submissions add constraint contact_submissions_form_type_check
  check (form_type = any (array['demo'::text,'partner'::text,'general'::text,'newsletter'::text]));