DROP POLICY IF EXISTS "Anyone can submit a contact form" ON public.contact_submissions;

CREATE POLICY "Anyone can submit a contact form"
ON public.contact_submissions
FOR INSERT
TO anon, authenticated
WITH CHECK (
  form_type IN ('demo', 'partner', 'newsletter', 'contact')
  AND char_length(full_name) BETWEEN 1 AND 100
  AND char_length(email) BETWEEN 3 AND 255
  AND email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'
  AND (organization IS NULL OR char_length(organization) <= 150)
  AND (message IS NULL OR char_length(message) <= 1000)
);