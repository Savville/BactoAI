"""
BactoAI CSV Export
===================
Generates CSV exports of submission history.
"""

import csv
import io
from datetime import datetime


CSV_COLUMNS = [
    "submission_id",
    "sample_id",
    "filename",
    "submitted_at",
    "meropenem_label",
    "meropenem_probability",
    "meropenem_confidence",
    "ciprofloxacin_label",
    "ciprofloxacin_probability",
    "ciprofloxacin_confidence",
    "cefotaxime_label",
    "cefotaxime_probability",
    "cefotaxime_confidence",
    "notes",
]


def generate_csv_export(submissions):
    """Generate a CSV string from a list of submission rows."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS)
    writer.writeheader()

    for sub in submissions:
        writer.writerow({
            "submission_id": sub["id"],
            "sample_id": sub["sample_id"],
            "filename": sub["filename"],
            "submitted_at": sub["submitted_at"],
            "meropenem_label": sub.get("meropenem_label", ""),
            "meropenem_probability": _format_prob(sub.get("meropenem_prob")),
            "meropenem_confidence": sub.get("meropenem_confidence", ""),
            "ciprofloxacin_label": sub.get("ciprofloxacin_label", ""),
            "ciprofloxacin_probability": _format_prob(sub.get("ciprofloxacin_prob")),
            "ciprofloxacin_confidence": sub.get("ciprofloxacin_confidence", ""),
            "cefotaxime_label": sub.get("cefotaxime_label", ""),
            "cefotaxime_probability": _format_prob(sub.get("cefotaxime_prob")),
            "cefotaxime_confidence": sub.get("cefotaxime_confidence", ""),
            "notes": sub.get("notes", ""),
        })

    return output.getvalue()


def _format_prob(prob):
    """Format a probability as percentage string."""
    if prob is None:
        return ""
    return f"{prob * 100:.1f}%"
