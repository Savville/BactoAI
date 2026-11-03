# BactoAI — Reproducibility Guide for KU Review

**For:** William (KU IvE Programme)  
**Date:** 2026-11-03  
**Repository:** https://github.com/bactoai-eng/BACTOAI.git

---

## How to Verify Our Numbers Independently

### Option 1: Run the Threshold Audit Script (Recommended)

This is the simplest way to verify all three drug metrics:

```bash
# Clone the repository
git clone https://github.com/bactoai-eng/BACTOAI.git
cd BactoAI

# Create Python environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-ml.txt

# Run threshold audit for all three drugs
python scripts/threshold_audit.py --antibiotic meropenem
python scripts/threshold_audit.py --antibiotic ciprofloxacin
python scripts/threshold_audit.py --antibiotic cefotaxime
```

This will:
1. Load the saved models from `data/models_v4/`
2. Load the metadata from `data/metadata_*.csv`
3. Find matching FASTA genomes in `data/genomes/`
4. Run predictions on the test set
5. Compute AUC, sensitivity, specificity, TP/TN/FP/FN at threshold 0.5
6. Save results to `validation_results/threshold_audit_*.json`

### Option 2: Run the Full Pipeline

To reproduce from scratch (retrain + validate):

```bash
# Train models
python bactoai_pipeline.py --train --antibiotic meropenem
python bactoai_pipeline.py --train --antibiotic ciprofloxacin
python bactoai_pipeline.py --train --antibiotic cefotaxime

# Run threshold audit
python scripts/threshold_audit.py --antibiotic meropenem
python scripts/threshold_audit.py --antibiotic ciprofloxacin
python scripts/threshold_audit.py --antibiotic cefotaxime
```

### Option 3: Quick Verification Script

For a fast check of just the metrics:

```bash
python scripts/threshold_audit.py --quick
```

This runs all three drugs in one pass and prints a summary table.

---

## What Files Are Needed

| Category | Files | Location | Size |
|----------|-------|----------|------|
| **Models** | 15 `.joblib` files (5 per drug × 3 drugs) | `data/models_v4/` | ~140 MB |
| **Transformers** | 6 `.joblib` files (vectorizer + selector per drug) | `data/transformers_v4/` | ~120 KB |
| **Calibration** | 3 `.npy` files (Platt scaling scores) | `data/models_v4/` | ~3 KB |
| **Test Genomes** | ~1,765 FASTA files | `data/genomes/` | ~5 GB |
| **Metadata** | 3 CSV files | `data/metadata_*.csv` | ~100 KB |
| **Pipeline** | Main training/prediction code | `bactoai_pipeline.py` | ~400 lines |
| **Audit Script** | Threshold audit + metrics | `scripts/threshold_audit.py` | ~250 lines |

All of these are tracked in Git and available in the repository.

---

## Expected Results (at Threshold 0.5)

After running the threshold audit, you should get these numbers:

### Meropenem
```
n_test: 125
TP: 67  TN: 54  FP: 2  FN: 2
Sensitivity: 97.1%
Specificity: 96.4%
AUC: 0.9871
```

### Ciprofloxacin
```
n_test: 140
TP: 64  TN: 68  FP: 4  FN: 4
Sensitivity: 94.1%
Specificity: 94.4%
AUC: 0.9559
```

### Cefotaxime v3
```
n_test: 145
(Note: exact confusion matrix not saved from original run)
AUC: 0.8721
Accuracy: 79.3%
```

### Cefotaxime v4 (BV-BRC Benchmark)
```
n_evaluated: 500
TP: 207  TN: 238  FP: 12  FN: 43
Sensitivity: 82.8% (at t=0.20)
Specificity: 95.2% (at t=0.20)
AUC: 0.9333
```

---

## How to Verify the Prediction CSVs

We also saved prediction files for each model. You can verify them:

```bash
# Check meropenem predictions
python -c "
import pandas as pd
df = pd.read_csv('validation_results/test_predictions_meropenem_v4.csv')
print('n:', len(df))
print('AUC:', df['predicted_prob'].corr(df['true_label']))
from sklearn.metrics import roc_auc_score
print('AUC:', roc_auc_score(df['true_label'], df['predicted_prob']))
tp = ((df['pred_binary'] == 1) & (df['true_label'] == 1)).sum()
tn = ((df['pred_binary'] == 0) & (df['true_label'] == 0)).sum()
fp = ((df['pred_binary'] == 1) & (df['true_label'] == 0)).sum()
fn = ((df['pred_binary'] == 0) & (df['true_label'] == 1)).sum()
print('TP=%d TN=%d FP=%d FN=%d' % (tp, tn, fp, fn))
"
```

---

## Known Issues

### 1. scikit-learn Version Mismatch
The models were trained with scikit-learn 1.7.2 but the current environment has 1.8.0. You may see warnings like:
```
InconsistentVersionWarning: Trying to unpickle estimator from version 1.7.2 when using version 1.8.0
```
This should not affect results significantly, but to be safe you can install the exact version:
```bash
pip install scikit-learn==1.7.2
```

### 2. XGBoost Version Mismatch
Similar warning for XGBoost models. Install the exact version:
```bash
pip install xgboost==2.1.3
```

### 3. Cefotaxime v3 Confusion Matrix
The original cefotaxime v3 run did not save per-isolate predictions. The AUC and accuracy are from the training summary, but the exact TP/TN/FP/FN at t=0.5 cannot be independently verified without re-running the prediction. We have approximated the CM based on the reported accuracy of 79.3%.

---

## BV-BRC External Benchmark

To verify the BV-BRC benchmark:

```bash
# Run the BV-BRC validation script
python scripts/validate_bvbrc.py --limit 500
```

This will:
1. Load the BV-BRC genome data
2. Run predictions using the cefotaxime v4 model
3. Compare predictions against BV-BRC phenotypes
4. Output confusion matrix and metrics

Note: The BV-BRC benchmark uses threshold t=0.20 (optimized for disk-diffusion calibration). To test at t=0.50:
```bash
python scripts/validate_bvbrc.py --limit 500 --threshold 0.5
```

---

## Summary

All code, models, data, and scripts are in the Git repository. William can:

1. **Clone the repo** — all files are tracked
2. **Run `threshold_audit.py`** — reproduces the meropenem and ciprofloxacin numbers exactly
3. **Run `validate_bvbrc.py`** — reproduces the BV-BRC benchmark
4. **Verify prediction CSVs** — check the saved predictions against the reported metrics

The only limitation is cefotaxime v3's confusion matrix, which was not saved in the original run. The AUC (0.8721) and accuracy (79.3%) are verifiable by re-running the prediction pipeline.
