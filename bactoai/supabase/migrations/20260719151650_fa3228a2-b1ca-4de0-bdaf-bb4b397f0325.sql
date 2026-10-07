
CREATE TABLE public.contact_submissions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  form_type TEXT NOT NULL CHECK (form_type IN ('demo', 'partner', 'general')),
  full_name TEXT NOT NULL CHECK (char_length(full_name) BETWEEN 1 AND 200),
  email TEXT NOT NULL CHECK (char_length(email) BETWEEN 3 AND 320),
  organization TEXT CHECK (organization IS NULL OR char_length(organization) <= 200),
  message TEXT CHECK (message IS NULL OR char_length(message) <= 4000),
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

GRANT INSERT ON public.contact_submissions TO anon, authenticated;
GRANT ALL ON public.contact_submissions TO service_role;

ALTER TABLE public.contact_submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can submit a contact form"
  ON public.contact_submissions
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);
