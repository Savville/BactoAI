"""
Regenerate the three test-split prediction CSVs from the deployed assets.

The original training script (bactoai_pipeline.py) never saved y_test, so the
split is reconstructed deterministically:
    dropna -> drop_duplicates -> sample(frac=1, random_state=42)
    -> drop missing/empty genomes -> train_test_split(0.25, 42, stratify)
This reproduces the exact n_test and class counts recorded in
data/models_v4/summary_*.json and the lengths of calibration_scores_*.npy.
"""
import os, sys, json, time, hashlib, argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import pandas as pd
import joblib
from scipy.sparse import csr_matrix, hstack
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

sys.stdout.reconfigure(line_buffering=True)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from bactoai_pipeline import build_kmers, extract_gene_signatures, read_fasta

DATA = "data"
GEN = os.path.join(DATA, "genomes")
MODELS = os.path.join(DATA, "models_v4")
TRANS = os.path.join(DATA, "transformers_v4")
OUT = "validation_results"
KMER = 5
NUM = 5
THRESH = 0.5

DRUGS = {
    "meropenem":     dict(out="test_predictions_meropenem_v4.csv",     expect_n=124, expect_R=70, version="v4_ensemble"),
    "ciprofloxacin": dict(out="test_predictions_ciprofloxacin_v4.csv", expect_n=143, expect_R=70, version="v4_ensemble"),
    "cefotaxime":    dict(out="test_predictions_cefotaxime_v4.csv",    expect_n=145, expect_R=71, version="v4_ncbi_only"),
}

_ASSET = None
_AB = None

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def genome_path(acc):
    for ext in (".fna", ".fna.gz"):
        p = os.path.join(GEN, acc + ext)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    return None

def split_for(ab):
    df = pd.read_csv(os.path.join(DATA, f"metadata_{ab}.csv"))
    df = df.dropna(subset=["asm_acc", "resistant"]).drop_duplicates(subset="asm_acc").copy()
    df["resistant"] = df["resistant"].astype(int)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df["genome_path"] = df.asm_acc.map(genome_path)
    df = df[df.genome_path.notna()].reset_index(drop=True)
    y = df.resistant.values
    idx = np.arange(len(df))
    tr, te = train_test_split(idx, test_size=0.25, random_state=42, stratify=y)
    return df.iloc[te].reset_index(drop=True)

def load_assets(ab):
    models = []
    files = []
    for i in range(NUM):
        p = os.path.join(MODELS, f"model_{ab}_model{i}.joblib")
        if os.path.exists(p):
            models.append(joblib.load(p)); files.append(p)
    vec_p = os.path.join(TRANS, f"vectorizer_{ab}.joblib")
    sel_p = os.path.join(TRANS, f"selector_{ab}.joblib")
    return dict(vectorizer=joblib.load(vec_p), selector=joblib.load(sel_p),
                models=models, files=files + [vec_p, sel_p])

def _init_worker(ab):
    global _ASSET, _AB
    _AB = ab
    _ASSET = load_assets(ab)

def _predict_one(item):
    acc, path = item
    seq = read_fasta(path)
    if not seq:
        return acc, None, None
    kmer = build_kmers(seq, KMER)
    gene = extract_gene_signatures(seq)
    gv = np.array(list(gene.values()), dtype=np.float64).reshape(1, -1)
    Xk = _ASSET["vectorizer"].transform([kmer])
    X = _ASSET["selector"].transform(hstack([Xk, csr_matrix(gv)]))
    probs = np.array([m.predict_proba(X)[0][1] for m in _ASSET["models"]], dtype=float)
    return acc, float(probs.mean()), float(probs.std())

def compute(df):
    tp = int(((df.pred_binary == 1) & (df.true_label == 1)).sum())
    tn = int(((df.pred_binary == 0) & (df.true_label == 0)).sum())
    fp = int(((df.pred_binary == 1) & (df.true_label == 0)).sum())
    fn = int(((df.pred_binary == 0) & (df.true_label == 1)).sum())
    n = len(df)
    sens = tp/(tp+fn) if tp+fn else None
    spec = tn/(tn+fp) if tn+fp else None
    live = df.live_pred_binary
    ltp = int(((live == 1) & (df.true_label == 1)).sum())
    ltn = int(((live == 0) & (df.true_label == 0)).sum())
    lfp = int(((live == 1) & (df.true_label == 0)).sum())
    lfn = int(((live == 0) & (df.true_label == 1)).sum())
    return dict(n=n, R=int((df.true_label == 1).sum()), S=int((df.true_label == 0).sum()),
                tp=tp, tn=tn, fp=fp, fn=fn,
                auc=float(roc_auc_score(df.true_label, df.predicted_prob)),
                accuracy=(tp+tn)/n, sensitivity=sens, specificity=spec,
                ppv=tp/(tp+fp) if tp+fp else None, npv=tn/(tn+fn) if tn+fn else None,
                predR=int((df.pred_binary == 1).sum()),
                live=dict(tp=ltp, tn=ltn, fp=lfp, fn=lfn,
                          sensitivity=ltp/(ltp+lfn) if ltp+lfn else None,
                          specificity=ltn/(ltn+lfp) if ltn+lfp else None,
                          accuracy=(ltp+ltn)/n,
                          flips_vs_fixed=int((live != df.pred_binary).sum())))


def confidence_level(std):
    if std <= 0.05:
        return "HIGH"
    if std <= 0.15:
        return "MEDIUM"
    return "LOW"


def adaptive_threshold(std):
    return 0.50 + min(std * 0.5, 0.15)


def fmt(v, nd=4):
    return "N/A" if v is None else f"{v:.{nd}f}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drug", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    args = ap.parse_args()

    drugs = [args.drug] if args.drug else list(DRUGS)
    manifest = {}
    all_metrics = {}
    for ab in drugs:
        t0 = time.time()
        cfg = DRUGS[ab]
        test = split_for(ab)
        assert len(test) == cfg["expect_n"], (ab, len(test))
        assert int((test.resistant == 1).sum()) == cfg["expect_R"], (ab, int((test.resistant == 1).sum()))
        print(f"\n=== {ab}: reconstructed test n={len(test)} R={int((test.resistant==1).sum())} S={int((test.resistant==0).sum())} ===", flush=True)

        asset_files = [os.path.join(MODELS, f"model_{ab}_model{i}.joblib") for i in range(NUM)]
        asset_files += [os.path.join(TRANS, f"vectorizer_{ab}.joblib"), os.path.join(TRANS, f"selector_{ab}.joblib")]
        manifest[ab] = {os.path.relpath(p, ROOT): sha256(p) for p in asset_files if os.path.exists(p)}

        todo = test if args.limit is None else test.head(args.limit)
        items = list(zip(todo.asm_acc, todo.genome_path))
        results = {}
        with ProcessPoolExecutor(max_workers=args.workers, initializer=_init_worker, initargs=(ab,)) as ex:
            futs = {ex.submit(_predict_one, it): it[0] for it in items}
            done = 0
            for fut in as_completed(futs):
                acc, prob, std = fut.result()
                results[acc] = (prob, std)
                done += 1
                if done % 10 == 0 or done == len(items):
                    print(f"  {done}/{len(items)}  elapsed {time.time()-t0:.1f}s", flush=True)

        rows = []
        for _, row in todo.iterrows():
            prob, std = results.get(row.asm_acc, (None, None))
            if prob is None:
                print(f"  SKIP unreadable {row.asm_acc}"); continue
            thr = adaptive_threshold(std)
            rows.append(dict(asm_acc=row.asm_acc, true_label=int(row.resistant),
                             predicted_prob=round(prob, 6), pred_binary=int(prob >= THRESH),
                             ensemble_std=round(std, 6), uncertainty=round(std, 6),
                             adaptive_threshold=round(thr, 6),
                             live_pred_binary=int(prob >= thr),
                             live_label="RESISTANT" if prob >= thr else "SUSCEPTIBLE",
                             confidence=confidence_level(std),
                             lower_bound=round(max(0.0, prob - 1.96 * std), 6),
                             upper_bound=round(min(1.0, prob + 1.96 * std), 6),
                             antibiotic=ab, model_version=DRUGS[ab]["version"]))
        df = pd.DataFrame(rows)
        m = compute(df)
        all_metrics[ab] = m
        print(f"  METRICS n={m['n']} R={m['R']} S={m['S']} TP={m['tp']} TN={m['tn']} FP={m['fp']} FN={m['fn']} "
              f"AUC={m['auc']:.6f} Acc={m['accuracy']:.4f} Sens={fmt(m['sensitivity'])} Spec={fmt(m['specificity'])}", flush=True)

        if args.limit is None:
            out_path = os.path.join(OUT, cfg["out"])
            df.to_csv(out_path, index=False)
            print(f"  WROTE {out_path}")
            split_path = os.path.join(OUT, f"test_split_{ab}.csv")
            test[["asm_acc", "resistant"]].rename(columns={"resistant": "true_label"}).to_csv(split_path, index=False)
            print(f"  WROTE {split_path}")

    if args.limit is None:
        flat_hashes = {}
        for d in manifest.values():
            flat_hashes.update(d)
        with open(os.path.join(OUT, "regenerated_predictions_manifest.json"), "w") as f:
            json.dump({"metrics": all_metrics, "model_sha256": flat_hashes,
                       "threshold": THRESH,
                       "live_rule": "adaptive_threshold = 0.50 + min(uncertainty*0.5, 0.15); "
                                    "confidence = HIGH if uncertainty<=0.05, MEDIUM if <=0.15, else LOW",
                       "note": "Exact training test split reconstructed; original y_test was never saved."}, f, indent=2)
        print("\nWROTE validation_results/regenerated_predictions_manifest.json")

if __name__ == "__main__":
    main()
