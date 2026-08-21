"""
BactoAI Prediction Module
==========================
Handles model loading, genome prediction, and result classification.
All ML imports are lazy (inside functions) to avoid loading heavy deps at startup.
"""

import os
import tempfile
import shutil
from pathlib import Path

from bactoai.config import (
    ANTIBIOTIC_FILES,
    DATA_DIR,
    GENOMES_DIR,
    KMER_SIZE,
    NUM_ENSEMBLE_MODELS,
    TRANSFORMERS_DIR,
)


# =====================================================================
# Lazy imports (only loaded when prediction functions are called)
# =====================================================================

def _get_pipeline():
    """Import pipeline functions lazily to avoid loading heavy deps at startup."""
    from bactoai_pipeline import (
        build_kmers,
        extract_gene_signatures,
        get_adaptive_threshold,
        get_confidence_level,
        read_fasta,
    )
    return build_kmers, extract_gene_signatures, get_adaptive_threshold, get_confidence_level, read_fasta


def _get_ml_deps():
    """Import ML dependencies lazily."""
    import joblib
    import numpy as np
    from scipy.sparse import csr_matrix, hstack
    return joblib, np, csr_matrix, hstack


# =====================================================================
# Model Loading
# =====================================================================

def load_prediction_assets(app):
    """Load all prediction models and transformers into the app config."""
    joblib, _, _, _ = _get_ml_deps()

    assets = {}
    startup_error = None

    try:
        for antibiotic in app.config["ANTIBIOTIC_ORDER"]:
            vectorizer_path = os.path.join(TRANSFORMERS_DIR, f"vectorizer_{antibiotic}.joblib")
            selector_path = os.path.join(TRANSFORMERS_DIR, "selector_{antibiotic}.joblib")

            if not os.path.exists(vectorizer_path):
                raise FileNotFoundError(f"Missing vectorizer: {vectorizer_path}")
            if not os.path.exists(selector_path):
                raise FileNotFoundError(f"Missing selector: {selector_path}")

            models = []
            for index in range(NUM_ENSEMBLE_MODELS):
                model_path = os.path.join(
                    app.config["MODEL_DIR"], f"model_{antibiotic}_model{index}.joblib"
                )
                if os.path.exists(model_path):
                    models.append(joblib.load(model_path))

            if not models:
                raise FileNotFoundError(
                    f"No models found for {antibiotic} in {app.config['MODEL_DIR']}"
                )

            assets[antibiotic] = {
                "vectorizer": joblib.load(vectorizer_path),
                "selector": joblib.load(selector_path),
                "models": models,
            }
    except Exception as exc:
        startup_error = str(exc)
        app.logger.error(f"Failed to load prediction assets: {exc}")

    app.config["PREDICTION_ASSETS"] = assets
    app.config["STARTUP_ERROR"] = startup_error
    return assets


def get_prediction_assets(app=None):
    """Get the loaded prediction assets from the current app."""
    from flask import current_app
    app = app or current_app
    return app.config.get("PREDICTION_ASSETS", {})


# =====================================================================
# Prediction Helpers
# =====================================================================

def _classify_result(mean_prob, uncertainty):
    """Classify a prediction result based on probability and uncertainty."""
    _, _, get_adaptive_threshold, get_confidence_level, _ = _get_pipeline()
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


def predict_single_antibiotic(antibiotic, genome_path, assets=None):
    """Run prediction for a single antibiotic on a genome path."""
    if assets is None:
        assets = get_prediction_assets()

    _, np, csr_matrix, hstack = _get_ml_deps()
    build_kmers, extract_gene_signatures, _, _, read_fasta = _get_pipeline()

    asset = assets[antibiotic]
    sequence = read_fasta(genome_path)
    if not sequence:
        raise ValueError("Could not read genome sequence. The file may be empty or not a valid FASTA.")

    kmer_string = build_kmers(sequence, KMER_SIZE)
    gene_row = extract_gene_signatures(sequence)
    gene_values = np.array(list(gene_row.values()), dtype=np.float64).reshape(1, -1)

    X_kmers = asset["vectorizer"].transform([kmer_string])
    X_combined = hstack([X_kmers, csr_matrix(gene_values)])
    X = asset["selector"].transform(X_combined)

    probabilities = np.array(
        [model.predict_proba(X)[0][1] for model in asset["models"]], dtype=float
    )
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


def predict_genome(genome_path, assets=None):
    """Run prediction for all antibiotics on a genome file."""
    from flask import current_app
    antibiotic_order = current_app.config["ANTIBIOTIC_ORDER"]
    results = [
        predict_single_antibiotic(antibiotic, genome_path, assets)
        for antibiotic in antibiotic_order
    ]
    return results


# =====================================================================
# Genome File Helpers
# =====================================================================

def save_uploaded_file(uploaded_file):
    """Save an uploaded file to a temp location. Returns the temp path."""
    suffix = Path(uploaded_file.filename).suffix or ".fna"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_path = temp_file.name
    uploaded_file.save(temp_path)
    temp_file.close()
    return temp_path


def cleanup_temp_file(temp_path):
    """Remove a temporary file if it exists."""
    if temp_path and os.path.exists(temp_path):
        os.remove(temp_path)


def find_genome_path(genome_id, preferred_dirs):
    """Find a genome file by ID in the given directories."""
    candidates = [f"{genome_id}.fna", f"{genome_id}.fna.gz"]
    for directory in preferred_dirs:
        for filename in candidates:
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return path
    return None


def copy_genome_into_dir(genome_id, target_dir):
    """Copy a genome file into a target directory."""
    source_path = find_genome_path(genome_id, [GENOMES_DIR])
    if source_path is None:
        return None
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, os.path.basename(source_path))
    if not os.path.exists(target_path):
        shutil.copy2(source_path, target_path)
    return target_path
