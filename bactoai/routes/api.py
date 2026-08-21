"""
BactoAI REST API Routes
========================
External API for programmatic access to predictions.
Uses API key authentication (no CSRF).
"""

import os

from flask import (
    Blueprint, request, jsonify, current_app,
)

from bactoai.database import (
    verify_api_key, save_submission, get_user_submissions,
    get_submission_by_id, log_action,
)
from bactoai.models.prediction import (
    get_prediction_assets, predict_genome,
    save_uploaded_file, cleanup_temp_file,
)
from bactoai.utils.genome_validator import validate_genome_file, GenomeValidationError


api_bp = Blueprint("api", __name__)


# =====================================================================
# API Key Authentication
# =====================================================================

def get_api_user():
    """Authenticate request via API key. Returns user_id or None."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        raw_key = auth_header[7:]
        return verify_api_key(raw_key)
    return None


def api_auth_required(f):
    """Decorator to require API key authentication."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_api_user()
        if not user_id:
            return jsonify({"error": "Unauthorized. Provide a valid API key in the Authorization header."}), 401
        request.api_user_id = user_id
        return f(*args, **kwargs)
    return decorated


# =====================================================================
# API Endpoints
# =====================================================================

@api_bp.route("/predict", methods=["POST"])
@api_auth_required
def api_predict():
    """Predict antibiotic resistance from an uploaded genome file.

    ---
    Headers:
        Authorization: Bearer <api_key>

    Form Data:
        file: Genome file (.fna, .fasta, .gz)
        sample_id: Optional sample identifier
        notes: Optional notes

    Returns:
        JSON with prediction results for all antibiotics.
    """
    if current_app.config.get("STARTUP_ERROR"):
        return jsonify({
            "error": f"Prediction models could not be loaded: {current_app.config['STARTUP_ERROR']}"
        }), 503

    uploaded_file = request.files.get("file")
    if uploaded_file is None or uploaded_file.filename.strip() == "":
        return jsonify({"error": "No genome file was uploaded. Use the 'file' field in multipart form data."}), 400

    sample_id = request.form.get("sample_id", "").strip() or None
    notes = request.form.get("notes", "").strip() or None
    temp_path = None

    try:
        temp_path = save_uploaded_file(uploaded_file)
        validate_genome_file(temp_path, uploaded_file.filename)

        genome_size = os.path.getsize(temp_path)
        results = predict_genome(temp_path)

        submission_id = save_submission(
            user_id=request.api_user_id,
            sample_id=sample_id or uploaded_file.filename,
            filename=uploaded_file.filename,
            genome_size=genome_size,
            results=results,
            notes=notes,
        )

        log_action(
            request.api_user_id, "api_predict",
            f"Sample: {sample_id}, File: {uploaded_file.filename}",
            ip_address=request.remote_addr,
        )

        return jsonify({
            "submission_id": submission_id,
            "filename": uploaded_file.filename,
            "genome_size": genome_size,
            "results": results,
        })

    except GenomeValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400
    except Exception as exc:
        current_app.logger.error(f"API prediction error: {exc}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the genome."}), 400
    finally:
        cleanup_temp_file(temp_path)


@api_bp.route("/history", methods=["GET"])
@api_auth_required
def api_history():
    """Get submission history for the authenticated API user.

    ---
    Headers:
        Authorization: Bearer <api_key>

    Query Parameters:
        limit: Maximum number of results (default 100, max 1000)

    Returns:
        JSON array of submissions.
    """
    limit = min(request.args.get("limit", 100, type=int), 1000)
    submissions = get_user_submissions(request.api_user_id, limit=limit)
    return jsonify({
        "count": len(submissions),
        "submissions": [dict(row) for row in submissions],
    })


@api_bp.route("/submission/<int:submission_id>", methods=["GET"])
@api_auth_required
def api_submission(submission_id):
    """Get a specific submission by ID.

    ---
    Headers:
        Authorization: Bearer <api_key>

    Returns:
        JSON with submission details.
    """
    submission = get_submission_by_id(submission_id)
    if not submission or submission["user_id"] != request.api_user_id:
        return jsonify({"error": "Submission not found."}), 404
    return jsonify(dict(submission))


@api_bp.route("/status", methods=["GET"])
def api_status():
    """API status check (no auth required).

    Returns:
        JSON with API version and model status.
    """
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "models_loaded": bool(get_prediction_assets()),
        "antibiotics": current_app.config.get("ANTIBIOTIC_ORDER", []),
    })
