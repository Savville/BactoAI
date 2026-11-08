# BactoAI Infrastructure, Accounts, and Environment Reference

Date: October 27, 2026  
Status: Updated 2026-11-08 with owner-provided account details; Render backend URL confirmed, key value remains masked.

This document records known accounts, configured project references, and deployment settings. Treat values masked in dashboard screenshots and any unconfirmed project ownership as unresolved.

---

## 1. Supabase Databases

BactoAI uses two distinct Supabase projects. They serve different layers and do not need to be merged.

### Backend Database (ML Prediction Engine)

* **Project ID:** `ofuxwgapzjgcrsuiqpyu`
* **Project Name in Dashboard:** `bactoai`
* **Account Owner:** `ochiwilliamotieno@gmail.com` (owner-provided)
* **Host URL:** `https://ofuxwgapzjgcrsuiqpyu.supabase.co`
* **Project region:** `eu-west-2` (owner-provided dashboard screenshot, 2026-11-08)
* **Purpose:** Stores backend prediction history, validation feedback, and server authentication.
* **Tables:**
  * `public.users` (legacy and admin credentials for the Flask dashboard)
  * `public.api_keys` (SHA-256 hashed keys for `/api/v1/predict`)
  * `public.submissions` (uploaded genome metadata, drug probabilities, confidence scores)
  * `public.feedback` (microbiology laboratory confirmation records)
  * `public.audit_log` (event timestamps and request IPs)
* **Auto-Pause Note:** Free-tier Supabase projects pause after 7 days of inactivity. If the Render health check ever reports `database_ok: false` or DNS fails, log into this account and click **Resume project**. Restoration takes about 2 minutes.

### Intended Website Database (Public Web App)

* **Project ID:** `ojnecaomcicsayeweoab`
* **Account Owner:** Intended to be the BactoAI account; exact project/account still being identified
* **Host URL:** `https://ojnecaomcicsayeweoab.supabase.co`
* **Project region:** Not yet confirmed
* **Purpose:** The local frontend configuration references this project. Confirm in the Supabase dashboard that this is the intended/current project before relying on it.
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
| Render service `srv-daob3gv40ujc73ejs44g` | `bactoai@gmail.com` (owner-provided) | Public hostname and current health not confirmed from the supplied settings screenshot | ML prediction API / Gunicorn service |
| `https://bactoai.onrender.com` | Previously described as a personal account | Status not re-confirmed | Confirm the service and hostname before use |

The owner confirms the Render `SUPABASE_URL` is `https://ofuxwgapzjgcrsuiqpyu.supabase.co`, the backend project. The screenshot masks the `SUPABASE_KEY`, so its role is not confirmed. The service's public hostname and current health are also unconfirmed.

---

## 4. Environment File Configurations

### Root Backend Environment File: `.env`

Located at the repository root. Used by local Flask scripts. The supplied Render screenshot masks values, so it does not establish that the local and Render values match.

```env
SUPABASE_URL=https://ofuxwgapzjgcrsuiqpyu.supabase.co
SUPABASE_KEY=<key value not shown; role unverified>
```

Render dashboard variables (service `srv-daob3gv40ujc73ejs44g`):
* `SUPABASE_URL`: Confirmed by the owner as `https://ofuxwgapzjgcrsuiqpyu.supabase.co` (backend project).
* `SUPABASE_KEY`: Present; masked in the supplied screenshot. Key role is unconfirmed.
* `BACTOAI_SECRET`: `<session_signing_secret>`
* `BACTOAI_ADMIN_USER`: `bactoai`
* `BACTOAI_ADMIN_PASS`: `<admin_password>`
* `BACTOAI_ADMIN_CLINIC`: `BactoAI Admin`

### Frontend Web App Environment File: `bactoai/.env`

Located in the `bactoai/` folder. Used by the React / TanStack Start application.

```env
# Website Database (intended BactoAI account; exact project/account still being identified)
SUPABASE_PROJECT_ID="ojnecaomcicsayeweoab"
SUPABASE_PUBLISHABLE_KEY="<public_anon_key>"
SUPABASE_URL="https://ojnecaomcicsayeweoab.supabase.co"

VITE_SUPABASE_PROJECT_ID="ojnecaomcicsayeweoab"
VITE_SUPABASE_PUBLISHABLE_KEY="<public_anon_key>"
VITE_SUPABASE_URL="https://ojnecaomcicsayeweoab.supabase.co"

# Prediction Engine Connection (Render service hostname must be confirmed)
MODEL_API_URL="<confirm the public URL for srv-daob3gv40ujc73ejs44g>"
MODEL_API_KEY=<set in hosting secret settings>
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
|    - Local config references Supabase Project: ojnecaomcicsayeweoab|
|    - Saves contact requests into public.contact_submissions       |
|    - Receives uploaded FASTA/FASTQ file                           |
+---------------------------------+---------------------------------+
                                  |
                                  | Server-side POST /api/v1/predict
                                  | Authorization: Bearer <MODEL_API_KEY>
                                  v
+-------------------------------------------------------------------+
| 3. ML Prediction Backend (Render service hostname unconfirmed)    |
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

1. **Confirm Render service URL:**
   In Render, open service `srv-daob3gv40ujc73ejs44g` and verify its name and public URL before testing health.
2. **If `database_ok: false`:**
   Open the Supabase dashboard for project `ofuxwgapzjgcrsuiqpyu` ("bactoai"). If the project is paused, click **Resume project**.
3. **If `models_loaded: false`:**
   Check the Render deploy logs for Gunicorn startup warnings or memory limits during joblib model loading.
4. **If frontend reports "Prediction engine not connected":**
   Verify that `MODEL_API_URL` and `MODEL_API_KEY` are defined in the hosting environment settings (e.g. Vercel or Netlify dashboard) matching `bactoai/.env`.
