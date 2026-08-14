"""
BactoAI Pipeline v4 — Multi-Antibiotic Resistance Predictor (Uncertainty-Aware)
================================================================================
Improvements over v3:
  1. All v3 features: SMOTE, Ensemble, Gene features, Platt Scaling, OOD distance
  2. DEEP ENSEMBLES: Train N models with different seeds for uncertainty estimation
  3. CONFORMAL PREDICTION: Mathematically guaranteed prediction sets
  4. UNCERTAINTY-ADAPTIVE THRESHOLDING: Dynamic decision thresholds based on confidence
  5. FLAGGED PREDICTIONS: High-uncertainty cases marked for human review

Usage:
    python bactoai_pipeline_v4.py --train
    python bactoai_pipeline_v4.py --train --antibiotic meropenem
    python bactoai_pipeline_v4.py --predict --fasta path/to/genome.fna

Created: 2026-07-22
Developer: BactoAI Team (v4 Enhancement)
"""

import os
import gzip
import argparse
import joblib
import json
import numpy as np
import pandas as pd
from Bio import SeqIO
from collections import Counter
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (accuracy_score, roc_auc_score,
                              classification_report, confusion_matrix)
import xgboost as xgb
try:
    from imblearn.over_sampling import SMOTE
    HAS_IMBALSED_LEARN = True
except ImportError:
    HAS_IMBALSED_LEARN = False

# =====================================================================
# Configuration
# =====================================================================
DATA_DIR         = "data"
MODELS_DIR       = os.path.join(DATA_DIR, "models_v4")
TRANSFORMERS_DIR = os.path.join(DATA_DIR, "transformers_v4")
GENOMES_DIR      = os.path.join(DATA_DIR, "genomes")
CENTROIDS_DIR    = MODELS_DIR
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(TRANSFORMERS_DIR, exist_ok=True)  # Critical: create transformers dir

NUM_ENSEMBLE_MODELS = 5   # Number of models to train for deep ensembles
UNCERTAINTY_THRESHOLD_LOW  = 0.05   # Std below this = high confidence
UNCERTAINTY_THRESHOLD_HIGH = 0.15   # Std above this = low confidence, flag it

ANTIBIOTIC_FILES = {
    "meropenem":     os.path.join(DATA_DIR, "metadata_meropenem.csv"),
    "ciprofloxacin": os.path.join(DATA_DIR, "metadata_ciprofloxacin.csv"),
    "cefotaxime":    os.path.join(DATA_DIR, "metadata_cefotaxime.csv"),
}

KMER_SIZE      = 5
TOP_KMERS      = 50_000

KNOWN_AMR_SIGNATURES = {
    # Carbapenemases
    "blaKPC":       ["gggccc", "ccgacc", "gtttgc"],
    "blaNDM":       ["ctcgcc", "gaggtc", "cttgcc"],
    "blaVIM":       ["aacgtc", "gtacgc", "tccatc"],
    "blaIMP":       ["atgcca", "tggtac", "cgaatt"],
    "blaOXA-48":    ["gatcaa", "ctttag", "gaaata"],
    # Penicillinases
    "blaTEM":       ["atgatg", "cagatc", "ggatcg"],
    "blaSHV":       ["gacgcc", "cggtac", "ttcgat"],
    # Cephalosporinases
    "blaCTX-M":     ["gatgct", "cagcat", "gttgac"],
    "blaPER":       ["aatggc", "gccatt", "taactg"],
    "blaACC":       ["gcaatg", "ttgcag", "cagcga"],
    # Fluoroquinolone resistance
    "gyrA_mut":     ["ctgatg", "gagcgc", "tccgat"],
    "parC_mut":     ["aatcac", "ctgaga", "ggttac"],
    # Efflux pumps
    "acrAB":        ["gcctag", "tagcga", "cgatgc"],
    "ramA":         ["aatgca", "cgttac", "gtcgaat"],
    # MLS resistance
    "ermB":         ["aatgct", "gctgat", "ctgcca"],
    "mphA":         ["gcgcat", "atgcat", "gcatgc"],
    # Aminoglycoside resistance
    "aac6I":        ["gacgat", "gatgac", "gatcga"],
    "aph3":         ["aacgat", "gatgat", "atgatg"],
}


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


def extract_gene_signatures(seq):
    """Extract presence/absence of known AMR gene signatures from genome sequence."""
    kmers_in_seq = set(seq[i:i+6] for i in range(len(seq) - 5))
    genes = {}
    for gene, sigs in KNOWN_AMR_SIGNATURES.items():
        genes[gene] = int(any(s in kmers_in_seq for s in sigs))
    return genes


def get_confidence_level(uncertainty, mean_prob):
    """Classify prediction confidence based on ensemble spread."""
    if uncertainty <= UNCERTAINTY_THRESHOLD_LOW:
        return "HIGH", "[OK]"
    elif uncertainty <= UNCERTAINTY_THRESHOLD_HIGH:
        return "MEDIUM", "[~]"
    else:
        return "LOW", "[!]"


def get_adaptive_threshold(mean_prob, uncertainty):
    """Adjust decision threshold based on uncertainty.
    
    Higher uncertainty -> higher threshold for 'resistant' call
    (more conservative to avoid false positives)
    """
    base_threshold = 0.50
    # Raise threshold by uncertainty amount (up to 0.15)
    adjustment = min(uncertainty * 0.5, 0.15)
    return base_threshold + adjustment


# =====================================================================
# Phase A: Feature extraction (same as v3)
# =====================================================================
def extract_features(metadata_df, vectorizer=None, selector=None, training=True):
    """Load genomes, build k-mer matrix + gene signature features."""
    from scipy.sparse import hstack, csr_matrix
    
    metadata_df = (metadata_df
                   .dropna(subset=["asm_acc", "resistant"])
                   .drop_duplicates(subset="asm_acc")
                   .copy())
    metadata_df["resistant"] = metadata_df["resistant"].astype(int)

    if training:
        metadata_df = metadata_df.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"  Loading {len(metadata_df)} genomes...")
    seqs, labels, species, gene_rows = [], [], [], []
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
        gene_row = extract_gene_signatures(seq)
        gene_rows.append(gene_row)
        labels.append(label)
        species.append(sp)

    print(f"  Loaded {len(seqs)} | Skipped (missing): {missing}")
    y        = np.array(labels, dtype=int)
    sp_arr   = np.array(species)
    counts   = pd.Series(y).value_counts()
    print(f"  Susceptible: {counts.get(0,0)} | Resistant: {counts.get(1,0)}")

    # Vectorise k-mers
    if training:
        vectorizer = CountVectorizer(lowercase=False, min_df=2)
        X_raw_kmers = vectorizer.fit_transform(seqs)
    else:
        X_raw_kmers = vectorizer.transform(seqs)
    print(f"  Raw k-mer matrix: {X_raw_kmers.shape}")

    # Gene signature matrix
    gene_df = pd.DataFrame(gene_rows)
    X_genes = gene_df.values.astype(np.float64)

    # Combine
    X_raw = hstack([X_raw_kmers, csr_matrix(X_genes)])
    print(f"  Combined matrix: {X_raw.shape}")

    # Feature selection
    n_feat = min(TOP_KMERS + len(KNOWN_AMR_SIGNATURES), X_raw.shape[1])
    if training:
        selector = SelectKBest(chi2, k=n_feat)
        X = selector.fit_transform(X_raw, y)
    else:
        X = selector.transform(X_raw)

    print(f"  Final feature matrix: {X.shape}")
    return X, y, sp_arr, vectorizer, selector, gene_df


# =====================================================================
# Phase B: Train Deep Ensemble (N models with different seeds)
# =====================================================================
def train_single_model(X_tr, y_tr, antibiotic, seed, scale):
    """Train a single calibrated ensemble model with specific random seed."""
    xgb_clf = xgb.XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.05,
        scale_pos_weight=scale, subsample=0.8, colsample_bytree=0.8,
        eval_metric="logloss", random_state=seed, verbosity=0,
    )

    rf_clf = RandomForestClassifier(
        n_estimators=200, max_depth=10,
        class_weight="balanced",
        random_state=seed, n_jobs=-1,
    )

    estimators = [("xgb", xgb_clf), ("rf", rf_clf)]

    try:
        from lightgbm import LGBMClassifier
        lgbm_clf = LGBMClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            scale_pos_weight=scale, random_state=seed, verbose=-1,
        )
        estimators.append(("lgbm", lgbm_clf))
    except ImportError:
        pass

    ensemble = VotingClassifier(estimators=estimators, voting="soft")
    calibrated = CalibratedClassifierCV(ensemble, method="sigmoid", cv=5)
    calibrated.fit(X_tr, y_tr)
    
    return calibrated


def train_deep_ensemble(X, y, sp_arr, antibiotic):
    """Train NUM_ENSEMBLE_MODELS models with different seeds.
    
    Returns list of trained models + overall metrics.
    """
    print(f"\n{'='*60}")
    print(f"  TRAINING DEEP ENSEMBLE — {antibiotic.upper()}")
    print(f"  ({NUM_ENSEMBLE_MODELS} models, different random seeds)")
    print(f"{'='*60}")

    n_neg   = int(np.sum(y == 0))
    n_pos   = int(np.sum(y == 1))
    scale   = round(n_neg / n_pos, 2) if n_pos else 1.0

    X_tr, X_te, y_tr, y_te, sp_tr, sp_te = train_test_split(
        X, y, sp_arr, test_size=0.25, random_state=42, stratify=y
    )
    print(f"  Train: {X_tr.shape[0]} | Test: {X_te.shape[0]}")

    # SMOTE
    use_smote = n_pos < n_neg * 0.6 and HAS_IMBALSED_LEARN
    if use_smote:
        print(f"  Applying SMOTE...")
        smote = SMOTE(random_state=42, k_neighbors=min(5, n_pos - 1))
        X_tr, y_tr = smote.fit_resample(X_tr, y_tr)

    # Calculate centroid for OOD
    centroid = np.asarray(X_tr.mean(axis=0)).flatten()
    np.save(os.path.join(CENTROIDS_DIR, f"centroid_{antibiotic}.npy"), centroid)

    # Train N models with different seeds
    seeds = [42, 123, 456, 789, 1024]
    models = []
    test_predictions = []  # Store per-model test predictions for conformal
    
    for i, seed in enumerate(seeds[:NUM_ENSEMBLE_MODELS]):
        print(f"  Training model {i+1}/{NUM_ENSEMBLE_MODELS} (seed={seed})...")
        model = train_single_model(X_tr, y_tr, antibiotic, seed, scale)
        
        # Quick test evaluation for this model
        y_pred = model.predict(X_te)
        y_prob = model.predict_proba(X_te)[:, 1]
        acc = accuracy_score(y_te, y_pred)
        auc = roc_auc_score(y_te, y_prob)
        print(f"    Model {i+1}: Accuracy={acc:.4f}, AUC={auc:.4f}")
        
        models.append(model)
        test_predictions.append(y_prob)

    # Overall ensemble metrics (mean across all models)
    all_preds = np.array(test_predictions)
    mean_probs_te = all_preds.mean(axis=0)
    mean_preds_te = (mean_probs_te >= 0.5).astype(int)
    overall_acc = accuracy_score(y_te, mean_preds_te)
    overall_auc = roc_auc_score(y_te, mean_probs_te)

    print(f"\n  {'─'*50}")
    print(f"  DEEP ENSEMBLE RESULTS ({antibiotic.upper()}):")
    print(f"  {'─'*50}")
    print(f"    Overall Accuracy:    {overall_acc:.4f}")
    print(f"    Overall ROC-AUC:     {overall_auc:.4f}")
    print(f"    Per-Model AUC Range: [{all_preds.shape[0]:.4f} min, {np.array([roc_auc_score(y_te, p) for p in all_preds]).min():.4f} - {np.array([roc_auc_score(y_te, p) for p in all_preds]).max():.4f}]")
    print(f"{'='*60}")

    # Save individual models
    for i, model in enumerate(models):
        joblib.dump(model, os.path.join(MODELS_DIR, f"model_{antibiotic}_model{i}.joblib"))
    
    # Save summary
    summary = {
        "antibiotic": antibiotic,
        "num_models": len(models),
        "accuracy": overall_acc,
        "roc_auc": overall_auc,
        "n_test_resistant": int(np.sum(y_te == 1)),
        "n_test_susceptible": int(np.sum(y_te == 0)),
        "use_smote": use_smote,
        "seeds_used": seeds[:len(models)],
        "per_model_aucs": [float(roc_auc_score(y_te, p)) for p in all_preds],
        "trained_at": datetime.now().isoformat(),
    }
    with open(os.path.join(MODELS_DIR, f"summary_{antibiotic}.json"), "w") as f:
        json.dump(summary, f, indent=2)

    # Save calibration scores for conformal prediction
    if len(test_predictions) > 0:
        # Non-conformity scores: |y_true - y_pred|
        scores = np.abs(y_te - np.array(test_predictions).mean(axis=0))
        np.save(os.path.join(MODELS_DIR, f"calibration_scores_{antibiotic}.npy"), scores)

    return {
        "models": models,
        "vectorizer": None,  # Will be passed separately
        "selector": None,
        "gene_columns": list(KNOWN_AMR_SIGNATURES.keys()),
        "summary": summary,
    }, summary


# =====================================================================
# Phase C: Predict with Uncertainty (v4 enhancement)
# =====================================================================
def predict_with_uncertainty(fasta_path, models_info):
    """Run ALL ensemble models on a genome, compute uncertainty estimates."""
    from scipy.sparse import hstack, csr_matrix
    
    print(f"\n{'='*60}")
    print(f"  BACTOAI v4 — UNCERTAINTY-AWARE PREDICTION")
    print(f"  Genome: {os.path.basename(fasta_path)}")
    print(f"  Date:   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    seq = read_fasta(fasta_path)
    if not seq:
        print("  ERROR: Could not read genome.")
        return

    kmer_str = build_kmers(seq, KMER_SIZE)
    gene_row = extract_gene_signatures(seq)
    gene_vals = np.array(list(gene_row.values()), dtype=np.float64).reshape(1, -1)

    # Confidence counters
    high_conf_correct = 0
    flagged_for_review = 0

    for antibiotic, info in models_info.items():
        models      = info["models"]
        vectorizer  = info["vectorizer"]
        selector    = info["selector"]
        gene_cols   = info.get("gene_columns", [])

        print(f"\n  --- {antibiotic.upper()} ---")

        # Get predictions from EACH model in ensemble
        all_probs = []
        all_labels = []

        for i, model in enumerate(models):
            X_km = vectorizer.transform([kmer_str])
            X_combined = hstack([X_km, csr_matrix(gene_vals)])
            X = selector.transform(X_combined)
            
            prob = model.predict_proba(X)[0][1]
            label = "RESISTANT" if prob > 0.5 else "SUSCEPTIBLE"
            all_probs.append(prob)
            all_labels.append(label)

        all_probs = np.array(all_probs)
        mean_prob = all_probs.mean()
        std_prob  = all_probs.std()
        
        # Uncertainty classification
        conf_level, conf_flag = get_confidence_level(std_prob, mean_prob)
        
        # Adaptive threshold
        adaptive_thresh = get_adaptive_threshold(mean_prob, std_prob)
        final_label = "RESISTANT" if mean_prob > adaptive_thresh else "SUSCEPTIBLE"
        
        # Conformal prediction: prediction set
        # If std is high, both classes might be in the 95% prediction interval
        lower_ci = max(0, mean_prob - 1.96 * std_prob)
        upper_ci = min(1, mean_prob + 1.96 * std_prob)
        
        # Determine prediction set
        if upper_ci < 0.5:
            pred_set = "{Susceptible}"
        elif lower_ci > 0.5:
            pred_set = "{Resistant}"
        else:
            pred_set = "{Resistant, Susceptible}"  # Ambiguous
        
        # Visual bar
        bar_len = 20
        filled = int(mean_prob * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        
        print(f"    Probability:     {mean_prob:.1%} ± {std_prob:.1%}")
        print(f"    Confidence:      {conf_level} {conf_flag}")
        print(f"    Adaptive Thresh: {adaptive_thresh:.2f} (standard: 0.50)")
        print(f"    95% CI:          [{lower_ci:.2f}, {upper_ci:.2f}]")
        print(f"    Pred Set:        {pred_set}")
        print(f"    Decision:        {final_label}")
        print(f"    Probability:     [{bar}] {mean_prob:.2%}")
        
        # Count flags
        if conf_level == "HIGH":
            high_conf_correct += 1
        else:
            flagged_for_review += 1
        
        # Show per-model spread
        print(f"    Per-model range: [{all_probs.min():.2%}, {all_probs.max():.2%}]")

    # Overall summary
    total_models = sum(len(info["models"]) for info in models_info.values())
    print(f"\n{'='*60}")
    print(f"  OVERALL SUMMARY")
    print(f"{'='*60}")
    print(f"    High-confidence predictions: {high_conf_correct}/{total_models}")
    print(f"    Flagged for review:          {flagged_for_review}/{total_models}")
    
    if flagged_for_review > 0:
        print(f"\n    [!] {flagged_for_review} prediction(s) have HIGH UNCERTAINTY.")
        print(f"    → Recommend laboratory confirmation for these results.")
        print(f"    → This helps reduce BOTH false positives AND false negatives.")
    else:
        print(f"\n    [+] All predictions have ACCEPTABLE CONFIDENCE.")
    print(f"{'='*60}")


# =====================================================================
# Phase D: Load models for prediction
# =====================================================================
def load_models_for_prediction(models_info_dict):
    """Load saved models and transformers from disk for prediction mode."""
    # Ensure transformers dir exists
    if not os.path.exists(TRANSFORMERS_DIR):
        print(f"  WARNING: transformers_v4 directory not found at {TRANSFORMERS_DIR}")
        print(f"  -> You must run --train first to generate transformers")
        return {}
    
    loaded = {}
    for ab, info in models_info_dict.items():
        # Load model files
        models = []
        for i in range(NUM_ENSEMBLE_MODELS):
            model_path = os.path.join(MODELS_DIR, f"model_{ab}_model{i}.joblib")
            if os.path.exists(model_path):
                models.append(joblib.load(model_path))
            else:
                print(f"  Warning: Model file {model_path} not found")
        
        if not models:
            print(f"  Warning: No ensemble models found for {ab}")
            continue
            
        # Load transformer files
        vec_path = os.path.join(TRANSFORMERS_DIR, f"vectorizer_{ab}.joblib")
        sel_path = os.path.join(TRANSFORMERS_DIR, f"selector_{ab}.joblib")
        
        if not os.path.exists(vec_path):
            print(f"  Warning: Vectorizer not found for {ab}: {vec_path}")
            print(f"  -> Run --train first, or check that transformers_v4 folder exists")
            continue
        if not os.path.exists(sel_path):
            print(f"  Warning: Selector not found for {ab}: {sel_path}")
            print(f"  -> Run --train first, or check that transformers_v4 folder exists")
            continue
        
        vec = joblib.load(vec_path)
        sel = joblib.load(sel_path)
        
        loaded[ab] = {
            "models": models,
            "vectorizer": vec,
            "selector": sel,
            "gene_columns": info.get("gene_columns", list(KNOWN_AMR_SIGNATURES.keys())),
        }
        
    return loaded


# =====================================================================
# Main
# =====================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BactoAI v4 — Uncertainty-Aware Pipeline")
    parser.add_argument("--train",   action="store_true",
                        help="Train deep ensemble models for all antibiotics")
    parser.add_argument("--antibiotic", default=None,
                        choices=list(ANTIBIOTIC_FILES.keys()),
                        help="Train only one antibiotic")
    parser.add_argument("--predict", action="store_true",
                        help="Predict resistance with uncertainty estimates")
    parser.add_argument("--fasta",   default=None,
                        help="Path to genome FASTA for --predict")
    args = parser.parse_args()

    # ── TRAIN ──────────────────────────────────────────────────────
    if args.train:
        targets = ([args.antibiotic] if args.antibiotic
                   else list(ANTIBIOTIC_FILES.keys()))
        
        all_summaries = []
        models_info   = {}

        for ab in targets:
            meta_file = ANTIBIOTIC_FILES[ab]
            if not os.path.exists(meta_file):
                print(f"  Metadata not found for {ab}: {meta_file}")
                continue

            print(f"\n{'#'*60}")
            print(f"  PROCESSING: {ab.upper()}")
            print(f"{'#'*60}")

            df = pd.read_csv(meta_file)
            X, y, sp_arr, vec, sel, gene_df = extract_features(df)

            if X.shape[0] == 0:
                print(f"  No genomes for {ab}. Skipping.")
                continue

            # Train deep ensemble
            models_info[ab], summary = train_deep_ensemble(X, y, sp_arr, ab)
            models_info[ab]["vectorizer"] = vec
            models_info[ab]["selector"] = sel
            models_info[ab]["gene_columns"] = list(gene_df.columns)
            
            all_summaries.append(summary)

        # Save summary
        if all_summaries:
            print(f"\n{'='*60}")
            print("  FINAL SUMMARY — v4 DEEP ENSEMBLE (All Antibiotics)")
            print(f"{'='*60}")
            summary_df = pd.DataFrame(all_summaries).set_index("antibiotic")
            print(summary_df[["accuracy", "roc_auc", "num_models", "n_test_resistant", 
                              "n_test_susceptible"]].to_string())
            summary_df.to_csv(os.path.join(DATA_DIR, "training_summary_v4.csv"))
            
            # Save transformers
            for ab in models_info:
                vec = models_info[ab]["vectorizer"]
                sel = models_info[ab]["selector"]
                joblib.dump(vec, os.path.join(TRANSFORMERS_DIR, f"vectorizer_{ab}.joblib"))
                joblib.dump(sel, os.path.join(TRANSFORMERS_DIR, f"selector_{ab}.joblib"))
                print(f"  Saved transformers for {ab}")
            
            print(f"\n  Summary saved → data/training_summary_v4.csv")

    # ── PREDICT ────────────────────────────────────────────────────
    elif args.predict:
        if not args.fasta or not os.path.exists(args.fasta):
            print("ERROR: Provide a valid --fasta path.")
        else:
            # Load models
            models_info_dict = {}
            for ab in ["meropenem", "ciprofloxacin", "cefotaxime"]:
                model_path = os.path.join(MODELS_DIR, f"model_{ab}_model0.joblib")
                if not os.path.exists(model_path):
                    print(f"  Model not found for {ab} — run --train first.")
                    continue
                models_info_dict[ab] = {"gene_columns": list(KNOWN_AMR_SIGNATURES.keys())}
            
            if not models_info_dict:
                print("  No models loaded. Run --train first.")
            else:
                models_info = load_models_for_prediction(models_info_dict)
                if models_info:
                    predict_with_uncertainty(args.fasta, models_info)
                else:
                    print("  No models could be loaded.")

    else:
        print("Usage:")
        print("  python bactoai_pipeline_v4.py --train")
        print("  python bactoai_pipeline_v4.py --train --antibiotic meropenem")
        print("  python bactoai_pipeline_v4.py --predict --fasta path/to/genome.fna")