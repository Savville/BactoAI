"""
BactoAI Pipeline v2 — Multi-Antibiotic, Multi-Species Resistance Predictor
============================================================================
Trains one XGBoost model per antibiotic (meropenem, ciprofloxacin, cefotaxime).
Reports accuracy, ROC-AUC, recall by species and antibiotic.
Saves each trained model to data/models/.

Usage:
    python bactoai_pipeline_v2.py --train
    python bactoai_pipeline_v2.py --train --antibiotic meropenem
    python bactoai_pipeline_v2.py --predict --fasta path/to/genome.fna
"""

import os
import gzip
import argparse
import numpy as np
import pandas as pd
from Bio import SeqIO
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.metrics import (accuracy_score, roc_auc_score,
                              classification_report, confusion_matrix)
from xgboost import XGBClassifier

# =====================================================================
# Configuration
# =====================================================================
DATA_DIR    = "data"
GENOMES_DIR = os.path.join(DATA_DIR, "genomes")
MODELS_DIR  = os.path.join(DATA_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

ANTIBIOTIC_FILES = {
    "meropenem":     os.path.join(DATA_DIR, "metadata_meropenem.csv"),
    "ciprofloxacin": os.path.join(DATA_DIR, "metadata_ciprofloxacin.csv"),
    "cefotaxime":    os.path.join(DATA_DIR, "metadata_cefotaxime.csv"),
}

KMER_SIZE  = 5
TOP_KMERS  = 50_000   # cap n-features for speed

# =====================================================================
# Helpers
# =====================================================================
def read_fasta(path):
    """Concatenate all contigs in a FASTA file into one string."""
    seq = ""
    try:
        _open = gzip.open if path.endswith(".gz") else open
        with _open(path, "rt") as fh:
            for record in SeqIO.parse(fh, "fasta"):
                seq += str(record.seq).upper()
    except Exception as e:
        print(f"    Error reading {path}: {e}")
    return seq


def build_kmers(seq, k):
    """Return space-separated k-mer string from a DNA sequence."""
    return " ".join(seq[i:i+k] for i in range(len(seq) - k + 1))


# =====================================================================
# Phase A: Feature extraction
# =====================================================================
def extract_features(metadata_df, vectorizer=None, selector=None, training=True):
    """
    Load genomes, build k-mer matrix, apply feature selection.
    Returns (X, y, species_list, vectorizer, selector).
    """
    metadata_df = (metadata_df
                   .dropna(subset=["asm_acc", "resistant"])
                   .drop_duplicates(subset="asm_acc")
                   .copy())
    metadata_df["resistant"] = metadata_df["resistant"].astype(int)

    if training:
        metadata_df = metadata_df.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"  Loading {len(metadata_df)} genomes...")
    seqs, labels, species = [], [], []
    missing = 0

    for _, row in metadata_df.iterrows():
        acc   = row["asm_acc"]
        label = int(row["resistant"])
        sp    = row.get("taxgroup_name", "Unknown")

        fna = os.path.join(GENOMES_DIR, f"{acc}.fna")
        if not os.path.exists(fna):
            fna = os.path.join(GENOMES_DIR, f"{acc}.fna.gz")
        if not os.path.exists(fna):
            missing += 1
            continue

        seq = read_fasta(fna)
        if not seq:
            missing += 1
            continue

        seqs.append(build_kmers(seq, KMER_SIZE))
        labels.append(label)
        species.append(sp)

    print(f"  Loaded {len(seqs)} | Skipped (missing file): {missing}")
    y        = np.array(labels, dtype=int)
    sp_arr   = np.array(species)
    counts   = pd.Series(y).value_counts()
    print(f"  Susceptible: {counts.get(0,0)} | Resistant: {counts.get(1,0)}")

    # Vectorise
    if training:
        vectorizer = CountVectorizer(lowercase=False, min_df=2)
        X_raw = vectorizer.fit_transform(seqs)
    else:
        X_raw = vectorizer.transform(seqs)

    print(f"  Raw k-mer matrix: {X_raw.shape}")

    # Feature selection
    n_feat = min(TOP_KMERS, X_raw.shape[1])
    if training:
        selector = SelectKBest(chi2, k=n_feat)
        X = selector.fit_transform(X_raw, y)
    else:
        X = selector.transform(X_raw)

    print(f"  Final feature matrix: {X.shape}")
    return X, y, sp_arr, vectorizer, selector


# =====================================================================
# Phase B: Train & Evaluate one model
# =====================================================================
def train_model(X, y, sp_arr, antibiotic):
    print(f"\n  --- Training for: {antibiotic.upper()} ---")

    n_neg   = int(np.sum(y == 0))
    n_pos   = int(np.sum(y == 1))
    scale   = round(n_neg / n_pos, 2) if n_pos else 1.0

    X_tr, X_te, y_tr, y_te, sp_tr, sp_te = train_test_split(
        X, y, sp_arr,
        test_size=0.25, random_state=42, stratify=y
    )

    print(f"  Train {X_tr.shape[0]} | Test {X_te.shape[0]}")
    print(f"  scale_pos_weight = {scale}  (neg={n_neg}, pos={n_pos})")

    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=scale,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
        verbosity=0,
    )
    model.fit(X_tr, y_tr)

    # Overall metrics
    y_pred  = model.predict(X_te)
    y_proba = model.predict_proba(X_te)[:, 1]
    acc  = accuracy_score(y_te, y_pred)
    auc  = roc_auc_score(y_te, y_proba)

    print("\n" + "=" * 52)
    print(f"  {antibiotic.upper():<20}  Accuracy: {acc:.4f}   ROC-AUC: {auc:.4f}")
    print("=" * 52)
    print(classification_report(y_te, y_pred,
          target_names=["Susceptible (0)", "Resistant (1)"]))

    # Per-species breakdown
    print("  ── Per-species breakdown (test set) ──")
    sp_unique = np.unique(sp_te)
    rows = []
    for sp in sp_unique:
        mask = sp_te == sp
        if mask.sum() < 3:
            continue
        sp_acc = accuracy_score(y_te[mask], y_pred[mask])
        sp_res = int(np.sum(y_te[mask] == 1))
        sp_sus = int(np.sum(y_te[mask] == 0))
        rows.append({"Species": sp, "Samples": int(mask.sum()),
                     "Resistant": sp_res, "Susceptible": sp_sus,
                     "Accuracy": f"{sp_acc:.2f}"})
        print(f"    {sp:<35} n={int(mask.sum()):>3}  "
              f"R={sp_res}  S={sp_sus}  acc={sp_acc:.2f}")

    return model, {"antibiotic": antibiotic, "accuracy": acc, "roc_auc": auc,
                   "n_test_resistant": int(np.sum(y_te == 1)),
                   "n_test_susceptible": int(np.sum(y_te == 0))}


# =====================================================================
# Phase C: Predict on a new genome
# =====================================================================
def predict_genome(fasta_path, models_info):
    """Run all trained models on a single FASTA file and print resistance scores."""
    print(f"\n{'='*52}")
    print(f"  RESISTANCE PREDICTION")
    print(f"  Genome: {os.path.basename(fasta_path)}")
    print(f"{'='*52}")

    seq = read_fasta(fasta_path)
    if not seq:
        print("  ERROR: Could not read genome.")
        return

    kmer_str = build_kmers(seq, KMER_SIZE)

    for antibiotic, info in models_info.items():
        model      = info["model"]
        vectorizer = info["vectorizer"]
        selector   = info["selector"]

        X = vectorizer.transform([kmer_str])
        X = selector.transform(X)
        prob = model.predict_proba(X)[0][1]
        label = "RESISTANT" if prob > 0.5 else "Susceptible"
        bar = "█" * int(prob * 20) + "░" * (20 - int(prob * 20))
        print(f"  {antibiotic:<18} [{bar}] {prob:.2%}  → {label}")

    print(f"{'='*52}")


# =====================================================================
# Main
# =====================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BactoAI v2 — Multi-Antibiotic Pipeline")
    parser.add_argument("--train",   action="store_true",
                        help="Train all 3 antibiotic models")
    parser.add_argument("--antibiotic", default=None,
                        choices=list(ANTIBIOTIC_FILES.keys()),
                        help="Train only one antibiotic (optional)")
    parser.add_argument("--predict", action="store_true",
                        help="Predict resistance on a new genome")
    parser.add_argument("--fasta",   default=None,
                        help="Path to genome FASTA for --predict")
    args = parser.parse_args()

    # ── TRAIN ──────────────────────────────────────────────────────
    if args.train:
        targets = ([args.antibiotic] if args.antibiotic
                   else list(ANTIBIOTIC_FILES.keys()))
        summary_rows = []
        models_info  = {}

        for ab in targets:
            meta_file = ANTIBIOTIC_FILES[ab]
            if not os.path.exists(meta_file):
                print(f"  Metadata not found for {ab}: {meta_file}")
                continue

            print(f"\n{'#'*52}")
            print(f"  ANTIBIOTIC: {ab.upper()}")
            print(f"{'#'*52}")

            df = pd.read_csv(meta_file)
            X, y, sp_arr, vec, sel = extract_features(df)

            if X.shape[0] == 0:
                print(f"  No genomes loaded for {ab}. Skipping.")
                continue

            model, metrics = train_model(X, y, sp_arr, ab)

            # Save model
            model_path = os.path.join(MODELS_DIR, f"model_{ab}.json")
            model.save_model(model_path)
            print(f"\n  Model saved → {model_path}")

            models_info[ab] = {"model": model, "vectorizer": vec, "selector": sel}
            summary_rows.append(metrics)

        # ── Summary table ─────────────────────────────────────────
        if summary_rows:
            print(f"\n{'='*52}")
            print("  FINAL SUMMARY — ALL ANTIBIOTICS")
            print(f"{'='*52}")
            summary = pd.DataFrame(summary_rows).set_index("antibiotic")
            summary.columns = ["Accuracy", "ROC-AUC", "Test Resistant", "Test Susceptible"]
            print(summary.to_string())
            print(f"{'='*52}")
            summary.to_csv(os.path.join(DATA_DIR, "training_summary.csv"))
            print("  Summary saved → data/training_summary.csv")

    # ── PREDICT ────────────────────────────────────────────────────
    elif args.predict:
        if not args.fasta or not os.path.exists(args.fasta):
            print("ERROR: Provide a valid --fasta path.")
        else:
            # Re-load all saved models for prediction
            models_info = {}
            for ab, meta_file in ANTIBIOTIC_FILES.items():
                model_path = os.path.join(MODELS_DIR, f"model_{ab}.json")
                if not os.path.exists(model_path):
                    print(f"  Model not found for {ab} — run --train first.")
                    continue
                df  = pd.read_csv(meta_file)
                X, y, sp_arr, vec, sel = extract_features(
                    df, training=True)   # rebuild vectorizer from metadata
                loaded_model = XGBClassifier()
                loaded_model.load_model(model_path)
                models_info[ab] = {"model": loaded_model, "vectorizer": vec, "selector": sel}

            predict_genome(args.fasta, models_info)

    else:
        print("Usage: python bactoai_pipeline_v2.py [--train] [--predict --fasta PATH]")
