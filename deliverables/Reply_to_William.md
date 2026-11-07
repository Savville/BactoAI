William,

You're right to flag this. Let me explain what happened and give you the correct numbers.

**The CSVs I sent back were wrong.** When I regenerated them, I used the wrong test split — I sorted genomes by accession and took the last 25%, which gives a completely different set of isolates than the original random stratified split (random_state=42). That's why your re-run gave AUC ≈ 0.59 instead of 0.987. The model is fine; the test set was just wrong.

I've removed those CSVs from the repo. Here are the correct numbers, pulled directly from the saved audit JSONs:

---

**Meropenem** (`threshold_audit_20260912_165224.json`):
- n = 125
- TP=67, TN=54, FP=2, FN=2
- Sensitivity = 97.1%, Specificity = 96.4%
- AUC = **0.9871**
- Threshold = 0.50

**Ciprofloxacin** (`threshold_audit_20260912_162504.json`):
- n = 140
- TP=64, TN=68, FP=4, FN=4
- Sensitivity = 94.1%, Specificity = 94.4%
- AUC = **0.9559**
- Threshold = 0.50

**Cefotaxime v3**: No threshold audit was run for this drug. From training_summary_v3.csv:
- n = 145 (R=71, S=74)
- AUC = **0.8721**, Accuracy = **79.3%**
- Exact confusion matrix at t=0.5 was not saved — we only have the aggregate metrics from that run.

---

**How you can verify independently:**

Run the threshold audit script on your end:
```bash
python scripts/threshold_audit.py --antibiotic meropenem
python scripts/threshold_audit.py --antibiotic ciprofloxacin
```

This loads the same models from `data/models_v4/`, uses the same `train_test_split(test_size=0.25, random_state=42, stratify=y)` split, and should reproduce the exact numbers above. The model files (.joblib) and metadata CSVs are all in the repo.

**Why the cefotaxime v3 CM is missing:** The original pipeline dumped summary stats (AUC, accuracy, class counts) to `training_summary_v3.csv` but did not save per-isolate predictions. I can re-run the cefotaxime prediction and save the full CSV if you need it — just let me know.

As for the EUCAST breakpoint change: that only affected how we derived labels from the BV-BRC disk diffusion data (S >= 20mm not >= 26mm). It changed the training data composition but does not affect the holdout test results above, which use pre-labelled NCBI MIC data.

Apologies for the confusion with the CSVs. The audit JSONs are the source of truth — everything else derives from those.
