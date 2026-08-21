"""
BactoAI Configuration
======================
Central configuration for all environments.
"""

import os
import secrets
from pathlib import Path

from bactoai_pipeline import (
    ANTIBIOTIC_FILES,
    DATA_DIR,
    GENOMES_DIR,
    KMER_SIZE,
    NUM_ENSEMBLE_MODELS,
    TRANSFORMERS_DIR,
)


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get("BACTOAI_SECRET", secrets.token_hex(32))

    # Database
    DB_PATH = os.path.join(DATA_DIR, "bactoai.db")

    # ML Pipeline
    ANTIBIOTIC_ORDER = ["meropenem", "ciprofloxacin", "cefotaxime"]
    MODEL_DIR = os.path.join(DATA_DIR, "models_v4")
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
    DB_PATH = ":memory:"
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    SKIP_MODEL_LOADING = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
