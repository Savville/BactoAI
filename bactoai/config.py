"""
BactoAI Configuration
======================
Central configuration for all environments.
"""

import os
import secrets

from dotenv import load_dotenv

load_dotenv()


# =====================================================================
# ML Pipeline Constants (defined here to avoid importing heavy deps)
# =====================================================================

DATA_DIR = "data"
MODELS_DIR = os.path.join(DATA_DIR, "models_v4")
TRANSFORMERS_DIR = os.path.join(DATA_DIR, "transformers_v4")
GENOMES_DIR = os.path.join(DATA_DIR, "genomes")

ANTIBIOTIC_FILES = {
    "meropenem": os.path.join(DATA_DIR, "metadata_meropenem.csv"),
    "ciprofloxacin": os.path.join(DATA_DIR, "metadata_ciprofloxacin.csv"),
    "cefotaxime": os.path.join(DATA_DIR, "metadata_cefotaxime.csv"),
}

KMER_SIZE = 5
NUM_ENSEMBLE_MODELS = 5


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get("BACTOAI_SECRET", secrets.token_hex(32))

    # Database (Supabase PostgreSQL)
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

    # ML Pipeline
    ANTIBIOTIC_ORDER = ["meropenem", "ciprofloxacin", "cefotaxime"]
    MODEL_DIR = MODELS_DIR
    TRAIN_GENOMES_DIR = os.path.join(DATA_DIR, "train_genomes")
    TEST_GENOMES_DIR = os.path.join(DATA_DIR, "test_genomes")
    VALIDATION_TEST_SIZE = 0.25
    VALIDATION_RANDOM_STATE = 42

    # Upload
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB max upload
    ALLOWED_EXTENSIONS = {".fna", ".fasta", ".gz"}

    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")

    # Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    SKIP_MODEL_LOADING = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
