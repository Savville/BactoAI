"""
Re-save all model .joblib files with current library versions.

Model structure discovered:
  CalibratedClassifierCV
    -> _CalibratedClassifier x5 (one per CV fold)
       -> VotingClassifier (XGBClassifier, RandomForestClassifier, LGBMClassifier)

The XGBoost warning occurs because XGBClassifier inside was pickled with an older
XGBoost. Re-loading then re-dumping with the current versions clears the warning.

Usage (from project root):
    python scripts/resave_xgboost_models.py
"""

import os
import sys
import warnings

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

warnings.filterwarnings("ignore")

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import joblib
import xgboost as xgb
import sklearn

MODELS_DIR = os.path.join(project_root, "data", "models_v4")
ANTIBIOTICS = ["meropenem", "ciprofloxacin", "cefotaxime"]
NUM_ENSEMBLE_MODELS = 5


def resave_model(model_path):
    """
    Load a model, then immediately re-dump it with the current library versions.
    This refreshes the pickle metadata so XGBoost and sklearn no longer warn
    about version mismatches on the next load.
    """
    print(f"  Loading:  {os.path.basename(model_path)}")
    model = joblib.load(model_path)
    print(f"  Type:     {type(model).__name__}")

    # Re-dump to the same path with current versions
    joblib.dump(model, model_path, compress=3)
    print(f"  Re-saved: {os.path.basename(model_path)}")
    return True


def verify_no_warning(model_path):
    """Load the re-saved model and check no XGBoost warning fires."""
    import io
    import logging

    # Capture warnings
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        joblib.load(model_path)

    xgb_warns = [w for w in caught if "XGBoost" in str(w.message) or "xgboost" in str(w.category.__name__).lower()]
    return len(xgb_warns) == 0


def main():
    print(f"XGBoost version:  {xgb.__version__}")
    print(f"sklearn version:  {sklearn.__version__}")
    print(f"Models directory: {MODELS_DIR}")
    print()

    total = 0
    failed = []

    for antibiotic in ANTIBIOTICS:
        print(f"--- {antibiotic.upper()} ---")
        for idx in range(NUM_ENSEMBLE_MODELS):
            model_path = os.path.join(MODELS_DIR, f"model_{antibiotic}_model{idx}.joblib")
            if not os.path.exists(model_path):
                print(f"  [MISSING] {model_path}")
                continue
            total += 1
            try:
                resave_model(model_path)
                clean = verify_no_warning(model_path)
                status = "[CLEAN]" if clean else "[WARN - still has warning]"
                print(f"  {status}")
            except Exception as exc:
                print(f"  [ERROR] {exc}")
                failed.append(model_path)
            print()
        print()

    print(f"Done: {total} models processed, {len(failed)} errors.")
    if failed:
        print("Failed files:")
        for f in failed:
            print(f"  {f}")
    else:
        print()
        print("Next steps:")
        print("  git add data/models_v4/")
        print("  git commit -m 'chore: re-save models with current XGBoost + sklearn'")
        print("  git push   (Render will auto-deploy)")


if __name__ == "__main__":
    main()
