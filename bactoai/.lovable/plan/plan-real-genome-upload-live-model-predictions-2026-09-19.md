# Plan: Real genome upload → live model predictions

## Goal
Signed-in users can upload their own FASTA/FASTQ genome file on the site and get real AMR predictions from the team's actual Python model. Visitors who aren't signed in still see the current simulated sample demo.

## Architecture
The model (Python) cannot run on Lovable's hosting. It must run on an always-on server (Render or Railway — cheap, runs Python, always on) and expose an HTTPS API. The website calls that API.

```text
Browser (signed-in user)
   │  uploads genome file
   ▼
Lovable site — new server route /api/analyze (auth-checked)
   │  forwards file + shared secret header
   ▼
Model API on Render/Railway (FastAPI wrapper around existing model)
   │  returns JSON predictions
   ▼
Site renders real results in the existing results view
```

## Part A — I build now (website side)
1. **Upload UI in ProductDemo**: a "Upload your own genome" mode with file browse / drag-and-drop (.fasta/.fastq, size limit), shown only to signed-in users; signed-out visitors see a "Sign in to analyze your own genomes" prompt linking to /auth.
2. **Server route `src/routes/api/analyze.ts`**: verifies the user's session, validates the file (extension, size cap, basic FASTA/FASTQ sanity check), forwards it to the model API (`MODEL_API_URL` + `MODEL_API_KEY` secrets), returns the predictions JSON.
3. **Results rendering**: real predictions render in the same per-antibiotic result cards used by the simulated demo, with a "results from live model" indicator and clear error states (model offline, invalid file, timeout).
4. Keep the four simulated samples exactly as they are for the public demo.
5. Update sitemap/SEO unaffected; verify build passes.

## Part B — the team does, with my step-by-step guide (model side)
1. Share or package the model code (a GitHub repo is fine — GitHub matters *here*, for deploying the model, not for the website).
2. Deploy it to Render or Railway with a small FastAPI wrapper exposing `POST /predict` accepting a FASTA/FASTQ file and returning `{ organism, predictions: [{ drug, status, confidence }] }`. I'll supply a ready-made wrapper template the team can drop the model into.
3. Add the deployed API URL and key as project secrets (`MODEL_API_URL`, `MODEL_API_KEY`) via the secure form.
4. End-to-end test with a real isolate.

## Contract between site and model API
- Request: `POST {MODEL_API_URL}/predict`, header `X-API-Key: {MODEL_API_KEY}`, multipart file field `file`.
- Response 200: `{ "organism": "string", "predictions": [{ "drug": "string", "status": "Resistant"|"Susceptible", "confidence": 0-100 }] }`
- Errors: 4xx invalid input, 5xx model failure — site shows a friendly message.

## Security
- Analysis is signed-in only (session verified in the server route, not just hidden UI).
- Model API requires a shared secret key so only our site can call it.
- Uploaded genomes are not stored by default (processed in transit); storage/audit history can be a follow-up.

## Out of scope (follow-ups if wanted)
- Storing analysis history per user, PDF export of real results, usage limits/rate limiting per user.
