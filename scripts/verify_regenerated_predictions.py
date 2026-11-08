"""
Independent verification of the regenerated test-prediction CSVs.

Reads only the three CSVs plus the saved calibration_scores_*.npy and
summary_*.json, and recomputes every reported metric from scratch. Also
records SHA256 hashes of the deployed assets.

This script does NOT use export_all_predictions.py or threshold_audit.py.
"""
import os, sys, json, hashlib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

FILES = {
    "meropenem":     ("validation_results/test_predictions_meropenem_v4.csv",     "data/models_v4/summary_meropenem.json",     "data/models_v4/calibration_scores_meropenem.npy"),
    "ciprofloxacin": ("validation_results/test_predictions_ciprofloxacin_v4.csv", "data/models_v4/summary_ciprofloxacin.json", "data/models_v4/calibration_scores_ciprofloxacin.npy"),
    "cefotaxime":    ("validation_results/test_predictions_cefotaxime_v4.csv",    "data/models_v4/summary_cefotaxime.json",    "data/models_v4/calibration_scores_cefotaxime.npy"),
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out = {"per_drug": {}, "model_sha256": {}}
    ok_all = True
    for ab, (csv_path, summary_path, calib_path) in FILES.items():
        df = pd.read_csv(csv_path)
        y = df.true_label.to_numpy()
        p = df.predicted_prob.to_numpy()
        pred = df.pred_binary.to_numpy()

        tp = int(((pred == 1) & (y == 1)).sum())
        tn = int(((pred == 0) & (y == 0)).sum())
        fp = int(((pred == 1) & (y == 0)).sum())
        fn = int(((pred == 0) & (y == 1)).sum())
        n = len(df)
        auc = float(roc_auc_score(y, p))
        acc = (tp + tn) / n
        sens = tp / (tp + fn) if (tp + fn) else None
        spec = tn / (tn + fp) if (tn + fp) else None

        rec = {
            "csv": csv_path,
            "n": n, "R": int((y == 1).sum()), "S": int((y == 0).sum()),
            "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "predR": int((pred == 1).sum()),
            "auc": auc, "accuracy": acc,
            "sensitivity": sens, "specificity": spec,
            "vme_rate": fn / (tp + fn) if (tp + fn) else None,
            "me_rate": fp / (tn + fp) if (tn + fp) else None,
            "ppv": tp / (tp + fp) if (tp + fp) else None,
            "npv": tn / (tn + fn) if (tn + fn) else None,
            "pred_binary_matches_prob": bool((pred == (p >= 0.5).astype(int)).all()),
        }

        # Verify the live decision rule columns (uncertainty, adaptive threshold,
        # live label, confidence) against the values used by predict_single_antibiotic.
        required = {"uncertainty", "adaptive_threshold", "live_pred_binary",
                    "live_label", "confidence", "lower_bound", "upper_bound"}
        rec["live_rule_columns_present"] = required.issubset(df.columns)
        if rec["live_rule_columns_present"]:
            std = df.uncertainty.to_numpy()
            thr = 0.5 + np.minimum(std * 0.5, 0.15)
            live = (p >= thr).astype(int)
            conf = np.where(std <= 0.05, "HIGH", np.where(std <= 0.15, "MEDIUM", "LOW"))
            rec["adaptive_threshold_matches"] = bool(np.allclose(df.adaptive_threshold, thr, atol=1e-5))
            rec["live_pred_binary_matches"] = bool((df.live_pred_binary.to_numpy() == live).all())
            rec["live_label_matches"] = bool(
                (df.live_label.to_numpy() == np.where(live == 1, "RESISTANT", "SUSCEPTIBLE")).all())
            rec["confidence_matches"] = bool((df.confidence.to_numpy() == conf).all())
            rec["live_tp"] = int(((live == 1) & (y == 1)).sum())
            rec["live_tn"] = int(((live == 0) & (y == 0)).sum())
            rec["live_fp"] = int(((live == 1) & (y == 0)).sum())
            rec["live_fn"] = int(((live == 0) & (y == 1)).sum())
            rec["live_sensitivity"] = rec["live_tp"] / (rec["live_tp"] + rec["live_fn"])
            rec["live_specificity"] = rec["live_tn"] / (rec["live_tn"] + rec["live_fp"])
            rec["live_vme_rate"] = rec["live_fn"] / (rec["live_tp"] + rec["live_fn"])
            rec["live_me_rate"] = rec["live_fp"] / (rec["live_tn"] + rec["live_fp"])
            rec["live_flips_vs_fixed"] = int((live != pred).sum())
            rec["low_confidence_count"] = int((conf == "LOW").sum())
            rec["low_confidence_share"] = float((conf == "LOW").mean())
            rec["live_metrics_equal_fixed"] = (
                rec["live_tp"] == tp and rec["live_tn"] == tn
                and rec["live_fp"] == fp and rec["live_fn"] == fn)
        else:
            rec["adaptive_threshold_matches"] = False
            rec["live_pred_binary_matches"] = False
            rec["live_label_matches"] = False
            rec["confidence_matches"] = False
            rec["live_metrics_equal_fixed"] = False
            rec["low_confidence_count"] = None
            rec["low_confidence_share"] = None

        # Compare against the training-time summary written by the pipeline.
        with open(summary_path) as f:
            s = json.load(f)
        rec["summary_auc"] = s.get("roc_auc")
        rec["summary_accuracy"] = s.get("accuracy")
        rec["summary_n_test"] = int(s["n_test_resistant"] + s["n_test_susceptible"])
        rec["summary_R"] = int(s["n_test_resistant"])
        rec["summary_S"] = int(s["n_test_susceptible"])
        rec["auc_matches_summary"] = abs(auc - s["roc_auc"]) < 1e-6
        rec["acc_matches_summary"] = abs(acc - s["accuracy"]) < 1e-6
        rec["n_matches_summary"] = n == rec["summary_n_test"]
        rec["class_counts_match_summary"] = (rec["R"] == rec["summary_R"]
                                             and rec["S"] == rec["summary_S"])

        # Calibration scores are saved in test-split order; compare |y-p|.
        calib = np.load(calib_path)
        rec["calib_len"] = int(len(calib))
        if len(calib) == n:
            diff = np.abs(np.abs(y - p) - calib)
            rec["calib_max_abs_diff"] = float(diff.max())
            rec["calib_matches"] = bool(diff.max() < 1e-5)
        else:
            rec["calib_matches"] = False

        ok = (rec["auc_matches_summary"] and rec["acc_matches_summary"]
              and rec["n_matches_summary"] and rec["class_counts_match_summary"]
              and rec["calib_matches"] and rec["pred_binary_matches_prob"]
              and rec["live_rule_columns_present"]
              and rec["adaptive_threshold_matches"] and rec["live_pred_binary_matches"]
              and rec["live_label_matches"] and rec["confidence_matches"]
              and rec["live_metrics_equal_fixed"])
        rec["ALL_CHECKS_PASS"] = ok
        ok_all = ok_all and ok

        for i in range(5):
            pth = os.path.join("data", "models_v4", f"model_{ab}_model{i}.joblib")
            if os.path.exists(pth):
                out["model_sha256"][pth] = sha256(pth)
        for kind in ("vectorizer", "selector"):
            pth = os.path.join("data", "transformers_v4", f"{kind}_{ab}.joblib")
            if os.path.exists(pth):
                out["model_sha256"][pth] = sha256(pth)

        out["per_drug"][ab] = rec

    out["ALL_DRUGS_PASS"] = ok_all
    print(json.dumps(out, indent=2))
    with open("validation_results/regenerated_predictions_verification.json", "w") as f:
        json.dump(out, f, indent=2)

    # Also write the full three-drug manifest (the regeneration run may have
    # been split into per-drug invocations, leaving only the last drug in it).
    manifest = {
        "metrics": {
            ab: {**{k: r[k] for k in ("n", "R", "S", "tp", "tn", "fp", "fn",
                                      "predR", "auc", "accuracy", "sensitivity",
                                      "specificity", "ppv", "npv")},
                 "live": {k: r[k] for k in ("live_tp", "live_tn", "live_fp", "live_fn",
                                            "live_sensitivity", "live_specificity",
                                            "live_vme_rate", "live_me_rate",
                                            "live_flips_vs_fixed", "live_metrics_equal_fixed")},
                 "low_confidence_count": r["low_confidence_count"],
                 "low_confidence_share": r["low_confidence_share"]}
            for ab, r in out["per_drug"].items()
        },
        "model_sha256": out["model_sha256"],
        "threshold": 0.5,
        "live_rule": ("adaptive_threshold = 0.50 + min(uncertainty*0.5, 0.15); "
                      "confidence = HIGH if uncertainty<=0.05, MEDIUM if <=0.15, else LOW"),
        "note": ("Exact training test split reconstructed; original y_test was "
                 "never saved. Metrics recomputed from the CSVs only."),
        "verification": "validation_results/regenerated_predictions_verification.json",
    }
    with open("validation_results/regenerated_predictions_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("\nWROTE validation_results/regenerated_predictions_verification.json")
    print("WROTE validation_results/regenerated_predictions_manifest.json")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
