"""
BactoAI — Bootstrap Confidence Intervals for Validation Metrics
================================================================
Re-runs validation on existing test data and computes 95% CIs via bootstrap.

Usage:
  .venv\\Scripts\\python.exe scripts/compute_ci.py
  .venv\\Scripts\\python.exe scripts/compute_ci.py --output validation_results/bootstrap_ci_report.md
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.metrics import roc_auc_score, confusion_matrix

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from bactoai_pipeline import (
    build_kmers, extract_gene_signatures, read_fasta,
    get_adaptive_threshold, get_confidence_level,
)

# =====================================================================
# Paths
# =====================================================================
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
TRANSFORMERS_DIR = os.path.join(DATA_DIR, "transformers_v4")
MODELS_DIR = os.path.join(DATA_DIR, "models_v4")
TEST_GENOMES_DIR = os.path.join(DATA_DIR, "test_genomes")
GENOMES_DIR = os.path.join(DATA_DIR, "genomes")

ANTIBIOTIC_ORDER = ["meropenem", "ciprofloxacin", "cefotaxime"]
KMER_SIZE = 5
NUM_ENSEMBLE = 5
N_BOOTSTRAP = 2000
RANDOM_STATE = 42

# =====================================================================
# Load Models
# =====================================================================

def load_models():
    """Load all prediction models and transformers."""
    import joblib
    assets = {}
    for ab in ANTIBIOTIC_ORDER:
        vec_path = os.path.join(TRANSFORMERS_DIR, f"vectorizer_{ab}.joblib")
        sel_path = os.path.join(TRANSFORMERS_DIR, f"selector_{ab}.joblib")
        models = []
        for i in range(NUM_ENSEMBLE):
            mpath = os.path.join(MODELS_DIR, f"model_{ab}_model{i}.joblib")
            if os.path.exists(mpath):
                models.append(joblib.load(mpath))
        if not models:
            raise FileNotFoundError(f"No models for {ab}")
        assets[ab] = {
            "vectorizer": joblib.load(vec_path),
            "selector": joblib.load(sel_path),
            "models": models,
        }
    return assets


def predict_single(antibiotic, genome_path, assets):
    """Run prediction for one antibiotic on a genome."""
    asset = assets[antibiotic]
    sequence = read_fasta(genome_path)
    if not sequence:
        return None
    
    kmer_string = build_kmers(sequence, KMER_SIZE)
    gene_row = extract_gene_signatures(sequence)
    gene_values = np.array(list(gene_row.values()), dtype=np.float64).reshape(1, -1)
    
    X_kmers = asset["vectorizer"].transform([kmer_string])
    from scipy.sparse import csr_matrix, hstack
    X_combined = hstack([X_kmers, csr_matrix(gene_values)])
    X = asset["selector"].transform(X_combined)
    
    probabilities = np.array(
        [model.predict_proba(X)[0][1] for model in asset["models"]], dtype=float
    )
    mean_prob = float(probabilities.mean())
    return mean_prob


# =====================================================================
# Load Test Data
# =====================================================================

def load_test_data():
    """Load test set metadata and return {drug: (y_true, y_prob, genomes)}."""
    import joblib
    
    assets = load_models()
    results = {}
    
    for ab in ANTIBIOTIC_ORDER:
        meta_path = os.path.join(DATA_DIR, f"metadata_{ab}.csv")
        if not os.path.exists(meta_path):
            print(f"  Missing: {meta_path}")
            continue
        
        df = pd.read_csv(meta_path)
        df = df.dropna(subset=["asm_acc", "resistant"]).drop_duplicates(subset="asm_acc")
        
        # Find test genomes (those in test_genomes directory)
        test_files = set(os.listdir(TEST_GENOMES_DIR)) if os.path.exists(TEST_GENOMES_DIR) else set()
        
        y_true = []
        y_prob = []
        sample_ids = []
        
        for _, row in df.iterrows():
            acc = row["asm_acc"]
            label = int(row["resistant"])
            fasta_file = f"{acc}.fna"
            gz_file = f"{acc}.fna.gz"
            
            # Find the genome file
            genome_path = None
            for candidate in [fasta_file, gz_file]:
                # Check test dir first, then main genomes dir
                for d in [TEST_GENOMES_DIR, GENOMES_DIR]:
                    p = os.path.join(d, candidate)
                    if os.path.exists(p):
                        genome_path = p
                        break
                if genome_path:
                    break
            
            if genome_path is None:
                continue
            
            prob = predict_single(ab, genome_path, assets)
            if prob is None:
                continue
            
            y_true.append(label)
            y_prob.append(prob)
            sample_ids.append(acc)
        
        if len(y_true) > 1:
            results[ab] = {
                "y_true": np.array(y_true),
                "y_prob": np.array(y_prob),
                "sample_ids": sample_ids,
                "n": len(y_true),
            }
            print(f"  {ab}: loaded {len(y_true)} test samples")
        else:
            print(f"  {ab}: only {len(y_true)} samples found, skipping")
    
    return results, assets


# =====================================================================
# Bootstrap CI
# =====================================================================

def bootstrap_ci_binomial(successes, total, n_boot=2000, conf=0.95, rng=None):
    """Bootstrap CI for a binomial proportion."""
    if rng is None:
        rng = np.random.default_rng(RANDOM_STATE)
    if total == 0:
        return {"point": np.nan, "ci_lower": np.nan, "ci_upper": np.nan}
    
    p_hat = successes / total
    boot_probs = []
    for _ in range(n_boot):
        s = rng.binomial(total, p_hat)
        boot_probs.append(s / total)
    
    alpha = 1 - conf
    return {
        "point": float(p_hat),
        "ci_lower": float(np.percentile(boot_probs, 100 * alpha / 2)),
        "ci_upper": float(np.percentile(boot_probs, 100 * (1 - alpha / 2))),
    }


def compute_all_metrics(y_true, y_prob, threshold=0.5):
    """Compute all metrics for a single threshold."""
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    sens = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    spec = tn / (tn + fp) if (tn + fp) > 0 else np.nan
    ppv = tp / (tp + fp) if (tp + fp) > 0 else np.nan
    npv = tn / (tn + fn) if (tn + fn) > 0 else np.nan
    acc = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else np.nan
    vme = fn / (fn + tp) if (fn + tp) > 0 else np.nan
    me = fp / (fp + tn) if (fp + tn) > 0 else np.nan
    auc = roc_auc_score(y_true, y_prob) if len(set(y_true)) > 1 else np.nan
    
    return {
        "n": len(y_true),
        "threshold": threshold,
        "sens": sens, "spec": spec, "ppv": ppv, "npv": npv,
        "acc": acc, "vme": vme, "me": me, "auc": auc,
        "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
    }


def bootstrap_validation(y_true, y_prob, n_boot=N_BOOTSTRAP, random_state=RANDOM_STATE):
    """Compute bootstrap CIs for all metrics."""
    rng = np.random.default_rng(random_state)
    
    # Base metrics
    base = compute_all_metrics(y_true, y_prob)
    
    # Bootstrap sensitivity (conditional on positive cases)
    pos_idx = np.where(y_true == 1)[0]
    if len(pos_idx) > 0:
        def sens_fn(idx):
            yt = y_true[idx]
            yp = y_prob[idx]
            pred = (yp >= base["threshold"]).astype(int)
            tp = ((pred == 1) & (yt == 1)).sum()
            fn = ((pred == 0) & (yt == 1)).sum()
            return tp / (tp + fn) if (tp + fn) > 0 else np.nan
        
        ci_sens = bootstrap_ci_from_function(pos_idx, sens_fn, n_boot, rng)
        base["sens_ci"] = ci_sens
    else:
        base["sens_ci"] = {"point": np.nan, "ci_lower": np.nan, "ci_upper": np.nan}
    
    # Bootstrap specificity (conditional on negative cases)
    neg_idx = np.where(y_true == 0)[0]
    if len(neg_idx) > 0:
        def spec_fn(idx):
            yt = y_true[idx]
            yp = y_prob[idx]
            pred = (yp >= base["threshold"]).astype(int)
            tn = ((pred == 0) & (yt == 0)).sum()
            fp = ((pred == 1) & (yt == 0)).sum()
            return tn / (tn + fp) if (tn + fp) > 0 else np.nan
        
        ci_spec = bootstrap_ci_from_function(neg_idx, spec_fn, n_boot, rng)
        base["spec_ci"] = ci_spec
    else:
        base["spec_ci"] = {"point": np.nan, "ci_lower": np.nan, "ci_upper": np.nan}
    
    # Bootstrap AUC
    if len(set(y_true)) > 1:
        all_idx = np.arange(len(y_true))
        def auc_fn(idx):
            return roc_auc_score(y_true[idx], y_prob[idx])
        
        ci_auc = bootstrap_ci_from_function(all_idx, auc_fn, n_boot, rng)
        base["auc_ci"] = ci_auc
    else:
        base["auc_ci"] = {"point": np.nan, "ci_lower": np.nan, "ci_upper": np.nan}
    
    return base


def bootstrap_ci_from_function(indices, stat_fn, n_boot, rng):
    """Generic bootstrap CI for any statistic."""
    n = len(indices)
    boot_stats = []
    for _ in range(n_boot):
        sample_idx = rng.choice(indices, size=n, replace=True)
        stat = stat_fn(sample_idx)
        if np.isfinite(stat):
            boot_stats.append(stat)
    
    if not boot_stats:
        return {"point": np.nan, "ci_lower": np.nan, "ci_upper": np.nan}
    
    boot_stats = np.array(boot_stats)
    return {
        "point": float(stat_fn(indices)),
        "ci_lower": float(np.percentile(boot_stats, 2.5)),
        "ci_upper": float(np.percentile(boot_stats, 97.5)),
    }


# =====================================================================
# Report
# =====================================================================

def generate_report(all_results, output_path):
    """Generate markdown report with bootstrap CIs."""
    lines = []
    lines.append("# BactoAI — Bootstrap Confidence Intervals")
    lines.append(f"\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Method:** Non-parametric bootstrap, {N_BOOTSTRAP} resamples, 95% CI")
    lines.append(f"**Random seed:** {RANDOM_STATE}")
    lines.append("")
    
    for drug, result in all_results.items():
        lines.append(f"## {drug.capitalize()}")
        lines.append("")
        lines.append(f"| Metric | Value | 95% CI |")
        lines.append(f"|:---|:---:|:---:|")
        
        # Sensitivity
        sens = result.get("sens", np.nan)
        sens_ci = result.get("sens_ci", {})
        sens_ci_str = f"[{sens_ci.get('ci_lower', np.nan):.1%}, {sens_ci.get('ci_upper', np.nan):.1%}]" if not np.isnan(sens_ci.get('ci_lower', np.nan)) else "N/A"
        lines.append(f"| Sensitivity | {sens:.1%} | {sens_ci_str} |")
        
        # Specificity
        spec = result.get("specificity", result.get("spec", np.nan))
        spec_ci = result.get("spec_ci", {})
        spec_ci_str = f"[{spec_ci.get('ci_lower', np.nan):.1%}, {spec_ci.get('ci_upper', np.nan):.1%}]" if not np.isnan(spec_ci.get('ci_lower', np.nan)) else "N/A"
        lines.append(f"| Specificity | {spec:.1%} | {spec_ci_str} |")
        
        # PPV
        ppv = result.get("ppv", np.nan)
        lines.append(f"| PPV | {ppv:.1%} | — |")
        
        # NPV
        npv = result.get("npv", np.nan)
        lines.append(f"| NPV | {npv:.1%} | — |")
        
        # VME
        vme = result.get("vme", np.nan)
        lines.append(f"| VME rate | {vme:.1%} | — |")
        
        # ME
        me = result.get("me", np.nan)
        lines.append(f"| ME rate | {me:.1%} | — |")
        
        # AUC
        auc = result.get("auc", np.nan)
        auc_ci = result.get("auc_ci", {})
        auc_ci_str = f"[{auc_ci.get('ci_lower', np.nan):.4f}, {auc_ci.get('ci_upper', np.nan):.4f}]" if not np.isnan(auc_ci.get('ci_lower', np.nan)) else "N/A"
        lines.append(f"| AUC | {auc:.4f} | {auc_ci_str} |")
        
        # Confusion matrix
        lines.append(f"\n**Confusion matrix (threshold={result.get('threshold', 0.5)}):**")
        lines.append(f"  TP={result.get('tp', 'N/A')}  TN={result.get('tn', 'N/A')}  FP={result.get('fp', 'N/A')}  FN={result.get('fn', 'N/A')}")
        lines.append(f"  n={result.get('n', 'N/A')}")
        lines.append("")
    
    # Summary table
    lines.append("## Summary Table")
    lines.append("")
    lines.append("| Drug | n | Sens | 95% CI | Spec | 95% CI | AUC | 95% CI |")
    lines.append("|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
    
    for drug, result in all_results.items():
        sens = result.get("sens", np.nan)
        spec = result.get("spec", result.get("specificity", np.nan))
        auc = result.get("auc", np.nan)
        n = result.get("n", "N/A")
        
        sens_ci = result.get("sens_ci", {})
        spec_ci = result.get("spec_ci", {})
        auc_ci = result.get("auc_ci", {})
        
        sens_ci_str = f"[{sens_ci.get('ci_lower', np.nan):.0%}, {sens_ci.get('ci_upper', np.nan):.0%}]" if not np.isnan(sens_ci.get('ci_lower', np.nan)) else "—"
        spec_ci_str = f"[{spec_ci.get('ci_lower', np.nan):.0%}, {spec_ci.get('ci_upper', np.nan):.0%}]" if not np.isnan(spec_ci.get('ci_lower', np.nan)) else "—"
        auc_ci_str = f"[{auc_ci.get('ci_lower', np.nan):.3f}, {auc_ci.get('ci_upper', np.nan):.3f}]" if not np.isnan(auc_ci.get('ci_lower', np.nan)) else "—"
        
        lines.append(f"| {drug} | {n} | {sens:.1%} | {sens_ci_str} | {spec:.1%} | {spec_ci_str} | {auc:.4f} | {auc_ci_str} |")
    
    lines.append("")
    lines.append("---")
    lines.append("*Computed with bootstrap resampling (2000 iterations, seed=42). Sensitivity and specificity CIs are conditional on the respective class. AUC CI is computed over all samples.*")
    
    report = "\n".join(lines)
    
    with open(output_path, "w") as f:
        f.write(report)
    
    return report


# =====================================================================
# Main
# =====================================================================

def main():
    print("=" * 70)
    print("  BACTOAI — BOOTSTRAP CONFIDENCE INTERVALS")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    # Load test data
    print("\n[1] Loading test data and models...")
    try:
        results, assets = load_test_data()
    except Exception as e:
        print(f"  [ERROR] Failed to load test data: {e}")
        print("  Make sure test genomes exist in data/test_genomes/ and models in data/models_v4/")
        sys.exit(1)
    
    if not results:
        print("  No test data found. Run the pipeline to generate test sets first.")
        sys.exit(1)
    
    # Compute bootstrap CIs
    print(f"\n[2] Computing bootstrap CIs ({N_BOOTSTRAP} resamples)...")
    ci_results = {}
    
    for drug, data in results.items():
        print(f"\n  {drug} (n={data['n']})...")
        ci = bootstrap_validation(data["y_true"], data["y_prob"])
        ci_results[drug] = ci
        
        print(f"    Sens: {ci['sens']:.1%}  Spec: {ci.get('spec', ci.get('specificity', 0)):.1%}  AUC: {ci['auc']:.4f}")
        if "sens_ci" in ci:
            print(f"    Sens CI95: [{ci['sens_ci']['ci_lower']:.1%}, {ci['sens_ci']['ci_upper']:.1%}]")
        if "spec_ci" in ci:
            print(f"    Spec CI95: [{ci['spec_ci']['ci_lower']:.1%}, {ci['spec_ci']['ci_upper']:.1%}]")
        if "auc_ci" in ci:
            print(f"    AUC CI95:  [{ci['auc_ci']['ci_lower']:.4f}, {ci['auc_ci']['ci_upper']:.4f}]")
    
    # Generate report
    output_dir = os.path.join(PROJECT_ROOT, "validation_results")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"bootstrap_ci_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    report = generate_report(ci_results, output_path)
    print(f"\n[3] Report saved to: {output_path}")
    print("\n" + report)


if __name__ == "__main__":
    main()
