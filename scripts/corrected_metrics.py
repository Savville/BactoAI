"""
BactoAI — Corrected Metrics for NPHL Submission
================================================
Reconciles all model metrics across deliverables.
Sources of truth: validation_results/threshold_audit_*.json, bvbrc_validation_summary_*.json
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =====================================================================
# TRUE VALUES (from validation JSONs)
# =====================================================================

# Meropenem: threshold_audit_20260912_165224.json
MEROPENEM = {
    "auc": 0.98706,
    "n_test": 125,
    "tp": 67, "tn": 54, "fp": 2, "fn": 2,
    "sensitivity": 0.971,
    "specificity": 0.9643,
    "accuracy": 0.968,
    "ppv": 0.971,
    "npv": 0.9643,
    "vme_rate": 0.029,   # FN / (FN+TP) = 2/69
    "me_rate": 0.036,    # FP / (FP+TN) = 2/56
    "threshold": 0.5,
}

# Ciprofloxacin: threshold_audit_20260912_162504.json
CIPROFLOXACIN = {
    "auc": 0.955882,
    "n_test": 140,
    "tp": 64, "tn": 68, "fp": 4, "fn": 4,
    "sensitivity": 0.9412,
    "specificity": 0.9444,
    "accuracy": 0.9429,
    "ppv": 0.9412,
    "npv": 0.9444,
    "vme_rate": 0.0588,  # 4/68
    "me_rate": 0.0556,   # 4/72
    "threshold": 0.5,
}

# Cefotaxime v3 (NCBI only, before BV-BRC retraining): training_summary_v3.csv
# n_test_resistant=71, n_test_susceptible=74, total=145, AUC=0.8721, Acc=79.3%
# We don't have confusion matrix for v3 — need to compute or note as unavailable
CEFOTAXIME_V3 = {
    "auc": 0.8721,
    "n_test": 145,
    "tp": None, "tn": None, "fp": None, "fn": None,  # not in audit JSON
    "sensitivity": None,
    "specificity": None,
    "accuracy": 0.7931,
    "n_test_resistant": 71,
    "n_test_susceptible": 74,
    "threshold": 0.5,
    "note": "v3 NCBI-only model; confusion matrix not in threshold audit JSON",
}

# Cefotaxime v4 (combined NCBI+BV-BRC): training_summary_v4.csv
# n_test_resistant=167, n_test_susceptible=833, total=1000, AUC=0.7793
CEFOTAXIME_V4 = {
    "auc": 0.7793,
    "n_test": 1000,
    "n_test_resistant": 167,
    "n_test_susceptible": 833,
    "accuracy": 0.859,
    "threshold": 0.5,
    "note": "v4 combined model; NOT deployed (production uses v3)",
}

# BV-BRC external benchmark (bvbrc_validation_summary_20260914_070116.json)
# NOTE: These 500 genomes are FROM the same BV-BRC source as training data.
# This is an in-corpus benchmark, NOT independent external validation.
BVBRC_BENCHMARK = {
    "auc": 0.9333,
    "n_evaluated": 500,
    "tp": 207, "tn": 238, "fp": 12, "fn": 43,
    "sensitivity": 0.828,
    "specificity": 0.952,
    "accuracy": 0.89,
    "ppv": 0.9452,
    "npv": 0.8470,
    "vme_rate": 0.172,   # 43/250
    "me_rate": 0.048,    # 12/250
    "threshold": 0.20,   # optimal threshold for disk-diffusion calibration
    "note": "In-corpus benchmark on BV-BRC holdout. NOT independent external validation.",
}

# =====================================================================
# Export as JSON for other scripts to use
# =====================================================================
OUTPUT = os.path.join(PROJECT_ROOT, "validation_results", "corrected_metrics.json")
metrics = {
    "meropenem": MEROPENEM,
    "ciprofloxacin": CIPROFLOXACIN,
    "cefotaxime_v3": CEFOTAXIME_V3,
    "cefotaxime_v4": CEFOTAXIME_V4,
    "bvbrc_benchmark": BVBRC_BENCHMARK,
    "generated_at": "2026-11-03",
    "notes": {
        "meropenem": "From threshold_audit_20260912_165224.json",
        "ciprofloxacin": "From threshold_audit_20260912_162504.json",
        "cefotaxime_v3": "From training_summary_v3.csv (AUC, accuracy only; CM unavailable)",
        "cefotaxime_v4": "From training_summary_v4.csv (retrained on BV-BRC, NOT deployed)",
        "bvbrc_benchmark": "FROM bvbrc_validation_summary_20260914_070116.json — in-corpus benchmark, not independent external validation",
    }
}
with open(OUTPUT, "w") as f:
    json.dump(metrics, f, indent=2)
print("Saved corrected metrics to:", OUTPUT)

# Print summary
print()
print("=" * 70)
print("  CORRECTED METRICS SUMMARY")
print("=" * 70)
for drug, m in metrics.items():
    if drug in ("cefotaxime_v3", "cefotaxime_v4"):
        print(f"\n{drug.upper()}:")
        print(f"  AUC: {m['auc']}")
        print(f"  n_test: {m['n_test']}")
        print(f"  Accuracy: {m['accuracy']:.1%}")
        if "note" in m:
            print(f"  Note: {m['note']}")
    elif drug == "bvbrc_benchmark":
        print(f"\n{drug.upper()} (IN-CORPUS BENCHMARK, not external):")
        print(f"  AUC: {m['auc']}")
        print(f"  n: {m['n_evaluated']}")
        print(f"  TP={m['tp']} TN={m['tn']} FP={m['fp']} FN={m['fn']}")
        print(f"  Sens: {m['sensitivity']:.1%}  Spec: {m['specificity']:.1%}")
        print(f"  Threshold: {m['threshold']}")
        print(f"  Note: {m['note']}")
    else:
        m2 = m
        print(f"\n{drug.upper()}:")
        print(f"  AUC: {m2['auc']}")
        print(f"  n: {m2['n_test']}")
        print(f"  TP={m2['tp']} TN={m2['tn']} FP={m2['fp']} FN={m2['fn']}")
        print(f"  Sens: {m2['sensitivity']:.1%}  Spec: {m2['specificity']:.1%}")
        print(f"  VME: {m2['vme_rate']:.1%}  ME: {m2['me_rate']:.1%}")
        print(f"  Threshold: {m2['threshold']}")
