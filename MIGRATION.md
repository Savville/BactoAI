# BactoAI Refactoring Guide

## What Changed

BactoAI has been restructured from a single-file Flask app into a modular package
with proper separation of concerns, security hardening, and new features.

## New Project Structure

```
Bacto_AI/
├── bactoai/                    # NEW: Main application package
│   ├── __init__.py             # Package init with create_app export
│   ├── app.py                  # Application factory
│   ├── config.py               # Configuration classes (Dev/Prod/Test)
│   ├── database.py             # All DB operations (users, submissions, feedback, audit)
│   ├── models/
│   │   └── prediction.py       # Model loading and prediction logic
│   ├── routes/
│   │   ├── auth.py             # Login, register, logout, API keys
│   │   ├── main.py             # Upload, predict, history, feedback, export
│   │   ├── api.py              # REST API (external integrations)
│   │   └── admin.py            # Admin dashboard and user management
│   ├── utils/
│   │   └── genome_validator.py # File validation (FASTA format, size, content)
│   └── export/
│       └── csv_export.py       # CSV export of submission history
├── tests/                      # NEW: Test suite
│   ├── conftest.py             # Shared fixtures
│   ├── test_auth.py            # Authentication tests
│   ├── test_database.py        # Database operation tests
│   └── test_genome_validator.py # Genome validation tests
├── templates/
│   ├── admin/                  # NEW: Admin templates
│   │   ├── dashboard.html
│   │   └── users.html
│   ├── submission_detail.html  # NEW: Submission detail with feedback form
│   ├── api_keys.html           # NEW: API key management
│   └── ... (existing templates updated with CSRF tokens)
├── .github/workflows/          # NEW: CI/CD
│   └── ci.yml
├── run.py                      # NEW: Entry point
├── pytest.ini                  # NEW: Test configuration
├── app.py                      # Original (kept for reference)
├── bactoai_pipeline.py         # ML pipeline (unchanged)
└── requirements.txt            # Updated with new dependencies
```

## New Features

### Security
- **CSRF Protection**: All forms now include CSRF tokens via Flask-WTF
- **Rate Limiting**: 200 requests/day, 50/hour by default via Flask-Limiter
- **API Key Auth**: External integrations use Bearer token authentication
- **User Roles**: Admin, Lab Tech, Viewer with role-based access control
- **File Validation**: Genome files are validated for format and content before processing

### New Functionality
- **REST API**: `/api/v1/predict`, `/api/v1/history`, `/api/v1/submission/<id>`
- **Admin Dashboard**: `/admin/` with stats, user management
- **Feedback Loop**: Lab techs can submit confirmed results to track accuracy
- **Bulk Upload**: Upload multiple genomes at once
- **CSV Export**: Download submission history as CSV
- **API Key Management**: Generate and manage API keys for integrations

### Code Quality
- **Modular Architecture**: Separated into focused modules
- **Test Suite**: pytest-based tests for auth, DB, and validation
- **CI/CD**: GitHub Actions workflow for automated testing
- **Configuration**: Environment-based config (Dev/Prod/Test)

## Running the App

```bash
# Development
python run.py

# Production
FLASK_ENV=production python run.py

# With Gunicorn
gunicorn "bactoai.app:create_app()" --bind 0.0.0.0:8080
```

## Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=bactoai --cov-report=term-missing
```

## API Usage

```bash
# Get API key from /api-keys page, then:
curl -X POST http://localhost:5000/api/v1/predict \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@genome.fna" \
  -F "sample_id=TEST-001"

curl http://localhost:5000/api/v1/history \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Database Changes

New tables added:
- `api_keys` — API key storage
- `feedback` — Lab-confirmed results
- `users.role` — Role column added to users table

Existing data in `submissions` and `audit_log` tables is preserved.
