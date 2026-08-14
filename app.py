import os
import shutil
import sqlite3
import tempfile
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import (
    Flask, jsonify, render_template, request, session,
    redirect, url_for, flash, g
)
from scipy.sparse import csr_matrix, hstack
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

from bactoai_pipeline import (
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


# =====================================================================
# App Config
# =====================================================================
app = Flask(__name__)
app.secret_key = os.environ.get("BACTOAI_SECRET", secrets.token_hex(32))

DB_PATH = os.path.join(DATA_DIR, "bactoai.db")
ANTIBIOTIC_ORDER = ["meropenem", "ciprofloxacin", "cefotaxime"]
MODEL_DIR = os.path.join(DATA_DIR, "models_v4")
TRAIN_GENOMES_DIR = os.path.join(DATA_DIR, "train_genomes")
TEST_GENOMES_DIR = os.path.join(DATA_DIR, "test_genomes")
VALIDATION_TEST_SIZE = 0.25
VALIDATION_RANDOM_STATE = 42


# =====================================================================
# Database
# =====================================================================
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            clinic_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sample_id TEXT NOT NULL,
            filename TEXT,
            genome_size INTEGER,
            meropenem_label TEXT,
            meropenem_prob REAL,
            meropenem_confidence TEXT,
            ciprofloxacin_label TEXT,
            ciprofloxacin_prob REAL,
            ciprofloxacin_confidence TEXT,
            cefotaxime_label TEXT,
            cefotaxime_prob REAL,
            cefotaxime_confidence TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id);
        CREATE INDEX IF NOT EXISTS idx_submissions_date ON submissions(submitted_at);
        CREATE INDEX IF NOT EXISTS idx_submissions_sample ON submissions(sample_id);
    """)
    db.commit()
    db.close()


def hash_password(password):
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return salt + pw_hash.hex()


def verify_password(stored, password):
    salt = stored[:32]
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return stored[32:] == pw_hash.hex()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def log_action(user_id, action, details=None):
    db = get_db()
    db.execute(
        "INSERT INTO audit_log (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)",
        (user_id, action, details, request.remote_addr)
    )
    db.commit()


# =====================================================================
# Model Loading
# =====================================================================
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
    init_db()
    PREDICTION_ASSETS = _load_prediction_assets()
    STARTUP_ERROR = None
except Exception as exc:
    PREDICTION_ASSETS = {}
    STARTUP_ERROR = str(exc)


# =====================================================================
# Helpers
# =====================================================================
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


def _save_submission(user_id, sample_id, filename, genome_size, results, notes=None):
    db = get_db()
    result_map = {r["antibiotic"].lower(): r for r in results}
    db.execute(
        """INSERT INTO submissions
           (user_id, sample_id, filename, genome_size,
            meropenem_label, meropenem_prob, meropenem_confidence,
            ciprofloxacin_label, ciprofloxacin_prob, ciprofloxacin_confidence,
            cefotaxime_label, cefotaxime_prob, cefotaxime_confidence,
            notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id, sample_id, filename, genome_size,
            result_map.get("meropenem", {}).get("label"),
            result_map.get("meropenem", {}).get("probability"),
            result_map.get("meropenem", {}).get("confidence"),
            result_map.get("ciprofloxacin", {}).get("label"),
            result_map.get("ciprofloxacin", {}).get("probability"),
            result_map.get("ciprofloxacin", {}).get("confidence"),
            result_map.get("cefotaxime", {}).get("label"),
            result_map.get("cefotaxime", {}).get("probability"),
            result_map.get("cefotaxime", {}).get("confidence"),
            notes,
        ),
    )
    db.commit()


# =====================================================================
# Auth Routes
# =====================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and verify_password(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["clinic_name"] = user["clinic_name"]
            log_action(user["id"], "login")
            return redirect(url_for("index"))

        flash("Invalid username or password", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        clinic_name = request.form.get("clinic_name", "").strip()

        if not username or not password:
            flash("Username and password are required", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return render_template("register.html")

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            flash("Username already exists", "error")
            return render_template("register.html")

        db.execute(
            "INSERT INTO users (username, password_hash, clinic_name) VALUES (?, ?, ?)",
            (username, hash_password(password), clinic_name),
        )
        db.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    if "user_id" in session:
        log_action(session["user_id"], "logout")
    session.clear()
    return redirect(url_for("login"))


# =====================================================================
# Main Routes
# =====================================================================
@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session.get("username"), clinic=session.get("clinic_name"))


@app.route("/predict", methods=["POST"])
@login_required
def predict():
    if STARTUP_ERROR:
        return jsonify({"error": f"Prediction assets could not be loaded: {STARTUP_ERROR}"}), 503

    uploaded_file = request.files.get("file")
    if uploaded_file is None or uploaded_file.filename.strip() == "":
        return jsonify({"error": "No genome file was uploaded."}), 400

    sample_id = request.form.get("sample_id", "").strip() or None
    notes = request.form.get("notes", "").strip() or None
    suffix = Path(uploaded_file.filename).suffix or ".fna"
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            uploaded_file.save(temp_path)

        genome_size = os.path.getsize(temp_path)
        results = [_predict_single_antibiotic(antibiotic, temp_path) for antibiotic in ANTIBIOTIC_ORDER]

        _save_submission(
            user_id=session["user_id"],
            sample_id=sample_id or uploaded_file.filename,
            filename=uploaded_file.filename,
            genome_size=genome_size,
            results=results,
            notes=notes,
        )
        log_action(session["user_id"], "predict", f"Sample: {sample_id}, File: {uploaded_file.filename}")

        return jsonify({"filename": uploaded_file.filename, "results": results})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/history")
@login_required
def history():
    db = get_db()
    submissions = db.execute(
        """SELECT * FROM submissions WHERE user_id = ?
           ORDER BY submitted_at DESC LIMIT 100""",
        (session["user_id"],),
    ).fetchall()
    return render_template("history.html", submissions=submissions, username=session.get("username"))


@app.route("/history/json")
@login_required
def history_json():
    db = get_db()
    submissions = db.execute(
        """SELECT * FROM submissions WHERE user_id = ?
           ORDER BY submitted_at DESC LIMIT 1000""",
        (session["user_id"],),
    ).fetchall()
    return jsonify([dict(row) for row in submissions])


@app.route("/validate", methods=["GET"])
@login_required
def validate():
    if STARTUP_ERROR:
        return jsonify({"error": f"Prediction assets could not be loaded: {STARTUP_ERROR}"}), 503

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
                "accuracy": None, "roc_auc": None, "test_samples": 0,
                "missing_genomes": 0, "skipped_genomes": 0, "results": [],
            }

        split_frame = frame[["asm_acc", "resistant", "taxgroup_name"]].copy()
        train_frame, test_frame = train_test_split(
            split_frame, test_size=VALIDATION_TEST_SIZE,
            random_state=VALIDATION_RANDOM_STATE, stratify=split_frame["resistant"],
        )

        os.makedirs(TRAIN_GENOMES_DIR, exist_ok=True)
        os.makedirs(TEST_GENOMES_DIR, exist_ok=True)

        for _, row in train_frame.iterrows():
            _copy_genome_into_dir(row["asm_acc"], TRAIN_GENOMES_DIR)
        for _, row in test_frame.iterrows():
            _copy_genome_into_dir(row["asm_acc"], TEST_GENOMES_DIR)

        y_true, y_prob, sample_rows = [], [], []
        missing_genomes, skipped_genomes = 0, 0

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
            sample_rows.append({
                "asm_acc": genome_id,
                "species": row.get("taxgroup_name", "Unknown"),
                "truth": "RESISTANT" if int(row["resistant"]) == 1 else "SUSCEPTIBLE",
                "predicted": prediction["label"],
                "probability": prediction["probability"],
                "confidence": prediction["confidence"],
                "status": prediction["status"],
            })

        if not y_true:
            return {
                "antibiotic": antibiotic.capitalize(),
                "status": "no-data",
                "message": "No validation genomes were available on disk.",
                "accuracy": None, "roc_auc": None, "test_samples": 0,
                "missing_genomes": missing_genomes,
                "skipped_genomes": skipped_genomes, "results": [],
            }

        y_pred = [1 if prob >= 0.5 else 0 for prob in y_prob]
        accuracy = float(accuracy_score(y_true, y_pred))
        roc_auc = float(roc_auc_score(y_true, y_prob)) if len(set(y_true)) > 1 else None

        return {
            "antibiotic": antibiotic.capitalize(),
            "status": "ok", "message": None,
            "accuracy": accuracy, "roc_auc": roc_auc,
            "test_samples": len(y_true),
            "missing_genomes": missing_genomes,
            "skipped_genomes": skipped_genomes,
            "results": sample_rows[:12],
        }

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
    db_ok = True
    try:
        db = get_db()
        db.execute("SELECT 1")
    except Exception:
        db_ok = False

    return jsonify({
        "status": "ok" if (not STARTUP_ERROR and db_ok) else "degraded",
        "models_loaded": bool(PREDICTION_ASSETS),
        "database_ok": db_ok,
        "startup_error": STARTUP_ERROR,
    })


# =====================================================================
# CLI Commands
# =====================================================================
@app.cli.command("create-user")
def create_user_cli():
    """Create a new user: flask create-user"""
    import click
    username = click.prompt("Username")
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    clinic = click.prompt("Clinic name (optional)", default="")

    db = sqlite3.connect(DB_PATH)
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        click.echo("Error: Username already exists")
        return

    db.execute(
        "INSERT INTO users (username, password_hash, clinic_name) VALUES (?, ?, ?)",
        (username, hash_password(password), clinic),
    )
    db.commit()
    db.close()
    click.echo(f"User '{username}' created successfully.")


@app.cli.command("init-db")
def init_db_cli():
    """Initialize the database."""
    init_db()
    print("Database initialized.")


# =====================================================================
# Run
# =====================================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
