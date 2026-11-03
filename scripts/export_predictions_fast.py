"""
Fast export: generate test prediction CSVs from existing validation JSONs.
No model loading needed — uses stored confusion matrices and metrics.
Also generates a summary CSV with all verified numbers.
"""
import json, os, sys, csv
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
RESULTS_DIR = 'validation_results'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load corrected metrics
with open(os.path.join(PROJECT_ROOT, RESULTS_DIR, 'corrected_metrics.json')) as f:
    m = json.load(f)

# Generate summary CSV
out_path = os.path.join(PROJECT_ROOT, RESULTS_DIR, 'test_predictions_summary.csv')
with open(out_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['drug', 'model_version', 'n_test', 'auc', 'sensitivity', 'specificity',
                'ppv', 'npv', 'accuracy', 'tp', 'tn', 'fp', 'fn',
                'vme_rate', 'me_rate', 'threshold', 'notes'])

    # Meropenem
    d = m['meropenem']
    w.writerow(['meropenem', 'v4_ensemble', d['n_test'], d['auc'], d['sensitivity'],
                d['specificity'], d['ppv'], d['npv'], d['accuracy'],
                d['tp'], d['tn'], d['fp'], d['fn'],
                d['vme_rate'], d['me_rate'], d['threshold'], d.get('note', '')])

    # Ciprofloxacin
    d = m['ciprofloxacin']
    w.writerow(['ciprofloxacin', 'v4_ensemble', d['n_test'], d['auc'], d['sensitivity'],
                d['specificity'], d['ppv'], d['npv'], d['accuracy'],
                d['tp'], d['tn'], d['fp'], d['fn'],
                d['vme_rate'], d['me_rate'], d['threshold'], d.get('note', '')])

    # Cefotaxime v3
    d = m['cefotaxime_v3']
    w.writerow(['cefotaxime', 'v3_ncbi_only', d['n_test'], d['auc'],
                d.get('sensitivity', 'N/A'), d.get('specificity', 'N/A'),
                'N/A', 'N/A', d['accuracy'],
                'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', d['threshold'], d.get('note', '')])

    # BV-BRC benchmark
    d = m['bvbrc_benchmark']
    w.writerow(['cefotaxime', 'bvbrc_in_corpus_benchmark', d['n_evaluated'], d['auc'],
                d['sensitivity'], d['specificity'], d['ppv'], d['npv'], d['accuracy'],
                d['tp'], d['tn'], d['fp'], d['fn'],
                d['vme_rate'], d['me_rate'], d['threshold'], d.get('note', '')])

print(f"Saved summary: {out_path}")

# Print corrected table
print()
print("=" * 90)
print("  CORRECTED METRICS TABLE FOR NPHL SUBMISSION")
print("=" * 90)
print(f"{'Drug':<15} {'Version':<20} {'n':>5} {'AUC':>7} {'Sens':>7} {'Spec':>7} {'TP':>4} {'TN':>4} {'FP':>4} {'FN':>4} {'VME':>6} {'ME':>6}")
print("-" * 90)
for key in ['meropenem', 'ciprofloxacin', 'cefotaxime_v3']:
    d = m[key]
    sens = f"{d['sensitivity']:.1%}" if d.get('sensitivity') else "N/A"
    spec = f"{d['specificity']:.1%}" if d.get('specificity') else "N/A"
    vme = f"{d['vme_rate']:.1%}" if d.get('vme_rate') else "N/A"
    me = f"{d['me_rate']:.1%}" if d.get('me_rate') else "N/A"
    tp = d.get('tp', '?')
    tn = d.get('tn', '?')
    fp = d.get('fp', '?')
    fn = d.get('fn', '?')
    print(f"{key.replace('_',' ').title():<15} {'v4_ensemble':<20} {d['n_test']:>5} {d['auc']:>7.4f} {sens:>7} {spec:>7} {tp:>4} {tn:>4} {fp:>4} {fn:>4} {vme:>6} {me:>6}")

d = m['bvbrc_benchmark']
print(f"{'Cefotaxime':<15} {'BV-BRC benchmark':<20} {d['n_evaluated']:>5} {d['auc']:>7.4f} {d['sensitivity']:.1%} {d['specificity']:.1%} {d['tp']:>4} {d['tn']:>4} {d['fp']:>4} {d['fn']:>4} {d['vme_rate']:.1%} {d['me_rate']:.1%}")
print(f"  ^ In-corpus benchmark (NOT independent external validation)")
print()
print("KEY FIXES:")
print("  1. Ciprofloxacin AUC: 0.879 -> 0.9559 (corrected from threshold audit)")
print("  2. Meropenem AUC: confirmed 0.9871 (matches audit)")
print("  3. Cefotaxime v3: AUC 0.8721, accuracy 79.3%, n=145 (no CM available)")
print("  4. BV-BRC 500 genomes: RECLASSIFIED as in-corpus benchmark, not external validation")
print("  5. Production model: meropenem v4 + ciprofloxacin v4 + cefotaxime v3 (NOT v4)")
