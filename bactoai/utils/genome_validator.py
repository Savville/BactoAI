"""
BactoAI Genome Validator
=========================
Validates uploaded genome files to ensure they are legitimate FASTA files
with valid DNA sequences before processing.
"""

import gzip
import os
from pathlib import Path

from flask import current_app


VALID_DNA_CHARS = set("ACGTNRYWSMKHBVD")
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
MIN_SEQUENCE_LENGTH = 100  # Minimum valid genome length


class GenomeValidationError(Exception):
    """Raised when a genome file fails validation."""

    def __init__(self, message, code="invalid_genome"):
        self.message = message
        self.code = code
        super().__init__(self.message)


def validate_file_extension(filename):
    """Check if the file has an allowed extension."""
    if not filename or filename.strip() == "":
        raise GenomeValidationError("No filename provided.", "no_filename")

    ext = Path(filename).suffix.lower()
    # Handle .fna.gz, .fasta.gz
    if filename.lower().endswith(".gz"):
        base_ext = Path(filename[:-3]).suffix.lower()
        allowed = current_app.config.get("ALLOWED_EXTENSIONS", {".fna", ".fasta", ".gz"})
        if base_ext not in allowed and f"{base_ext}.gz" not in allowed:
            raise GenomeValidationError(
                f"File type '{ext}' not allowed. Accepted: .fna, .fasta, .fna.gz, .fasta.gz",
                "invalid_extension",
            )
    else:
        allowed = current_app.config.get("ALLOWED_EXTENSIONS", {".fna", ".fasta", ".gz"})
        if ext not in allowed:
            raise GenomeValidationError(
                f"File type '{ext}' not allowed. Accepted: .fna, .fasta",
                "invalid_extension",
            )


def validate_file_size(file_path):
    """Check if the file size is within acceptable limits."""
    size = os.path.getsize(file_path)
    if size == 0:
        raise GenomeValidationError("The uploaded file is empty.", "empty_file")
    if size > MAX_FILE_SIZE:
        raise GenomeValidationError(
            f"File is too large ({size / 1024 / 1024:.1f} MB). "
            f"Maximum allowed size is {MAX_FILE_SIZE / 1024 / 1024:.0f} MB.",
            "file_too_large",
        )


def validate_fasta_content(file_path):
    """Validate that the file contains valid FASTA-formatted DNA sequences."""
    try:
        _open = gzip.open if file_path.endswith(".gz") else open
        with _open(file_path, "rt") as fh:
            content = fh.read(10240)  # Read first 10KB for quick check
    except Exception as e:
        raise GenomeValidationError(
            f"Could not read the file: {str(e)}. Make sure it's a valid FASTA file.",
            "read_error",
        )

    if not content.strip():
        raise GenomeValidationError("The uploaded file is empty.", "empty_file")

    # Check for FASTA header
    lines = content.strip().split("\n")
    has_header = any(line.startswith(">") for line in lines)

    if not has_header:
        # Could be a raw sequence without headers - check if it looks like DNA
        seq_lines = [line.strip() for line in lines if not line.startswith("#")]
        if seq_lines:
            sample = "".join(seq_lines)[:1000].upper()
            valid_count = sum(1 for c in sample if c in VALID_DNA_CHARS)
            if valid_count / max(len(sample), 1) < 0.8:
                raise GenomeValidationError(
                    "The file does not appear to contain valid DNA sequences. "
                    "Expected FASTA format with A, C, G, T nucleotides.",
                    "invalid_content",
                )
        else:
            raise GenomeValidationError(
                "The file does not appear to be in FASTA format. "
                "FASTA files start with '>' followed by a sequence header.",
                "invalid_format",
            )

    # Try to parse with Biopython for thorough validation
    try:
        from Bio import SeqIO
        _open = gzip.open if file_path.endswith(".gz") else open
        with _open(file_path, "rt") as fh:
            record_count = 0
            total_length = 0
            for record in SeqIO.parse(fh, "fasta"):
                record_count += 1
                total_length += len(record.seq)
                if record_count >= 10:  # Check first 10 records
                    break

            if record_count == 0:
                raise GenomeValidationError(
                    "No valid FASTA sequences found in the file.",
                    "no_sequences",
                )

            if total_length < MIN_SEQUENCE_LENGTH:
                raise GenomeValidationError(
                    f"Sequence too short ({total_length} bp). "
                    f"Minimum expected length is {MIN_SEQUENCE_LENGTH} bp.",
                    "sequence_too_short",
                )

            return {
                "record_count": record_count,
                "total_length": total_length,
                "valid": True,
            }
    except GenomeValidationError:
        raise
    except Exception as e:
        raise GenomeValidationError(
            f"Error parsing FASTA file: {str(e)}. "
            "Please ensure the file is a valid FASTA-formatted genome.",
            "parse_error",
        )


def validate_genome_file(file_path, filename=None):
    """
    Full validation pipeline for an uploaded genome file.

    Returns a dict with validation info on success.
    Raises GenomeValidationError on failure.
    """
    if filename:
        validate_file_extension(filename)
    validate_file_size(file_path)
    result = validate_fasta_content(file_path)
    return result
