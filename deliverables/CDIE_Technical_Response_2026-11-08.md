# CDIE evidence and clarification

**8 November 2026**

The evidence bundle contains the requested scripts, test splits, prediction CSVs, model manifest and verification, drug metadata, and BV-BRC table. The prediction CSVs include uncertainty, adaptive threshold, live label and confidence.

## Reviewer checklist

Status: **Done** means supported by the included repository evidence; **Partial** means the available evidence is incomplete; **Owner action** requires dashboard access, missing source data, or a new analysis.

| Reviewer request | Status | Response |
|:--|:--|:--|
| Requested scripts, split/prediction CSVs, manifests, metadata, BV-BRC data; explain “E.coli isolates.csv” | **Done / Partial** | Files are in the branch and evidence bundle. That filename was not found in the repository. |
| Add uncertainty, adaptive threshold, live label and confidence; report live and fixed-threshold metrics | **Done** | Included for 412 rows. Live and fixed-0.50 results match; LOW confidence is 0 for each drug. |
| Identify deployed model classes and whether RF/LightGBM are used | **Done** | Five calibrated soft-voting models per drug; each base voting model includes XGBoost, Random Forest and LightGBM. |
| Training software versions and live-path prediction comparison | **Partial** | scikit-learn 1.7.2 is recorded; exact XGBoost training version is not established. A 30-isolate local live-path check passed, but this is not a direct Render execution. |
| Label sources, per-drug NCBI/BV-BRC counts, and I/ND/DD/NS handling | **Partial** | Deployed metadata has 600 NCBI labels and zero BV-BRC labels per drug. Available intermediate/missing-result evidence is incomplete; historical filtering rules cannot all be recovered. |
| Assembly versions used for FASTAs | **Done** | Exact accessions and checksums are listed in the genome manifest; this records the versions used, not newer NCBI replacements. |
| Kenyan-isolate count, source and train/test assignment | **Partial** | The two Kenyan accessions in deployed metadata are in training. A separate enrichment file has seven records; its study attribution comes from the supplied review, and relatedness was not assessed. |
| Supabase regions, RLS screenshots, Render key role, read-only access and retention | **Partial / Owner action** | Backend project `ofuxwgapzjgcrsuiqpyu` is in `eu-west-2`. The owner reports RLS is enabled on all backend tables; the screenshot shows the visible `api_keys`, `audit_log`, `feedback`, `submissions`, and `users` tables each also have an `ALL` policy applied to `public`. That is broad access, not an adequate least-privilege policy. Website project availability/region, Render key role, read-only access, and retention decision still need confirmation. No automated retention period is configured for records/logs. |
| Remove superseded record, correct old performance values, and avoid invalid population script | **Done** | Superseded deliverables and invalid audit results were removed from the branch; `populate_isolate_table.py` was not run. |
| Explain v3/v4 cefotaxime AUC difference and deployed model | **Partial** | Production uses v4 according to local artifacts and the supplied Render review. The old v3 model/predictions are unavailable, so its AUC difference cannot be reconciled. |
| Explain test-size and cefotaxime accuracy changes | **Partial** | The old split was non-equivalent and is withdrawn. The old cefotaxime row-level output is unavailable, so the one-call difference cannot be traced. |
| Reproduce 0.9333 and 0.7793 results | **Done** | 0.9333 is reproducible as an in-corpus benchmark, not external validation; 0.7793 is withdrawn for lack of row-level predictions. |
| Calibration data, threshold origin and test-data involvement | **Partial** | Platt calibration is fitted within training data. The test set is used for evaluation and saved conformal scores. The original rationale/selection history for thresholds is undocumented. |
| ANI/SNP or other train/test relatedness analysis | **Owner action** | No relatedness analysis has been run; possible leakage remains unmeasured. |

### Which accounts and projects to check

The repository account guide maps `ofuxwgapzjgcrsuiqpyu` to the **backend/ML Supabase project** and `ojnecaomcicsayeweoab` to the **website Supabase project**. The backend project area is confirmed as **eu-west-2** from the supplied dashboard screenshot. The owner reports RLS is enabled on every table in that backend project. The screenshot shows the visible `api_keys`, `audit_log`, `feedback`, `submissions`, and `users` tables each also have an `ALL` policy applied to `public`. That policy is broad; RLS being enabled does not make these tables private when a public policy permits all commands. Replace broad public access with least-privilege policies after checking the actual client/server access paths. The owner reports the website project may have been deleted, but this has not been independently confirmed; its status and region need checking in the BactoAI Gmail account. If it is unavailable, the website's Supabase Auth and project-backed data will fail until the project is restored or the website is migrated to a replacement. Predictions through Render depend separately on the backend's configured Supabase URL and database access. The account guide maps `bactoai-kt0q.onrender.com` to the **active production Render service** under the official BactoAI account, but the service ID `srv-daob3gv40ujc73ejs44g` shared by the owner is not yet matched to that hostname. Confirm the service name and public URL in Render before relying on the guide; the guide does not identify which of the two email logins owns each dashboard.

The older `PREDICTION_PIPELINE_FIX.md` recommends redirecting the backend to the website Supabase project. That conflicts with the current backend configuration and account guide; do not use that instruction as the current configuration without confirming the intended migration. The backend migration target also needs owner review.

| Drug | n (R/S) | Sensitivity | Specificity | VME | ME | Low confidence | AUC (95% CI) |
|:--|--:|--:|--:|--:|--:|--:|:--|
| Meropenem | 124 (70/54) | 91.4% | 87.0% | 8.6% (6/70) | 13.0% (7/54) | 0/124 | 0.9421 (0.9009–0.9832) |
| Ciprofloxacin | 143 (70/73) | 80.0% | 83.6% | 20.0% (14/70) | 16.4% (12/73) | 0/143 | 0.8773 (0.8189–0.9357) |
| Cefotaxime | 145 (71/74) | 83.1% | 74.3% | 16.9% (12/71) | 25.7% (19/74) | 0/145 | 0.8723 (0.8132–0.9314) |

These metrics are identical at fixed 0.50 and under the deployed adaptive rule on all 412 test rows. The live rule is `0.50 + min(0.5 × ensemble standard deviation, 0.15)`. A separate 30-isolate check against the local `predict_single_antibiotic()` path found no label or confidence mismatches and probability differences below 7.3e-7.

## Model, thresholds, and calibration

Five saved `CalibratedClassifierCV` objects are loaded per drug. Each wraps a soft-voting `VotingClassifier` with XGBoost, Random Forest and LightGBM. This is five calibrated top-level models per drug, not one 15-model ensemble. Local `joblib.load()` inspection confirms the classes; Sam's Render review reports that production loads these `models_v4` assets and that all 21 deployed-file hashes match the earlier supplied manifest. The current manifest records the asset hashes; direct Render access was not available for this review.

The current cefotaxime artifact is from `models_v4`; the prediction output is named `test_predictions_cefotaxime_v4.csv`. Its reconstructed holdout AUC is 0.872288. `training_summary_v3.csv` records 0.872097 and 79.31% accuracy, but the corresponding v3 model and row-level predictions are unavailable, so that result cannot be reconciled or claimed to describe the current artifact. The current v4 CSV and `summary_cefotaxime.json` agree at 0.872288 and 78.62% (114/145).

Each deployed `metadata_{drug}.csv` has 600 NCBI labels and zero BV-BRC labels. `requirements-ml.txt` declares scikit-learn 1.7.2 and XGBoost 3.2.0; the serialized estimator confirms scikit-learn 1.7.2. The exact XGBoost training version is not established, and loading emits a serialized-model compatibility warning. Local verification used scikit-learn 1.8.0 and XGBoost 3.2.0.

The deployed code sets a 0.50 base threshold, a 0.15 maximum increase, and HIGH/MEDIUM/LOW uncertainty cutoffs of 0.05 and 0.15. The code comment says the increase is intended to reduce false positives. No documented threshold-selection or clinical decision-cost analysis was found; it can increase false-susceptible calls and is not a validated safety feature. No evidence establishes whether test results informed the original choice. All current test rows are HIGH and no calls changed under the adaptive rule.

`CalibratedClassifierCV(method="sigmoid", cv=5)` is fitted on training-partition data. The test partition is not used to fit this Platt calibrator, but it is used for reported evaluation and for the saved conformal nonconformity scores. The earlier statement that test data was not used for calibration scores was imprecise.

## Previous figures and split differences

The previous 0.9871 and 0.9559 AUCs came from the `threshold_audit` split, which did not reproduce the training split and overlapped training rows. They are withdrawn as holdout results. Earlier counts of 125/140/147 also came from that non-equivalent split. The reproduced split deduplicates assembly accessions, shuffles with seed 42, excludes missing/unreadable FASTAs, then performs a stratified 25% split; it yields 124/143/145.

The earlier cefotaxime 79.31% accuracy corresponds to 115/145, while the verified v4 output is 114/145 (78.62%). The old row-level predictions are unavailable, so the one-call discrepancy cannot be traced; 79.31% is superseded.

The 0.9333 BV-BRC cefotaxime AUC is reproducible from the 500-row benchmark CSV (0.933336 from stored probabilities). At the stored 0.20 operating point the confusion counts are TP=207, TN=238, FP=12, FN=43. This is an in-corpus benchmark, not independent external validation; the rationale for 0.20 is undocumented. The 0.7793 combined-model AUC appears only in a training summary; its 1,000-row prediction output is unavailable, so we withdraw it from reported performance.

No ANI or SNP-cluster analysis has been run; relatedness across the random split is unknown. The relatedness tool is not installed in this environment, so this remains open. Test genome accessions and SHA-256 values are in the test manifest, but the FASTA files are not tracked in Git. Full sequence-level regeneration requires those inputs; the CSV verification script independently recomputes metrics without them.

The “two Kenyan isolates” figure counts unique accessions in the deployed NCBI metadata (1,673 unique accessions across drugs). A separate enrichment CSV contains seven Kenyan *K. pneumoniae* meropenem records; the PRJNA717739 attribution is from the supplied review message, not a field in that CSV. The two accessions present in current metadata are GCA_019927625.1 and GCA_020407015.1; both are in training, not the test split. The all-metadata genome manifest records the exact FASTA accession version and checksum for each required assembly. GCA_019927405.1 is not in that manifest or local `data/genomes/`, so it was not used for these results.

## Repository and remaining checks

The website and backend Supabase projects will remain separate through the CDIE deadline; afterward, their boundaries should be reviewed against data trust, access control and operational ownership before deciding whether to consolidate. The backend project is `ofuxwgapzjgcrsuiqpyu` in `eu-west-2`; the owner reports RLS is enabled on all backend tables, but the screenshot shows broad `ALL` policies applied to `public` on the visible tables. Replace those policies with least-privilege rules after confirming application access requirements. The website project is `ojnecaomcicsayeweoab`; the owner suspects it may have been deleted, and its status, region and RLS settings remain unverified. The Render service ID and production hostname, key role, dashboard-account ownership and read-only reviewer access also remain unverified. The local backend migration points to the website project and defines permissive policies, while backend configuration names the backend project. Prediction records, feedback and IP logs have no automated retention policy; uploaded FASTA files are not retained. The project owner still needs to verify the website project and Render service, provide the remaining Table Editor evidence, and set a retention policy.

The requested `metadata_{drug}.csv` and `BVBRC_genome_amr.csv` are included in the repository branch. The tracked `.venv` and obsolete `data/models/` and `data/transformers/` assets are removed from the branch index without deleting local copies. The current loader uses the v4 directories. “E.coli isolates.csv” was not found in the repository; its source cannot be identified without a path or copy. `populate_isolate_table.py` was not run. The model files in branch history are ordinary Git objects; the Dockerfile has no Git LFS pull step.

Independent verification: `ALL_DRUGS_PASS: true`. Reproduction commands:

```text
python scripts/regenerate_test_predictions.py --workers 8
python scripts/verify_regenerated_predictions.py
python scripts/check_live_prediction_consistency.py
```
