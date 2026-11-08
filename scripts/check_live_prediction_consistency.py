"""
Check that the live predict_single_antibiotic() path reproduces the
regenerated test-prediction CSVs.

Runs a sample of test isolates through the same code path used by the Flask
application (bactoai.models.prediction.predict_single_antibiotic) and compares
probability, adaptive threshold, live label and confidence against the CSV.

Writes validation_results/live_predict_consistency_check.json.
"""
import os, sys, json, warnings
import numpy as np
import pandas as pd
import joblib

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from bactoai.models.prediction import predict_single_antibiotic

FILES = {
    "meropenem": "validation_results/test_predictions_meropenem_v4.csv",
    "ciprofloxacin": "validation_results/test_predictions_ciprofloxacin_v4.csv",
    "cefotaxime": "validation_results/test_predictions_cefotaxime_v4.csv",
}


def genome_path(acc):
    for ext in (".fna", ".fna.gz"):
        p = os.path.join("data", "genomes", acc + ext)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    return None


def load_assets(ab):
    return {
        "vectorizer": joblib.load(f"data/transformers_v4/vectorizer_{ab}.joblib"),
        "selector": joblib.load(f"data/transformers_v4/selector_{ab}.joblib"),
        "models": [joblib.load(f"data/models_v4/model_{ab}_model{i}.joblib") for i in range(5)],
    }


def main(n=10):
    out = {
        "generated_at": "2026-11-08",
        "method": ("bactoai.models.prediction.predict_single_antibiotic() run on the first "
                   f"{n} rows of each regenerated test CSV, compared with the CSV values."),
        "versions": {},
        "per_drug": {},
    }
    import sklearn, xgboost, numpy, joblib as _joblib, lightgbm
    out["versions"] = {
        "scikit_learn_runtime": sklearn.__version__,
        "xgboost_runtime": xgboost.__version__,
        "numpy_runtime": numpy.__version__,
        "joblib_runtime": _joblib.__version__,
        "lightgbm_runtime": lightgbm.__version__,
        "declared_requirements": {
            "scikit_learn": "1.7.2",
            "xgboost": "3.2.0",
            "numpy": "2.4.2",
            "joblib": "1.5.3",
            "lightgbm": ">=4.0.0",
        },
        "training_version_evidence": {
            "scikit_learn": "1.7.2 recorded in the serialized estimator metadata",
            "xgboost": "Not confirmed; loading emits a serialized-model compatibility warning",
        },
    }
    ok_all = True
    for ab, csv_path in FILES.items():
        df = pd.read_csv(csv_path).head(n)
        # predict_single_antibiotic indexes assets[antibiotic], so pass a mapping
        # keyed by drug name containing only this drug's assets.
        assets = {ab: load_assets(ab)}
        diffs, thr_diffs, label_mismatch, conf_mismatch = [], [], 0, 0
        rows = []
        for _, r in df.iterrows():
            path = genome_path(r.asm_acc)
            if not path:
                continue
            pred = predict_single_antibiotic(ab, path, assets=assets)
            dp = abs(pred["probability"] - float(r.predicted_prob))
            dt = abs(pred["adaptive_threshold"] - float(r.adaptive_threshold))
            diffs.append(dp)
            thr_diffs.append(dt)
            if pred["label"] != r.live_label:
                label_mismatch += 1
            if pred["confidence"] != r.confidence:
                conf_mismatch += 1
            rows.append({
                "asm_acc": r.asm_acc,
                "csv_probability": float(r.predicted_prob),
                "live_probability": pred["probability"],
                "abs_diff": dp,
                "csv_live_label": r.live_label,
                "live_label": pred["label"],
                "csv_confidence": r.confidence,
                "live_confidence": pred["confidence"],
            })
        rec = {
            "n_checked": len(rows),
            "max_abs_probability_diff": float(max(diffs)) if diffs else None,
            "max_abs_threshold_diff": float(max(thr_diffs)) if thr_diffs else None,
            "label_mismatches": label_mismatch,
            "confidence_mismatches": conf_mismatch,
            "all_match": bool(label_mismatch == 0 and conf_mismatch == 0
                              and diffs and max(diffs) < 1e-5),
            "examples": rows[:5],
        }
        out["per_drug"][ab] = rec
        ok_all = ok_all and rec["all_match"]
    out["ALL_DRUGS_MATCH"] = ok_all
    with open("validation_results/live_predict_consistency_check.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
