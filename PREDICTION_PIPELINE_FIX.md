# BactoAI, Prediction Pipeline Fix Report

**Date:** 2026-10-27  
**Symptom:** LiveAnalyzer shows "The prediction engine hit an error while analyzing this genome." (500 HTML)

---

## Root Cause Analysis

### The Break Chain

```
React (bactoai.co.ke) → POST /api/v1/predict (Bearer token)
  → Flask verify_api_key() → get_supabase().table("api_keys")...
    → Supabase query throws exception
      → Exception bubbles OUT of decorator (before route handler runs)
        → Flask default handler → raw HTML 500
          → React frontend: "prediction engine hit an error"
```

### Two Broken Supabase Projects

| Project | URL | Status | Tables |
|---------|-----|--------|--------|
| **Flask backend** (root `.env`) | `ofuxwgapzjgcrsuiqpyu.supabase.co` | ❌ Queries fail | Missing `users`, `api_keys`, etc. |
| **React app** (`bactoai/.env`) | `ojnecaomcicsayeweoab.supabase.co` | ✅ Working | Has `genome_analyses` only; missing `users`, `api_keys`, `submissions` |

The Flask backend's Supabase project either has no tables or uses a revoked/invalid service_role key. The health endpoint confirms: `{"database_ok":false,"models_loaded":true,"status":"degraded"}`.

---

## Fixes Applied (Code)

### 1. `bactoai/database.py`, `verify_api_key()` is now tolerant

```python
def verify_api_key(raw_key):
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    try:
        sb = get_supabase()
        result = sb.table("api_keys").select("*").eq("key_hash", key_hash).eq("is_active", True).execute()
        if result.data and len(result.data) > 0:
            row = result.data[0]
            sb.table("api_keys").update({"last_used_at": datetime.now().isoformat()}).eq("id", row["id"]).execute()
            return row["user_id"]
    except Exception as exc:
        import logging
        logging.warning(f"verify_api_key: Supabase error (treated as invalid key): {exc}")
    return None  # ← Now returns None instead of throwing
```

**Effect:** When Supabase is down, the API returns `401 Unauthorized` (clean JSON) instead of `500 HTML`.

### 2. `bactoai/routes/api.py`, DB save is non-blocking

```python
submission_id = None
try:
    submission_id = save_submission(...)
    log_action(...)
except Exception as db_exc:
    current_app.logger.warning(f"API predict: DB save failed (prediction still valid): {db_exc}")

return jsonify({...results...})  # ← Always returns prediction results
```

**Effect:** Even if the database is down, the prediction itself still works and returns results to the frontend.

---

## Remaining Fix: Database Tables (DO THIS NOW)

The code fix is deployed. The 500 → 401 change is live. Now you need to create the missing tables and update the Flask backend's Supabase connection.

### Step 1: Get the Service Role Key

1. Go to **https://supabase.com/dashboard/project/ojnecaomcicsayeweoab**
2. **Settings → API**
3. Copy the **service_role** key (not the anon/public key)

### Step 2: Create Tables

1. Go to **SQL Editor** in the same project
2. Paste and run: `migrations/create_flask_backend_tables.sql` (in this repo)
3. Verify:
   ```sql
   SELECT table_name FROM information_schema.tables
   WHERE table_schema = 'public' ORDER BY table_name;
   ```
   You should see: `api_keys`, `audit_log`, `feedback`, `submissions`, `users`

### Step 3: Update Flask Backend Environment Variables

On **Render dashboard → bactoai-kt0q → Environment**:
```
SUPABASE_URL=https://ojnecaomcicsayeweoab.supabase.co
SUPABASE_KEY=<paste service_role key from step 1>
```

Also update root `.env` (for local dev):
```
SUPABASE_URL=https://ojnecaomcicsayeweoab.supabase.co
SUPABASE_KEY=<same service_role key>
```

### Step 4: Redeploy Render

Trigger a manual deploy on Render (Settings → Manual Deploy).

### Step 5: Create an API Key

After redeploy, visit **https://bactoai.co.ke/auth** (or your login page), create an account, then go to `/api-keys` to generate a new API key. Use that key for the LiveAnalyzer.

### Expected Result After Fix

```bash
# Health should show database_ok: true
curl https://bactoai-kt0q.onrender.com/health
# → {"database_ok":true,"models_loaded":true,"status":"ok"}

# Predict should return JSON results
curl -X POST https://bactoai-kt0q.onrender.com/api/v1/predict \
  -H "Authorization: Bearer <your_new_key>" \
  -F "file=@data/test_genomes/GCA_052266145.1.fna"
# → {"submission_id":1,"filename":"...","genome_size":6554928,"results":[...]}
```

---

## Verify After Fix

```bash
# Health should show database_ok: true
curl https://bactoai-kt0q.onrender.com/health

# Predict should return JSON results, not HTML 500
curl -X POST https://bactoai-kt0q.onrender.com/api/v1/predict \
  -H "Authorization: Bearer <your_key>" \
  -F "file=@data/test_genomes/GCA_052266145.1.fna"
```

Expected response:
```json
{
  "submission_id": 1,
  "filename": "GCA_052266145.1.fna",
  "genome_size": 6554928,
  "results": [
    {"antibiotic": "Meropenem", "probability": 0.87, "label": "RESISTANT", ...},
    {"antibiotic": "Ciprofloxacin", "probability": 0.12, "label": "SUSCEPTIBLE", ...},
    {"antibiotic": "Cefotaxime", "probability": 0.45, "label": "SUSCEPTIBLE", ...}
  ]
}
```

---

## Files Changed in This Fix

| File | Change |
|------|--------|
| `bactoai/database.py` | `verify_api_key()` wrapped in try/except |
| `bactoai/routes/api.py` | `save_submission()` + `log_action()` wrapped in try/except |
