"""
BactoAI Genome Validator Tests
================================
Tests for genome file validation.
"""

import os
import pytest
from bactoai.utils.genome_validator import (
    validate_file_extension, validate_file_size, validate_fasta_content,
    validate_genome_file, GenomeValidationError,
)


class TestFileExtensionValidation:
    """Tests for file extension validation."""

    def test_valid_fna_extension(self, app):
        """.fna files should be accepted."""
        with app.app_context():
            validate_file_extension("genome.fna")  # Should not raise

    def test_valid_fasta_extension(self, app):
        """.fasta files should be accepted."""
        with app.app_context():
            validate_file_extension("genome.fasta")  # Should not raise

    def test_valid_gz_extension(self, app):
        """.fna.gz files should be accepted."""
        with app.app_context():
            validate_file_extension("genome.fna.gz")  # Should not raise

    def test_invalid_extension(self, app):
        """.txt files should be rejected."""
        with app.app_context():
            with pytest.raises(GenomeValidationError) as exc_info:
                validate_file_extension("genome.txt")
            assert exc_info.value.code == "invalid_extension"

    def test_empty_filename(self, app):
        """Empty filename should be rejected."""
        with app.app_context():
            with pytest.raises(GenomeValidationError) as exc_info:
                validate_file_extension("")
            assert exc_info.value.code == "no_filename"


class TestFileSizeValidation:
    """Tests for file size validation."""

    def test_empty_file(self, app, tmp_path):
        """Empty files should be rejected."""
        with app.app_context():
            empty_file = tmp_path / "empty.fna"
            empty_file.write_text("")
            with pytest.raises(GenomeValidationError) as exc_info:
                validate_file_size(str(empty_file))
            assert exc_info.value.code == "empty_file"

    def test_valid_size_file(self, app, tmp_path):
        """Files within size limit should pass."""
        with app.app_context():
            valid_file = tmp_path / "valid.fna"
            valid_file.write_text(">seq\nACGT" * 100)
            validate_file_size(str(valid_file))  # Should not raise


class TestFastaContentValidation:
    """Tests for FASTA content validation."""

    def test_valid_fasta(self, app, tmp_path):
        """Valid FASTA files should pass validation."""
        with app.app_context():
            fasta_file = tmp_path / "valid.fna"
            fasta_file.write_text(">genome_1\nACGTACGTACGTACGTACGTACGTACGTACGT\n>genome_2\nTTTTACGTACGTACGTACGTACGTACGTACGT\n")
            result = validate_fasta_content(str(fasta_file))
            assert result["valid"] is True
            assert result["record_count"] == 2

    def test_invalid_content(self, app, tmp_path):
        """Non-DNA content should be rejected."""
        with app.app_context():
            bad_file = tmp_path / "bad.fna"
            bad_file.write_text("This is not a DNA sequence at all.\nJust random text.\n")
            with pytest.raises(GenomeValidationError) as exc_info:
                validate_fasta_content(str(bad_file))
            assert exc_info.value.code in ("invalid_format", "invalid_content")

    def test_raw_sequence_without_header(self, app, tmp_path):
        """Raw DNA sequence without FASTA header should pass (it's DNA)."""
        with app.app_context():
            raw_file = tmp_path / "raw.fna"
            raw_file.write_text("ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT\n")
            result = validate_fasta_content(str(raw_file))
            assert result["valid"] is True


class TestFullValidation:
    """Tests for the full validation pipeline."""

    def test_valid_genome(self, app, tmp_path):
        """A valid genome file should pass all checks."""
        with app.app_context():
            genome_file = tmp_path / "genome.fna"
            genome_file.write_text(">test_genome\nACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT\n")
            result = validate_genome_file(str(genome_file), "genome.fna")
            assert result["valid"] is True

    def test_invalid_extension_pipeline(self, app, tmp_path):
        """Invalid extension should fail early."""
        with app.app_context():
            bad_file = tmp_path / "genome.txt"
            bad_file.write_text(">test\nACGTACGT\n")
            with pytest.raises(GenomeValidationError):
                validate_genome_file(str(bad_file), "genome.txt")
