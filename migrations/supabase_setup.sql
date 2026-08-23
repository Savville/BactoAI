-- ============================================================
-- BactoAI — Supabase PostgreSQL Schema
-- ============================================================
-- Run this SQL in the Supabase SQL Editor to create all
-- required tables, indexes, and constraints.
--
-- Go to: https://supabase.com/dashboard → Your Project → SQL Editor
-- Paste this entire file and click "Run"
-- ============================================================

-- ============================================================
-- Users Table
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    clinic_name TEXT DEFAULT '',
    role TEXT DEFAULT 'viewer' CHECK(role IN ('admin', 'lab_tech', 'viewer')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- API Keys Table
-- ============================================================
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash TEXT UNIQUE NOT NULL,
    key_prefix TEXT NOT NULL,
    name TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ
);

-- ============================================================
-- Submissions Table
-- ============================================================
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sample_id TEXT NOT NULL,
    filename TEXT,
    genome_size INTEGER,
    meropenem_label TEXT,
    meropenem_prob REAL,
    meropenem_confidence TEXT,
    ciprofloxacin_label TEXT,
    ciprofloxacin_prob REAL,
    ciprofloxacin_confidence TEXT,
    cefotaxime_label TEXT,
    cefotaxime_prob REAL,
    cefotaxime_confidence TEXT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

-- ============================================================
-- Feedback Table
-- ============================================================
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    antibiotic TEXT NOT NULL,
    predicted_label TEXT NOT NULL,
    actual_label TEXT NOT NULL,
    actual_value TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Audit Log Table
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Indexes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_date ON submissions(submitted_at);
CREATE INDEX IF NOT EXISTS idx_submissions_sample ON submissions(sample_id);
CREATE INDEX IF NOT EXISTS idx_feedback_submission ON feedback(submission_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ============================================================
-- Row Level Security (RLS) — Optional but recommended
-- ============================================================
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- RLS Policies — Allow all operations for now
-- (Tighten these when you go to production)
-- ============================================================
CREATE POLICY "Allow all" ON users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON api_keys FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON submissions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON feedback FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON audit_log FOR ALL USING (true) WITH CHECK (true);

-- ============================================================
-- Done! Verify tables were created:
-- ============================================================
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public' ORDER BY table_name;
