"""Export the verified prediction metrics to a compact summary CSV."""
import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
RESULTS_DIR = "validation_results"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(PROJECT_ROOT, RESULTS_DIR, "corrected_metrics.json"), encoding="utf-8") as f:
    metrics = json.load(f)

output_path = os.path.join(PROJECT_ROOT, RESULTS_DIR, "test_predictions_summary.csv")
live_rule = (
    "adaptive_threshold = 0.50 + min(uncertainty*0.5,0.15); "
    "confidence HIGH if uncertainty<=0.05"
)
header = [
    "drug", "model_version", "n_test", "auc", "sensitivity", "specificity",
    "ppv", "npv", "accuracy", "tp", "tn", "fp", "fn", "vme_rate", "me_rate",
    "threshold", "notes", "live_rule_applied", "live_flips_vs_fixed",
    "live_metrics_equal_fixed", "live_rule",
]

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for drug in ("meropenem", "ciprofloxacin", "cefotaxime"):
        result = metrics[drug]
        live = result["live"]
        writer.writerow([
            drug, "v4_ensemble", result["n_test"], result["auc"],
            result["sensitivity"], result["specificity"], result["ppv"],
            result["npv"], result["accuracy"], result["tp"], result["tn"],
            result["fp"], result["fn"], result["vme_rate"], result["me_rate"],
            result["threshold"], result.get("note", ""), True,
            live["flips_vs_fixed"], live["metrics_equal_fixed"], live_rule,
        ])

    result = metrics["bvbrc_benchmark"]
    writer.writerow([
        "cefotaxime", "bvbrc_in_corpus_benchmark", result["n_evaluated"],
        result["auc"], result["sensitivity"], result["specificity"],
        result["ppv"], result["npv"], result["accuracy"], result["tp"],
        result["tn"], result["fp"], result["fn"], result["vme_rate"],
        result["me_rate"], result["threshold"], result["note"], False,
        "N/A", "N/A", "N/A",
    ])

print(f"Saved verified metrics summary: {output_path}")
