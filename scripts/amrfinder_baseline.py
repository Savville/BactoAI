"""
BactoAI — AMRFinderPlus Baseline Comparison (Q25)
===================================================
Runs NCBI AMRFinderPlus on test genomes and compares
gene-based resistance predictions against the ML ensemble.

Prerequisites:
  AMRFinderPlus must be installed. Options:
  1. conda install -c bioconda amrfinderplus
  2. Docker: docker pull ncbitaxonomy/amrfinder
  3. Manual install from https://github.com/NCBIAMRFinder/amrfinder

Usage:
  .venv\\Scripts\\python.exe scripts/amrfinder_baseline.py --help
  .venv\\Scripts\\python.exe scripts/amrfinder_baseline.py --run        # Run on all test genomes
  .venv\\Scripts\\python.exe scripts/amrfinder_baseline.py --dry-run   # Show what would be done
  .venv\\Scripts\\python.exe scripts/amrfinder_baseline.py --results   # Show existing results
"""
import os
import sys
import json
import argparse
import subprocess
import shutil
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
TEST_GENOMES_DIR = os.path.join(DATA_DIR, "test_genomes")
GENOMES_DIR = os.path.join(DATA_DIR, "genomes")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "validation_results")
AMRFINDER_OUTPUT_DIR = os.path.join(RESULTS_DIR, "amrfinder_results")

# Target antibiotics and their resistance gene markers
ANTIBIOTIC_MARKERS = {
    "meropenem": ["blaKPC", "blaNDM", "blaVIM", "blaIMP", "blaOXA-48", "blaKPC-2", "blaIMP-4", "blaNDM-1"],
    "ciprofloxacin": ["gyrA", "parC", "qnr", "aac(6')-Ib-cr"],
    "cefotaxime": ["blaCTX-M", "blaTEM", "blaSHV", "blaPER", "blaACC", "blaCTX-M-15", "blaTEM-1", "blaSHV-1"],
}

TARGET_ANTIBIOTICS = ["meropenem", "ciprofloxacin", "cefotaxime"]


def find_amrfinder():
    """Find AMRFinderPlus executable."""
    # Try common locations
    candidates = [
        "amrfinder",
        "amrfinder_plus",
        shutil.which("amrfinder"),
    ]
    # Check conda environment
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        candidates.append(os.path.join(conda_prefix, "bin", "amrfinder"))
        candidates.append(os.path.join(conda_prefix, "bin", "amrfinder_plus"))
    # Check pip-installed location
    pip_path = os.path.join(PROJECT_ROOT, ".venv", "bin", "amrfinder")
    if sys.platform == "win32":
        pip_path = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "amrfinder.exe")
    candidates.append(pip_path)

    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


def run_amrfinder(genome_path, output_dir, amrfinder_path):
    """Run AMRFinderPlus on a single genome."""
    os.makedirs(output_dir, exist_ok=True)
    out_base = os.path.splitext(os.path.basename(genome_path))[0]
    gene_file = os.path.join(output_dir, f"{out_base}.genes.txt")
    summary_file = os.path.join(output_dir, f"{out_base}.summary.txt")

    cmd = [
        amrfinder_path,
        "--noci",  # Skip CI warnings
        "--species", "Escherichia_coli",  # Default species
        genome_path,
        "--output", output_dir,
        "--gene_output", gene_file,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            # Parse gene findings
            genes_found = []
            if os.path.exists(gene_file):
                with open(gene_file) as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 3 and parts[0] != "Query":
                            genes_found.append(parts[2])  # Gene name column
            return True, genes_found
        else:
            return False, []
    except subprocess.TimeoutExpired:
        return False, []
    except Exception as e:
        return False, []


def parse_amrfinder_results(results_dir):
    """Parse all AMRFinderPlus results."""
    all_results = {}
    for fname in os.listdir(results_dir):
        if fname.endswith(".genes.txt"):
            genome_id = fname.replace(".genes.txt", "")
            genes = []
            with open(os.path.join(results_dir, fname)) as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 3 and parts[0] != "Query":
                        genes.append(parts[2])
            all_results[genome_id] = genes
    return all_results


def map_genes_to_antibiotic(genes_found, antibiotic):
    """Check if any resistance genes for an antibiotic were found."""
    markers = ANTIBIOTIC_MARKERS.get(antibiotic, [])
    # Check exact matches and partial matches
    for gene in genes_found:
        for marker in markers:
            if marker.lower() in gene.lower():
                return True
    return False


def generate_report(aml_results, metadata_results, output_path):
    """Generate comparison report."""
    lines = []
    lines.append("# AMRFinderPlus Baseline Comparison (Q25)")
    lines.append(f"\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("**Method:** NCBI AMRFinderPlus gene detection vs. ML ensemble predictions")
    lines.append("")

    for ab in TARGET_ANTIBIOTICS:
        lines.append(f"## {ab.capitalize()}")
        lines.append("")

        # Get metadata for this antibiotic
        meta_path = os.path.join(DATA_DIR, f"metadata_{ab}.csv")
        if not os.path.exists(meta_path):
            lines.append(f"  No metadata for {ab}")
            continue

        df = __import__('pandas').read_csv(meta_path)
        df = df.dropna(subset=["asm_acc", "resistant"]).drop_duplicates(subset="asm_acc")

        # Find matching genomes in AMRFinder results
        matched = 0
        aml_correct = 0
        aml_missing_r = 0  # Resistant by ML but no gene found
        aml_false_r = 0    # Susceptible by ML but gene found

        for _, row in df.iterrows():
            acc = row["asm_acc"]
            # Try different filename formats
            gene_file = None
            for suffix in [".genes.txt", f"{acc}.genes.txt"]:
                p = os.path.join(aml_results.get("dir", RESULTS_DIR), suffix)
                if os.path.exists(p):
                    gene_file = p
                    break

            if not gene_file:
                continue

            # Parse genes
            genes = []
            with open(gene_file) as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 3 and parts[0] != "Query":
                        genes.append(parts[2])

            matched += 1
            ml_resistant = int(row["resistant"]) == 1
            aml_has_gene = map_genes_to_antibiotic(genes, ab)

            if ml_resistant and aml_has_gene:
                aml_correct += 1  # True positive
            elif ml_resistant and not aml_has_gene:
                aml_missing_r += 1  # ML says resistant but no gene detected
            elif not ml_resistant and aml_has_gene:
                aml_false_r += 1  # Gene found but ML says susceptible

        lines.append(f"  Genomes with AMRFinder results: {matched}")
        lines.append(f"  ML Resistant & Gene Found (TP): {aml_correct}")
        lines.append(f"  ML Resistant but No Gene (FN gene): {aml_missing_r}")
        lines.append(f"  Gene Found but ML Susceptible (FP gene): {aml_false_r}")
        lines.append("")

    lines.append("---")
    lines.append("*Note: This is a preliminary comparison. Full comparison requires running AMRFinderPlus on all test genomes.*")
    lines.append("*AMRFinderPlus installation: `conda install -c bioconda amrfinderplus`*")

    report = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(report)
    return report


def main():
    parser = argparse.ArgumentParser(description="AMRFinderPlus baseline for BactoAI")
    parser.add_argument("--run", action="store_true", help="Run AMRFinderPlus on test genomes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--results", action="store_true", help="Show existing results")
    parser.add_argument("--report", action="store_true", help="Generate comparison report")
    args = parser.parse_args()

    print("=" * 70)
    print("  BACTOAI — AMRFINDERPLUS BASELINE (Q25)")
    print("=" * 70)

    # Find AMRFinderPlus
    amrfinder_path = find_amrfinder()
    if not amrfinder_path:
        print("\nERROR: AMRFinderPlus not found!")
        print("\nInstall options:")
        print("  1. conda install -c bioconda amrfinderplus")
        print("  2. docker run --rm -v $(pwd):/data ncbitaxonomy/amrfinder amrfinder --upper_case_feature true /data/genome.fna")
        print("  3. Download from: https://github.com/NCBIAMRFinder/amrfinder")
        print("\nProceeding with dry-run mode.")
        amrfinder_path = None

    if args.dry_run or not amrfinder_path:
        print("\n[DRY RUN] Files that would be processed:")
        genome_files = [f for f in os.listdir(TEST_GENOMES_DIR) if f.endswith((".fna", ".fasta"))]
        print(f"  Test genomes: {len(genome_files)}")
        for ab in TARGET_ANTIBIOTICS:
            meta = __import__('pandas').read_csv(os.path.join(DATA_DIR, f"metadata_{ab}.csv"))
            print(f"  {ab}: {len(meta)} metadata rows")
        print(f"\n  Output directory: {AMRFINDER_OUTPUT_DIR}")
        print(f"\n  To run: .venv\\Scripts\\python.exe scripts/amrfinder_baseline.py --run")
        return

    if args.run:
        print("\n[RUN] Running AMRFinderPlus on test genomes...")
        os.makedirs(AMRFINDER_OUTPUT_DIR, exist_ok=True)

        genome_files = [f for f in os.listdir(TEST_GENOMES_DIR) if f.endswith((".fna", ".fasta"))]
        print(f"  Processing {len(genome_files)} genomes...")

        results = {"dir": AMRFINDER_OUTPUT_DIR, "processed": 0, "failed": 0}
        for i, gf in enumerate(genome_files):
            genome_path = os.path.join(TEST_GENOMES_DIR, gf)
            success, genes = run_amrfinder(genome_path, AMRFINDER_OUTPUT_DIR, amrfinder_path)
            if success:
                results["processed"] += 1
                if (i + 1) % 10 == 0:
                    print(f"  [{i+1}/{len(genome_files)}] Done (genes found: {len(genes)})")
            else:
                results["failed"] += 1

        print(f"\n  Complete: {results['processed']} processed, {results['failed']} failed")
        with open(os.path.join(RESULTS_DIR, "amrfinder_status.json"), "w") as f:
            json.dump(results, f, indent=2)

    if args.results or args.report:
        # Load existing results
        status_file = os.path.join(RESULTS_DIR, "amrfinder_status.json")
        aml_results = {"dir": AMRFINDER_OUTPUT_DIR}
        if os.path.exists(status_file):
            with open(status_file) as f:
                aml_results = json.load(f)

        # Generate report
        output_path = os.path.join(RESULTS_DIR, "amrfinder_comparison_report.md")
        report = generate_report(aml_results, None, output_path)
        print("\n" + report)
        print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
