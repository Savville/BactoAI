"""
BactoAI Main Routes
====================
Handles the core application: genome upload, prediction, results display,
history, feedback, and export.
"""

import os
from pathlib import Path

from flask import (
    Blueprint, render_template, request, session,
    redirect, url_for, flash, jsonify, current_app, Response,
)

from bactoai.database import (
    get_db, save_submission, get_user_submissions,
    get_submission_by_id, save_feedback, get_submission_feedback,
    log_action,
)
from bactoai.models.prediction import (
    get_prediction_assets, predict_genome, predict_single_antibiotic,
    save_uploaded_file, cleanup_temp_file,
)
from bactoai.utils.genome_validator import validate_genome_file, GenomeValidationError
from bactoai.routes.auth import login_required, role_required
from bactoai.export.csv_export import generate_csv_export


main_bp = Blueprint("main", __name__)


# =====================================================================
# Pages
# =====================================================================

@main_bp.route("/")
@login_required
def index():
    """Main prediction page."""
    return render_template(
        "index.html",
        username=session.get("username"),
        clinic=session.get("clinic_name"),
        role=session.get("role"),
    )


@main_bp.route("/history")
@login_required
def history():
    """View submission history."""
    submissions = get_user_submissions(session["user_id"])
    return render_template(
        "history.html",
        submissions=submissions,
        username=session.get("username"),
    )


@main_bp.route("/history/json")
@login_required
def history_json():
    """Get submission history as JSON."""
    submissions = get_user_submissions(session["user_id"], limit=1000)
    return jsonify([dict(row) for row in submissions])


@main_bp.route("/submission/<int:submission_id>")
@login_required
def submission_detail(submission_id):
    """View a single submission with feedback form."""
    submission = get_user_submissions(session["user_id"])
    # Find the specific submission
    db = get_db()
    sub = db.execute(
        "SELECT * FROM submissions WHERE id = ? AND user_id = ?",
        (submission_id, session["user_id"]),
    ).fetchone()

    if not sub:
        flash("Submission not found.", "error")
        return redirect(url_for("main.history"))

    feedback = get_submission_feedback(submission_id)
    return render_template(
        "submission_detail.html",
        submission=sub,
        feedback=feedback,
        username=session.get("username"),
    )


# =====================================================================
# Prediction
# =====================================================================

@main_bp.route("/predict", methods=["POST"])
@login_required
@role_required("admin", "lab_tech", "viewer")
def predict():
    """Handle genome upload and return prediction results."""
    if current_app.config.get("STARTUP_ERROR"):
        return jsonify({
            "error": f"Prediction models could not be loaded: {current_app.config['STARTUP_ERROR']}"
        }), 503

    uploaded_file = request.files.get("file")
    if uploaded_file is None or uploaded_file.filename.strip() == "":
        return jsonify({"error": "No genome file was uploaded."}), 400

    sample_id = request.form.get("sample_id", "").strip() or None
    notes = request.form.get("notes", "").strip() or None
    temp_path = None

    try:
        # Save and validate the uploaded file
        temp_path = save_uploaded_file(uploaded_file)
        validate_genome_file(temp_path, uploaded_file.filename)

        # Run predictions
        genome_size = os.path.getsize(temp_path)
        results = predict_genome(temp_path)

        # Save to database
        submission_id = save_submission(
            user_id=session["user_id"],
            sample_id=sample_id or uploaded_file.filename,
            filename=uploaded_file.filename,
            genome_size=genome_size,
            results=results,
            notes=notes,
        )

        log_action(
            session["user_id"], "predict",
            f"Sample: {sample_id}, File: {uploaded_file.filename}",
            ip_address=request.remote_addr,
        )

        return jsonify({
            "submission_id": submission_id,
            "filename": uploaded_file.filename,
            "results": results,
        })

    except GenomeValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400
    except Exception as exc:
        current_app.logger.error(f"Prediction error: {exc}", exc_info=True)
        return jsonify({
            "error": "An error occurred while processing the genome. "
                     "Please ensure the file is a valid FASTA genome."
        }), 400
    finally:
        cleanup_temp_file(temp_path)


# =====================================================================
# Bulk Upload
# =====================================================================

@main_bp.route("/predict/bulk", methods=["POST"])
@login_required
@role_required("admin", "lab_tech")
def predict_bulk():
    """Handle bulk genome upload and return predictions for all files."""
    if current_app.config.get("STARTUP_ERROR"):
        return jsonify({
            "error": f"Prediction models could not be loaded: {current_app.config['STARTUP_ERROR']}"
        }), 503

    uploaded_files = request.files.getlist("files")
    if not uploaded_files or all(f.filename == "" for f in uploaded_files):
        return jsonify({"error": "No genome files were uploaded."}), 400

    notes = request.form.get("notes", "").strip() or None
    all_results = []
    errors = []

    for uploaded_file in uploaded_files:
        if uploaded_file.filename == "":
            continue
        temp_path = None
        try:
            temp_path = save_uploaded_file(uploaded_file)
            validate_genome_file(temp_path, uploaded_file.filename)

            genome_size = os.path.getsize(temp_path)
            results = predict_genome(temp_path)

            submission_id = save_submission(
                user_id=session["user_id"],
                sample_id=uploaded_file.filename,
                filename=uploaded_file.filename,
                genome_size=genome_size,
                results=results,
                notes=notes,
            )

            all_results.append({
                "submission_id": submission_id,
                "filename": uploaded_file.filename,
                "results": results,
            })
        except GenomeValidationError as e:
            errors.append({"filename": uploaded_file.filename, "error": e.message})
        except Exception as exc:
            errors.append({"filename": uploaded_file.filename, "error": str(exc)})
        finally:
            cleanup_temp_file(temp_path)

    log_action(
        session["user_id"], "predict_bulk",
        f"Processed: {len(all_results)}, Errors: {len(errors)}",
        ip_address=request.remote_addr,
    )

    return jsonify({
        "processed": len(all_results),
        "errors": len(errors),
        "results": all_results,
        "error_details": errors,
    })


# =====================================================================
# Feedback
# =====================================================================

@main_bp.route("/feedback", methods=["POST"])
@login_required
@role_required("admin", "lab_tech")
def submit_feedback():
    """Submit lab-confirmed feedback for a prediction."""
    submission_id = request.form.get("submission_id", type=int)
    antibiotic = request.form.get("antibiotic", "").strip().lower()
    actual_label = request.form.get("actual_label", "").strip().upper()
    actual_value = request.form.get("actual_value", "").strip() or None
    feedback_notes = request.form.get("notes", "").strip() or None

    if not submission_id or not antibiotic or not actual_label:
        return jsonify({"error": "Missing required fields: submission_id, antibiotic, actual_label"}), 400

    if actual_label not in ("RESISTANT", "SUSCEPTIBLE"):
        return jsonify({"error": "actual_label must be RESISTANT or SUSCEPTIBLE"}), 400

    # Verify the submission belongs to this user
    submission = get_submission_by_id(submission_id)
    if not submission or submission["user_id"] != session["user_id"]:
        return jsonify({"error": "Submission not found or access denied."}), 404

    # Get the predicted label for this antibiotic
    predicted_label = submission.get(f"{antibiotic}_label")

    save_feedback(
        submission_id=submission_id,
        user_id=session["user_id"],
        antibiotic=antibiotic,
        predicted_label=predicted_label or "UNKNOWN",
        actual_label=actual_label,
        actual_value=actual_value,
        notes=feedback_notes,
    )

    log_action(
        session["user_id"], "feedback",
        f"Submission {submission_id}, {antibiotic}: predicted={predicted_label}, actual={actual_label}",
        ip_address=request.remote_addr,
    )

    flash("Feedback submitted. Thank you for improving BactoAI!", "success")
    return redirect(url_for("main.submission_detail", submission_id=submission_id))


# =====================================================================
# Export
# =====================================================================

@main_bp.route("/export/csv")
@login_required
def export_csv():
    """Export submission history as CSV."""
    submissions = get_user_submissions(session["user_id"], limit=10000)
    csv_data = generate_csv_export(submissions)

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=bactoai_export.csv",
        },
    )


# =====================================================================
# Validation
# =====================================================================

@main_bp.route("/validate", methods=["GET"])
@login_required
@role_required("admin")
def validate():
    """Run holdout validation (admin only)."""
    import pandas as pd
    from sklearn.metrics import accuracy_score, roc_auc_score
    from sklearn.model_selection import train_test_split
    from bactoai.config import ANTIBIOTIC_FILES, DATA_DIR, GENOMES_DIR

    if current_app.config.get("STARTUP_ERROR"):
        return jsonify({
            "error": f"Prediction models could not be loaded: {current_app.config['STARTUP_ERROR']}"
        }), 503

    def _load_metadata_frame(antibiotic):
        metadata_path = ANTIBIOTIC_FILES[antibiotic]
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Missing metadata file: {metadata_path}")
        frame = pd.read_csv(metadata_path)
        required = {"asm_acc", "resistant"}
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"Metadata missing columns: {sorted(missing)}")
        frame = frame.dropna(subset=["asm_acc", "resistant"]).drop_duplicates(subset="asm_acc").copy()
        frame["resistant"] = frame["resistant"].astype(int)
        return frame

    def _evaluate(antibiotic):
        frame = _load_metadata_frame(antibiotic)
        if frame.empty:
            return {"antibiotic": antibiotic.capitalize(), "status": "no-data",
                    "accuracy": None, "roc_auc": None, "test_samples": 0}

        from bactoai.models.prediction import find_genome_path, copy_genome_into_dir
        split_frame = frame[["asm_acc", "resistant", "taxgroup_name"]].copy()
        train_frame, test_frame = train_test_split(
            split_frame, test_size=current_app.config["VALIDATION_TEST_SIZE"],
            random_state=current_app.config["VALIDATION_RANDOM_STATE"],
            stratify=split_frame["resistant"],
        )

        train_dir = current_app.config["TRAIN_GENOMES_DIR"]
        test_dir = current_app.config["TEST_GENOMES_DIR"]
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(test_dir, exist_ok=True)

        for _, row in train_frame.iterrows():
            copy_genome_into_dir(row["asm_acc"], train_dir)
        for _, row in test_frame.iterrows():
            copy_genome_into_dir(row["asm_acc"], test_dir)

        y_true, y_prob = [], []
        for _, row in test_frame.iterrows():
            genome_path = find_genome_path(row["asm_acc"], [test_dir, GENOMES_DIR, train_dir])
            if genome_path is None:
                continue
            try:
                prediction = predict_single_antibiotic(antibiotic, genome_path)
            except Exception:
                continue
            y_true.append(int(row["resistant"]))
            y_prob.append(float(prediction["probability"]))

        if not y_true:
            return {"antibiotic": antibiotic.capitalize(), "status": "no-data",
                    "accuracy": None, "roc_auc": None, "test_samples": 0}

        y_pred = [1 if p >= 0.5 else 0 for p in y_prob]
        return {
            "antibiotic": antibiotic.capitalize(),
            "status": "ok",
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "roc_auc": float(roc_auc_score(y_true, y_prob)) if len(set(y_true)) > 1 else None,
            "test_samples": len(y_true),
        }

    try:
        payload = {
            "antibiotics": [_evaluate(ab) for ab in current_app.config["ANTIBIOTIC_ORDER"]],
        }
        return jsonify(payload)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


# =====================================================================
# Health Check
# =====================================================================

@main_bp.route("/health")
def health():
    """Health check endpoint."""
    db_ok = True
    try:
        db = get_db()
        db.execute("SELECT 1")
    except Exception:
        db_ok = False

    return jsonify({
        "status": "ok" if (not current_app.config.get("STARTUP_ERROR") and db_ok) else "degraded",
        "models_loaded": bool(get_prediction_assets()),
        "database_ok": db_ok,
        "startup_error": current_app.config.get("STARTUP_ERROR"),
    })
