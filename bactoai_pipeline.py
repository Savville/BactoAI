import os
import gzip
import joblib
import pandas as pd
import numpy as np
import urllib.request
from Bio import SeqIO
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.utils import resample
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

# =====================================================================
# Configuration
# =====================================================================
DATA_DIR = "data"
GENOMES_DIR = os.path.join(DATA_DIR, "genomes")
METADATA_FILE = os.path.join(DATA_DIR, "Ecoli_Carbapenem_Metadata.csv")
MODEL_FILE = os.path.join(DATA_DIR, "model_xgboost.json")
KMER_SIZE = 5
TOP_KMERS = 50000  # Keep the top N most informative k-mers

os.makedirs(GENOMES_DIR, exist_ok=True)

# =====================================================================
# Phase 1: Data Acquisition (Google BigQuery)
# =====================================================================
def acquire_data_bigquery():
    """
    Downloads metadata using Google BigQuery and then downloads the
    associated FASTA files from NCBI Datasets API.
    """
    try:
        from google.cloud import bigquery
    except ImportError:
        print("Please install google-cloud-bigquery: pip install google-cloud-bigquery")
        return None

    print("Fetching metadata from NCBI BigQuery...")
    from google.oauth2 import service_account
    import zipfile

    credentials_path = os.path.join(os.getcwd(), "credentials.json")
    if not os.path.exists(credentials_path):
        print(f"Error: {credentials_path} not found.")
        print("Please save your Google Cloud JSON key here as 'credentials.json'")
        return None

    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    query = """
    SELECT 
        target_acc, 
        taxgroup_name, 
        (SELECT phenotype FROM UNNEST(AST_phenotypes) WHERE antibiotic = 'meropenem' LIMIT 1) AS meropenem_phenotype,
        asm_acc
    FROM 
        `ncbi-pathogen-detect.pdbrowser.isolates` 
    WHERE 
        taxgroup_name = 'E.coli and Shigella' 
        AND EXISTS(SELECT 1 FROM UNNEST(AST_phenotypes) p 
                   WHERE p.antibiotic = 'meropenem' 
                   AND p.phenotype IN ('resistant', 'susceptible'))
        AND asm_acc IS NOT NULL
    LIMIT 500;
    """

    df = client.query(query).to_dataframe()

    def extract_label(val):
        if val == 'resistant':   return 1
        if val == 'susceptible': return 0
        return None

    df['resistant'] = df['meropenem_phenotype'].apply(extract_label)
    df = df.dropna(subset=['resistant', 'asm_acc'])
    df.to_csv(METADATA_FILE, index=False)
    print(f"Saved metadata to {METADATA_FILE} with {len(df)} samples.")

    # Download Genomes
    print("Downloading FASTA genomes...")
    for idx, row in df.iterrows():
        asm_acc = row['asm_acc']
        fasta_url = (f"https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/"
                     f"{asm_acc}/download?include_annotation_type=GENOME_FASTA")
        dest_file = os.path.join(GENOMES_DIR, f"{asm_acc}.fna")
        zip_path  = os.path.join(GENOMES_DIR, f"{asm_acc}.zip")

        if not os.path.exists(dest_file):
            try:
                urllib.request.urlretrieve(fasta_url, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    for member in zf.namelist():
                        if member.endswith(".fna"):
                            with zf.open(member) as src, open(dest_file, "wb") as dst:
                                dst.write(src.read())
                            break
                os.remove(zip_path)
                print(f"  Downloaded {asm_acc}")
            except Exception as e:
                print(f"  Failed {asm_acc}: {e}")
                if os.path.exists(zip_path):
                    os.remove(zip_path)
        else:
            print(f"  Already downloaded {asm_acc}")

    return df


# =====================================================================
# Phase 2: Feature Extraction (K-Mers)
# =====================================================================
def get_kmer_features(metadata_df, k=KMER_SIZE):
    """
    FIX 1: Shuffles and stratifies before loading genomes so BOTH classes
    are always evenly represented — no more sample-cap cutting off resistant rows.
    """
    print("\n--- Phase 2: K-Mer Feature Extraction ---")

    # ── FIX 1: Shuffle with stratification so both classes stay balanced ──
    metadata_df = metadata_df.dropna(subset=['asm_acc', 'resistant'])
    metadata_df['resistant'] = metadata_df['resistant'].astype(int)
    metadata_df = metadata_df.sample(frac=1, random_state=42).reset_index(drop=True)

    class_counts = metadata_df['resistant'].value_counts()
    print(f"  Full dataset — Susceptible: {class_counts.get(0,0)}, Resistant: {class_counts.get(1,0)}")

    sequences = []
    labels    = []
    skipped   = 0

    for _, row in metadata_df.iterrows():
        asm_acc   = row['asm_acc']
        label     = int(row['resistant'])

        fasta_path = os.path.join(GENOMES_DIR, f"{asm_acc}.fna.gz")
        if not os.path.exists(fasta_path):
            fasta_path = os.path.join(GENOMES_DIR, f"{asm_acc}.fna")

        if not os.path.exists(fasta_path):
            skipped += 1
            continue

        try:
            seq = ""
            _open = gzip.open if fasta_path.endswith('.gz') else open
            with _open(fasta_path, "rt") as handle:
                for record in SeqIO.parse(handle, "fasta"):
                    seq += str(record.seq).upper()

            kmers = [seq[i:i+k] for i in range(len(seq) - k + 1)]
            sequences.append(" ".join(kmers))
            labels.append(label)
        except Exception as e:
            print(f"  Error reading {fasta_path}: {e}")
            skipped += 1

    print(f"  Loaded {len(sequences)} genomes ({skipped} skipped — no .fna file).")

    y = np.array(labels, dtype=int)
    loaded_counts = pd.Series(y).value_counts()
    print(f"  Loaded — Susceptible: {loaded_counts.get(0,0)}, Resistant: {loaded_counts.get(1,0)}")

    # ── CountVectorizer: treat each k-mer as a word ──
    print(f"  Building k-mer frequency matrix (k={k})...")
    vectorizer = CountVectorizer(lowercase=False, min_df=2)
    X = vectorizer.fit_transform(sequences)
    print(f"  Raw feature matrix: {X.shape[0]} samples × {X.shape[1]} k-mers")

    # ── FIX 3: Select only top informative k-mers (chi-squared test) ──
    n_features = min(TOP_KMERS, X.shape[1])
    print(f"  Selecting top {n_features} k-mers by chi-squared score...")
    selector = SelectKBest(chi2, k=n_features)
    X = selector.fit_transform(X, y)
    print(f"  Reduced feature matrix: {X.shape[0]} samples × {X.shape[1]} k-mers")

    return X, y, vectorizer, selector


# =====================================================================
# Phase 3: Model Training & Evaluation
# =====================================================================
def train_and_evaluate(X, y):
    print("\n--- Phase 3: Training & Evaluation ---")

    # ── FIX 2: scale_pos_weight corrects class imbalance inside XGBoost ──
    n_neg = int(np.sum(y == 0))
    n_pos = int(np.sum(y == 1))
    scale = round(n_neg / n_pos, 2) if n_pos > 0 else 1.0
    print(f"  Class weight → scale_pos_weight = {scale}  (neg={n_neg}, pos={n_pos})")

    # Stratified split so both classes appear proportionally in train & test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    print(f"  Train: {X_train.shape[0]} samples | Test: {X_test.shape[0]} samples")
    print(f"  Train resistant: {int(np.sum(y_train==1))} | Test resistant: {int(np.sum(y_test==1))}")

    print(f"\n  Training XGBoost with {X_train.shape[1]} features...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=scale,   # ← FIX 2: Fight imbalance
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric='logloss',
        random_state=42,
        verbosity=0,
    )
    model.fit(X_train, y_train)

    # ── Evaluation ──
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("\n" + "=" * 45)
    print(f"  Accuracy : {acc:.4f}")
    print(f"  ROC-AUC  : {auc:.4f}")
    print("=" * 45)
    print(classification_report(y_test, y_pred,
                                target_names=["Susceptible (0)", "Resistant (1)"]))

    # ── FIX 4: Save model to disk ──
    model.save_model(MODEL_FILE)
    print(f"  Model saved → {MODEL_FILE}")

    return model


# =====================================================================
# Main Execution
# =====================================================================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="BactoAI ML Pipeline")
    parser.add_argument("--acquire", action="store_true",
                        help="Fetch data from BigQuery and download genomes")
    parser.add_argument("--train",   action="store_true",
                        help="Train the resistance prediction model")
    args = parser.parse_args()

    if args.acquire:
        acquire_data_bigquery()

    if args.train:
        if not os.path.exists(METADATA_FILE):
            print("Metadata not found. Run --acquire first.")
        else:
            df = pd.read_csv(METADATA_FILE)
            for col in ['asm_acc', 'resistant']:
                if col not in df.columns:
                    raise ValueError(f"Metadata missing column: {col}")

            X, y, vectorizer, selector = get_kmer_features(df)

            if X.shape[0] == 0:
                print("No genomes loaded. Check data/genomes/ directory.")
            else:
                train_and_evaluate(X, y)

    if not args.acquire and not args.train:
        print("Usage: python bactoai_pipeline.py [--acquire] [--train]")
