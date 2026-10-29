"""
BactoAI — Bootstrap/Wilson 95% CIs for Q24
===========================================
Computes 95% confidence intervals from existing validation results.
Uses Wilson score intervals (exact for binomial proportions) and
Delta-method approximation for AUC.

Sources:
  - validation_results/threshold_audit_*.json (internal holdout)
  - validation_results/bvbrc_validation_summary_*.json (external BV-BRC)

Usage:
  .venv\\Scripts\\python.exe scripts/compute_q24_cis.py
"""
import os
import json
import math
import argparse
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "validation_results")


def wilson_ci(successes, total, z=1.96):
    """Wilson score confidence interval for a binomial proportion."""
    if total == 0:
        return float("nan"), float("nan")
    p_hat = successes / total
    denom = 1 + z**2 / total
    centre = (p_hat + z**2 / (2 * total)) / denom
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total)) / total) / denom
    return max(0, centre - spread), min(1, centre + spread)


def delta_auc_ci(auc, n, z=1.96):
    """Approximate 95% CI for AUC using the Delta method."""
    if auc <= 0.5 or auc >= 1.0 or n < 10:
        return auc, auc, auc
    # Hanley & McNeil approximation
    Q1 = auc / (2 - auc)
    Q2 = (2 * auc**2) / (1 + auc)
    snr = math.sqrt(auc * (1 - auc) + (n - 1) * (Q1 - auc**2) + (n - 1) * (Q2 - auc**2))
    se = snr / n
    return max(0, auc - z * se), auc, min(1, auc + z * se)


def load_threshold_audit(path):
    """Load internal holdout results."""
    with open(path) as f:
        data = json.load(f)
    results = {}
    for drug, info in data.items():
        ct = info.get("current_threshold", {})
        if not ct:
            continue
        tp = ct.get("tp", 0)
        tn = ct.get("tn", 0)
        fp = ct.get("fp", 0)
        fn = ct.get("fn", 0)
        n = tp + tn + fp + fn
        if n == 0:
            continue
        sens = tp / (tp + fn) if (tp + fn) > 0 else 0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0
        vme = fn / (fn + tp) if (fn + tp) > 0 else 0
        me = fp / (fp + tn) if (fp + tn) > 0 else 0
        auc = info.get("auc", 0)

        # Wilson CIs
        sens_lo, sens_hi = wilson_ci(tp, tp + fn)
        spec_lo, spec_hi = wilson_ci(tn, tn + fp)
        vme_lo, vme_hi = wilson_ci(fn, fn + tp)
        me_lo, me_hi = wilson_ci(fp, fp + tn)
        auc_lo, _, auc_hi = delta_auc_ci(auc, n)

        results[drug] = {
            "n": n, "threshold": ct.get("value", 0.5),
            "sens": sens, "sens_ci": (sens_lo, sens_hi),
            "spec": spec, "spec_ci": (spec_lo, spec_hi),
            "ppv": ppv, "npv": npv,
            "vme": vme, "vme_ci": (vme_lo, vme_hi),
            "me": me, "me_ci": (me_lo, me_hi),
            "auc": auc, "auc_ci": (auc_lo, auc_hi),
            "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "source": "internal_holdout",
        }
    return results


def load_bvbrc_validation(path):
    """Load external BV-BRC validation results."""
    with open(path) as f:
        data = json.load(f)
    results = {}
    # Handle both flat and nested structures
    def find_result(obj):
        if isinstance(obj, dict):
            if "confusion_matrix" in obj and "roc_auc" in obj:
                return obj
            for v in obj.values():
                r = find_result(v)
                if r:
                    return r
        return None

    info = find_result(data)
    if not info:
        return results

    cm = info.get("confusion_matrix", {})
    tp = cm.get("tp", 0)
    tn = cm.get("tn", 0)
    fp = cm.get("fp", 0)
    fn = cm.get("fn", 0)
    n = tp + tn + fp + fn
    if n == 0:
        return results

    auc = info.get("roc_auc", 0)
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    vme = fn / (fn + tp) if (fn + tp) > 0 else 0
    me = fp / (fp + tn) if (fp + tn) > 0 else 0

    sens_lo, sens_hi = wilson_ci(tp, tp + fn)
    spec_lo, spec_hi = wilson_ci(tn, tn + fp)
    vme_lo, vme_hi = wilson_ci(fn, fn + tp)
    me_lo, me_hi = wilson_ci(fp, fp + tn)
    auc_lo, _, auc_hi = delta_auc_ci(auc, n)

    drug = info.get("antibiotic", "unknown")
    results[drug] = {
        "n": n, "threshold": 0.20,  # BV-BRC used optimal threshold
        "sens": sens, "sens_ci": (sens_lo, sens_hi),
        "spec": spec, "spec_ci": (spec_lo, spec_hi),
        "ppv": ppv, "npv": npv,
        "vme": vme, "vme_ci": (vme_lo, vme_hi),
        "me": me, "me_ci": (me_lo, me_hi),
        "auc": auc, "auc_ci": (auc_lo, auc_hi),
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "source": "external_bvbrc",
    }
    return results


def generate_report(all_results, output_path):
    lines = []
    lines.append("# BactoAI — 95% Confidence Intervals (Q24)")
    lines.append(f"\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("**Method:** Wilson score intervals (exact for binomial proportions) + Delta method for AUC")
    lines.append("**Reference:** Hanley & McNeil (1982), Newcombe (1998)")
    lines.append("")

    for split_name, drug_results in all_results.items():
        lines.append(f"## {split_name}")
        lines.append("")
        lines.append("| Drug | n | Threshold | Sens | 95% CI | Spec | 95% CI | VME | ME | AUC | 95% CI |")
        lines.append("|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")

        for drug, r in drug_results.items():
            def pct(v): return f"{v:.1%}" if not math.isnan(v) else "N/A"
            def ci_str(lo, hi):
                if math.isnan(lo): return "N/A"
                return f"[{lo:.1%}, {hi:.1%}]"
            def auc_ci_str(lo, hi):
                if math.isnan(lo): return "N/A"
                return f"[{lo:.4f}, {hi:.4f}]"

            lines.append(
                f"| {drug} | {r['n']} | {r['threshold']} | "
                f"{pct(r['sens'])} | {ci_str(*r['sens_ci'])} | "
                f"{pct(r['spec'])} | {ci_str(*r['spec_ci'])} | "
                f"{pct(r['vme'])} | {pct(r['me'])} | "
                f"{r['auc']:.4f} | {auc_ci_str(*r['auc_ci'])} |"
            )
        lines.append("")

    # Summary table across all splits
    lines.append("## Complete Summary")
    lines.append("")
    lines.append("| Drug | Source | n | Sens | 95% CI | Spec | 95% CI | AUC | 95% CI |")
    lines.append("|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")

    for split_name, drug_results in all_results.items():
        for drug, r in drug_results.items():
            def pct(v): return f"{v:.1%}" if not math.isnan(v) else "N/A"
            def ci_str(lo, hi):
                if math.isnan(lo): return "N/A"
                return f"[{lo:.1%}, {hi:.1%}]"
            def auc_ci_str(lo, hi):
                if math.isnan(lo): return "N/A"
                return f"[{lo:.4f}, {hi:.4f}]"

            lines.append(
                f"| {drug} | {r['source']} | {r['n']} | "
                f"{pct(r['sens'])} | {ci_str(*r['sens_ci'])} | "
                f"{pct(r['spec'])} | {ci_str(*r['spec_ci'])} | "
                f"{r['auc']:.4f} | {auc_ci_str(*r['auc_ci'])} |"
            )
    lines.append("")

    lines.append("---")
    lines.append("*Wilson score intervals are recommended for binomial proportions (sensitivity, specificity) as they maintain correct coverage even with small samples. AUC CIs use the DeLong/Hanley-McNeil delta method approximation.*")
    lines.append(f"*Computed: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    report = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(report)
    return report


def main():
    parser = argparse.ArgumentParser(description="Compute 95% CIs for BactoAI validation (Q24)")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    print("=" * 70)
    print("  BACTOAI — 95% CONFIDENCE INTERVALS (Q24)")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    all_results = {}

    # Load internal holdout (threshold audit)
    audit_paths = [
        os.path.join(RESULTS_DIR, "threshold_audit_20260912_165224.json"),
        os.path.join(RESULTS_DIR, "threshold_audit_20260912_162504.json"),
    ]
    for path in audit_paths:
        if os.path.exists(path):
            results = load_threshold_audit(path)
            if results:
                all_results["Internal Holdout (threshold audit)"] = results
                print(f"\n  Loaded: {os.path.basename(path)}")
                for drug, r in results.items():
                    print(f"    {drug}: n={r['n']}, Sens={r['sens']:.1%}, Spec={r['spec']:.1%}, AUC={r['auc']:.4f}")
                break

    # Load external BV-BRC validation
    bvbrc_paths = [
        os.path.join(RESULTS_DIR, "bvbrc_validation_summary_20260914_070116.json"),
        os.path.join(RESULTS_DIR, "bvbrc_validation_summary_20260914_003725.json"),
    ]
    for path in bvbrc_paths:
        if os.path.exists(path):
            results = load_bvbrc_validation(path)
            if results:
                all_results["External Validation (BV-BRC)"] = results
                print(f"\n  Loaded: {os.path.basename(path)}")
                for drug, r in results.items():
                    print(f"    {drug}: n={r['n']}, Sens={r['sens']:.1%}, Spec={r['spec']:.1%}, AUC={r['auc']:.4f}")
                break

    if not all_results:
        print("\nERROR: No validation results found.")
        print(f"  Expected files in: {RESULTS_DIR}")
        return

    # Generate report
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = args.output or os.path.join(RESULTS_DIR, f"q24_ci_report_{ts}.md")
    report = generate_report(all_results, output_path)
    print(f"\n  Report: {output_path}")
    print("\n" + report)

    # Save raw JSON
    json_path = os.path.join(RESULTS_DIR, f"q24_ci_{ts}.json")
    serializable = {}
    for split, drugs in all_results.items():
        serializable[split] = {}
        for drug, r in drugs.items():
            serializable[split][drug] = {k: (float(v) if isinstance(v, (float,)) else v) for k, v in r.items()}
    with open(json_path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"  JSON:   {json_path}")


if __name__ == "__main__":
    main()
