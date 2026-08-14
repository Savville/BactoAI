import os
import shutil
import tempfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request
from scipy.sparse import csr_matrix, hstack
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

from bactoai_pipeline_v4 import (
    ANTIBIOTIC_FILES,
    DATA_DIR,
    GENOMES_DIR,
    KMER_SIZE,
    NUM_ENSEMBLE_MODELS,
    TRANSFORMERS_DIR,
    build_kmers,
    extract_gene_signatures,
    get_adaptive_threshold,
    get_confidence_level,
    read_fasta,
)


app = Flask(__name__)

ANTIBIOTIC_ORDER = ["meropenem", "ciprofloxacin", "cefotaxime"]
MODEL_DIR = os.path.join(DATA_DIR, "models_v4")
TRAIN_GENOMES_DIR = os.path.join(DATA_DIR, "train_genomes")
TEST_GENOMES_DIR = os.path.join(DATA_DIR, "test_genomes")
VALIDATION_TEST_SIZE = 0.25
VALIDATION_RANDOM_STATE = 42


def _find_genome_path(genome_id, preferred_dirs):
    candidates = [f"{genome_id}.fna", f"{genome_id}.fna.gz"]
    for directory in preferred_dirs:
        for filename in candidates:
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return path
    return None


def _copy_genome_into_dir(genome_id, target_dir):
    source_path = _find_genome_path(genome_id, [GENOMES_DIR])
    if source_path is None:
        return None

    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, os.path.basename(source_path))
    if not os.path.exists(target_path):
        shutil.copy2(source_path, target_path)
    return target_path


def _load_prediction_assets():
    assets = {}

    for antibiotic in ANTIBIOTIC_ORDER:
        vectorizer_path = os.path.join(TRANSFORMERS_DIR, f"vectorizer_{antibiotic}.joblib")
        selector_path = os.path.join(TRANSFORMERS_DIR, f"selector_{antibiotic}.joblib")

        if not os.path.exists(vectorizer_path):
            raise FileNotFoundError(f"Missing vectorizer: {vectorizer_path}")
        if not os.path.exists(selector_path):
            raise FileNotFoundError(f"Missing selector: {selector_path}")

        models = []
        for index in range(NUM_ENSEMBLE_MODELS):
            model_path = os.path.join(MODEL_DIR, f"model_{antibiotic}_model{index}.joblib")
            if os.path.exists(model_path):
                models.append(joblib.load(model_path))

        if not models:
            raise FileNotFoundError(f"No models found for {antibiotic} in {MODEL_DIR}")

        assets[antibiotic] = {
            "vectorizer": joblib.load(vectorizer_path),
            "selector": joblib.load(selector_path),
            "models": models,
        }

    return assets


try:
    PREDICTION_ASSETS = _load_prediction_assets()
    STARTUP_ERROR = None
except Exception as exc:
    PREDICTION_ASSETS = {}
    STARTUP_ERROR = str(exc)


def _classify_result(mean_prob, uncertainty):
    confidence, _ = get_confidence_level(uncertainty, mean_prob)
    threshold = get_adaptive_threshold(mean_prob, uncertainty)
    label = "RESISTANT" if mean_prob >= threshold else "SUSCEPTIBLE"

    if confidence == "LOW":
        status = "uncertain"
        recommendation = "Low confidence. Recommend laboratory confirmation before acting on this result."
    elif label == "RESISTANT":
        status = "resistant"
        recommendation = "Likely resistant. Consider an alternative antibiotic."
    else:
        status = "susceptible"
        recommendation = "Likely susceptible based on the current model ensemble."

    return label, status, confidence, recommendation, threshold


def _predict_single_antibiotic(antibiotic, genome_path):
    asset = PREDICTION_ASSETS[antibiotic]
    sequence = read_fasta(genome_path)
    if not sequence:
        raise ValueError("Could not read genome sequence.")

    kmer_string = build_kmers(sequence, KMER_SIZE)
    gene_row = extract_gene_signatures(sequence)
    gene_values = np.array(list(gene_row.values()), dtype=np.float64).reshape(1, -1)

    X_kmers = asset["vectorizer"].transform([kmer_string])
    X_combined = hstack([X_kmers, csr_matrix(gene_values)])
    X = asset["selector"].transform(X_combined)

    probabilities = np.array([model.predict_proba(X)[0][1] for model in asset["models"]], dtype=float)
    mean_prob = float(probabilities.mean())
    uncertainty = float(probabilities.std())
    label, status, confidence, recommendation, threshold = _classify_result(mean_prob, uncertainty)

    lower_bound = max(0.0, mean_prob - 1.96 * uncertainty)
    upper_bound = min(1.0, mean_prob + 1.96 * uncertainty)

    return {
        "antibiotic": antibiotic.capitalize(),
        "probability": mean_prob,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "label": label,
        "status": status,
        "confidence": confidence,
        "recommendation": recommendation,
        "adaptive_threshold": threshold,
    }


def _load_metadata_frame(antibiotic):
    metadata_path = ANTIBIOTIC_FILES[antibiotic]
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Missing metadata file: {metadata_path}")

    frame = pd.read_csv(metadata_path)
    required = {"asm_acc", "resistant"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Metadata file {metadata_path} is missing columns: {sorted(missing)}")

    frame = frame.dropna(subset=["asm_acc", "resistant"]).drop_duplicates(subset="asm_acc").copy()
    frame["resistant"] = frame["resistant"].astype(int)
    return frame


def _evaluate_antibiotic_validation(antibiotic):
    frame = _load_metadata_frame(antibiotic)
    if frame.empty:
        return {
            "antibiotic": antibiotic.capitalize(),
            "status": "no-data",
            "message": "No labeled samples were available for validation.",
            "accuracy": None,
            "roc_auc": None,
            "test_samples": 0,
            "missing_genomes": 0,
            "skipped_genomes": 0,
            "results": [],
        }

    split_frame = frame[["asm_acc", "resistant", "taxgroup_name"]].copy()
    train_frame, test_frame = train_test_split(
        split_frame,
        test_size=VALIDATION_TEST_SIZE,
        random_state=VALIDATION_RANDOM_STATE,
        stratify=split_frame["resistant"],
    )

    os.makedirs(TRAIN_GENOMES_DIR, exist_ok=True)
    os.makedirs(TEST_GENOMES_DIR, exist_ok=True)

    for _, row in train_frame.iterrows():
        _copy_genome_into_dir(row["asm_acc"], TRAIN_GENOMES_DIR)

    for _, row in test_frame.iterrows():
        _copy_genome_into_dir(row["asm_acc"], TEST_GENOMES_DIR)

    y_true = []
    y_prob = []
    sample_rows = []
    missing_genomes = 0
    skipped_genomes = 0

    for _, row in test_frame.iterrows():
        genome_id = row["asm_acc"]
        genome_path = _find_genome_path(genome_id, [TEST_GENOMES_DIR, GENOMES_DIR, TRAIN_GENOMES_DIR])
        if genome_path is None:
            missing_genomes += 1
            continue

        try:
            prediction = _predict_single_antibiotic(antibiotic, genome_path)
        except Exception:
            skipped_genomes += 1
            continue

        y_true.append(int(row["resistant"]))
        y_prob.append(float(prediction["probability"]))
        sample_rows.append(
            {
                "asm_acc": genome_id,
                "species": row.get("taxgroup_name", "Unknown"),
                "truth": "RESISTANT" if int(row["resistant"]) == 1 else "SUSCEPTIBLE",
                "predicted": prediction["label"],
                "probability": prediction["probability"],
                "confidence": prediction["confidence"],
                "status": prediction["status"],
            }
        )

    if not y_true:
        return {
            "antibiotic": antibiotic.capitalize(),
            "status": "no-data",
            "message": "No validation genomes were available on disk.",
            "accuracy": None,
            "roc_auc": None,
            "test_samples": 0,
            "missing_genomes": missing_genomes,
            "skipped_genomes": skipped_genomes,
            "results": [],
        }

    y_pred = [1 if prob >= 0.5 else 0 for prob in y_prob]
    accuracy = float(accuracy_score(y_true, y_pred))
    roc_auc = float(roc_auc_score(y_true, y_prob)) if len(set(y_true)) > 1 else None

    return {
        "antibiotic": antibiotic.capitalize(),
        "status": "ok",
        "message": None,
        "accuracy": accuracy,
        "roc_auc": roc_auc,
        "test_samples": len(y_true),
        "missing_genomes": missing_genomes,
        "skipped_genomes": skipped_genomes,
        "results": sample_rows[:12],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if STARTUP_ERROR:
        return jsonify({"error": f"Prediction assets could not be loaded: {STARTUP_ERROR}"}), 503

    uploaded_file = request.files.get("file")
    if uploaded_file is None or uploaded_file.filename.strip() == "":
        return jsonify({"error": "No genome file was uploaded."}), 400

    suffix = Path(uploaded_file.filename).suffix or ".fna"
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            uploaded_file.save(temp_path)

        results = [_predict_single_antibiotic(antibiotic, temp_path) for antibiotic in ANTIBIOTIC_ORDER]
        return jsonify({"filename": uploaded_file.filename, "results": results})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/validate", methods=["GET"])
def validate():
    if STARTUP_ERROR:
        return jsonify({"error": f"Prediction assets could not be loaded: {STARTUP_ERROR}"}), 503

    try:
        payload = {
            "test_size": VALIDATION_TEST_SIZE,
            "random_state": VALIDATION_RANDOM_STATE,
            "train_genomes_dir": os.path.relpath(TRAIN_GENOMES_DIR, DATA_DIR).replace("\\", "/"),
            "test_genomes_dir": os.path.relpath(TEST_GENOMES_DIR, DATA_DIR).replace("\\", "/"),
            "antibiotics": [_evaluate_antibiotic_validation(antibiotic) for antibiotic in ANTIBIOTIC_ORDER],
        }
        return jsonify(payload)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok" if not STARTUP_ERROR else "degraded",
            "models_loaded": bool(PREDICTION_ASSETS),
            "startup_error": STARTUP_ERROR,
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
