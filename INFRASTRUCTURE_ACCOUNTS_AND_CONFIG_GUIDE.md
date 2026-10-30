# BactoAI Infrastructure, Accounts, and Environment Reference

Date: October 27, 2026  
Status: Verified Active (`status: ok`)

This document maps all active accounts, databases, GitHub remotes, hosting services, and environment variables across the BactoAI ecosystem.

---

## 1. Supabase Databases

BactoAI uses two distinct Supabase projects. They serve different layers and do not need to be merged.

### Backend Database (ML Prediction Engine)

* **Project ID:** `ofuxwgapzjgcrsuiqpyu`
* **Project Name in Dashboard:** `bactoai`
* **Account Owner:** Personal / ML Engineering account
* **Host URL:** `https://ofuxwgapzjgcrsuiqpyu.supabase.co`
* **Purpose:** Stores backend prediction history, validation feedback, and server authentication.
* **Tables:**
  * `public.users` (legacy and admin credentials for the Flask dashboard)
  * `public.api_keys` (SHA-256 hashed keys for `/api/v1/predict`)
  * `public.submissions` (uploaded genome metadata, drug probabilities, confidence scores)
  * `public.feedback` (microbiology laboratory confirmation records)
  * `public.audit_log` (event timestamps and request IPs)
* **Auto-Pause Note:** Free-tier Supabase projects pause after 7 days of inactivity. If the Render health check ever reports `database_ok: false` or DNS fails, log into this account and click **Resume project**. Restoration takes about 2 minutes.

### Website Database (Public Web App)

* **Project ID:** `ojnecaomcicsayeweoab`
* **Account Owner:** Web Collaborator / Lovable Account
* **Host URL:** `https://ojnecaomcicsayeweoab.supabase.co`
* **Purpose:** Powers the public React application.
* **Tables:**
  * `auth.users` (Supabase Auth identities for site visitors and pilot testers)
  * `public.genome_analyses` (browser-facing analysis summaries and saved reports)
  * `public.contact_submissions` (demo requests and inbound clinic leads)

---

## 2. GitHub Repositories and Remotes

Both remotes point to the same codebase and are synchronized on the `main` branch.

| Remote Name | Repository URL | Account / Owner | Purpose |
|---|---|---|---|
| `origin` | `https://github.com/Savville/BactoAI.git` | Savville (Personal) | Primary personal workspace repository |
| `bactoai-eng` | `https://github.com/bactoai-eng/BACTOAI.git` | bactoai-eng (Organization) | Official team and collaborator upstream |

* **Current Baseline Commit:** `72ef784` ("Update Product Demo workflow and Request a Demo form")
* **Rule:** When pulling or pushing updates, ensure both remotes receive the changes to keep the team and Lovable editor synchronized.

---

## 3. Render Hosting Deployments

| Deployment URL | Owner Account | Current Status | Purpose |
|---|---|---|---|
| `https://bactoai-kt0q.onrender.com` | Official BactoAI Account | **Active / Production Healthy** | Official ML prediction API and Gunicorn service |
| `https://bactoai.onrender.com` | Personal Account | Deprecated | Old test deployment (do not send traffic here) |

### Verification Command

You can confirm production health from any terminal:

```bash
curl https://bactoai-kt0q.onrender.com/health
```

Expected output:
```json
{"database_ok": true, "models_loaded": true, "startup_error": null, "status": "ok"}
```

---

## 4. Environment File Configurations

### Root Backend Environment File: `.env`

Located at the repository root. Used by local Flask scripts and matches the Render production environment variables.

```env
SUPABASE_URL=https://ofuxwgapzjgcrsuiqpyu.supabase.co
SUPABASE_KEY=<backend_service_role_secret_key>
```

Render production dashboard variables (`bactoai-kt0q`):
* `SUPABASE_URL`: `https://ofuxwgapzjgcrsuiqpyu.supabase.co`
* `SUPABASE_KEY`: `<backend_service_role_secret_key>`
* `BACTOAI_SECRET`: `<session_signing_secret>`
* `BACTOAI_ADMIN_USER`: `bactoai`
* `BACTOAI_ADMIN_PASS`: `<admin_password>`
* `BACTOAI_ADMIN_CLINIC`: `BactoAI Admin`

### Frontend Web App Environment File: `bactoai/.env`

Located in the `bactoai/` folder. Used by the React / TanStack Start application.

```env
# Website Database (Collaborator Project)
SUPABASE_PROJECT_ID="ojnecaomcicsayeweoab"
SUPABASE_PUBLISHABLE_KEY="<public_anon_key>"
SUPABASE_URL="https://ojnecaomcicsayeweoab.supabase.co"

VITE_SUPABASE_PROJECT_ID="ojnecaomcicsayeweoab"
VITE_SUPABASE_PUBLISHABLE_KEY="<public_anon_key>"
VITE_SUPABASE_URL="https://ojnecaomcicsayeweoab.supabase.co"

# Prediction Engine Connection (Official Render Deployment)
MODEL_API_URL="https://bactoai-kt0q.onrender.com/api/v1"
MODEL_API_KEY="0f31dfb7ccc763239c15c817e4a059184a093466286bb7f9b3f0000b994ae786"
```

---

## 5. Architecture and Request Flow

```
+-------------------------------------------------------------------+
| 1. Public Visitor / Lab Tech                                      |
|    Visits bactoai.co.ke (or bactoai.lovable.app)                 |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| 2. React / TanStack Web App (bactoai/)                            |
|    - Authenticates users via Supabase Project: ojnecaomcicsayeweoab|
|    - Saves contact requests into public.contact_submissions       |
|    - Receives uploaded FASTA/FASTQ file                           |
+---------------------------------+---------------------------------+
                                  |
                                  | Server-side POST /api/v1/predict
                                  | Authorization: Bearer <MODEL_API_KEY>
                                  v
+-------------------------------------------------------------------+
| 3. ML Prediction Backend (bactoai-kt0q.onrender.com)             |
|    - Validates API key in public.api_keys                         |
|    - Processes genome with Biopython & k-mer feature extraction   |
|    - Runs XGBoost models (Meropenem, Ciprofloxacin, Cefotaxime)   |
|    - Persists run metadata to Project: ofuxwgapzjgcrsuiqpyu       |
|    - Returns JSON predictions with calibrated confidence scores   |
+-------------------------------------------------------------------+
```

---

## 6. Incident Triage Checklist

If predictions or health checks fail in the future, follow these steps:

1. **Check Render Health:**
   Run `curl https://bactoai-kt0q.onrender.com/health`.
2. **If `database_ok: false`:**
   Open the Supabase dashboard for project `ofuxwgapzjgcrsuiqpyu` ("bactoai"). If the project is paused, click **Resume project**.
3. **If `models_loaded: false`:**
   Check the Render deploy logs for Gunicorn startup warnings or memory limits during joblib model loading.
4. **If frontend reports "Prediction engine not connected":**
   Verify that `MODEL_API_URL` and `MODEL_API_KEY` are defined in the hosting environment settings (e.g. Vercel or Netlify dashboard) matching `bactoai/.env`.
