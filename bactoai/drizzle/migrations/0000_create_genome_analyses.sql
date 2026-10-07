CREATE TABLE public.genome_analyses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  isolate_label text NOT NULL,
  organism text NOT NULL,
  specimen_source text NOT NULL,
  collection_date date,
  location text,
  clinical_notes text,
  file_name text NOT NULL,
  file_size_bytes bigint NOT NULL,
  sequence_stats jsonb NOT NULL,
  overall_risk text NOT NULL CHECK (overall_risk IN ('low','moderate','high','critical')),
  summary jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, DELETE ON public.genome_analyses TO authenticated;
GRANT ALL ON public.genome_analyses TO service_role;
ALTER TABLE public.genome_analyses ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users view own analyses" ON public.genome_analyses FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Users add own analyses" ON public.genome_analyses FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users delete own analyses" ON public.genome_analyses FOR DELETE TO authenticated USING (auth.uid() = user_id);
CREATE INDEX genome_analyses_user_created_idx ON public.genome_analyses (user_id, created_at DESC);