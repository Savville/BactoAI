"""
BactoAI — Kenya Genome Enrichment Pipeline
============================================
Downloads Kenyan and East African genomes with both genotype (assembly) and 
phenotype (AST) data from multiple public sources, then prepares them for 
model retraining.

Sources:
  1. NCBI BigQuery (ncbi-pathogen-detect.pdbrowser.isolates) — AST + country
  2. NCBI Datasets API — genome FASTA download
  3. BV-BRC API — E. coli AST + genome lookup (geographic inference)
  4. Pathogenwatch / Public databases — additional African isolates

Usage:
  .venv\\Scripts\\python.exe scripts/enrich_kenya_genomes.py --dry-run
  .venv\\Scripts\\python.exe scripts/enrich_kenya_genomes.py --download
  .venv\\Scripts\\python.exe scripts/enrich_kenya_genomes.py --report
  .venv\\Scripts\\python.exe scripts/enrich_kenya_genomes.py --all
"""

import os
import sys
import csv
import json
import argparse
import time
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import numpy as np
from google.cloud import bigquery

# =====================================================================
# Configuration
# =====================================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "enrichment_kenya")
GENOMES_DIR = os.path.join(DATA_DIR, "genomes")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GENOMES_DIR, exist_ok=True)

# Target organisms (NCBI taxon IDs)
TARGET_TAXON_IDS = ["562", "573", "561", "287", "1387"]  # E. coli, K. pneumoniae, A. baumannii, P. aeruginosa, S. enterica
TARGET_SPECIES = ["Escherichia coli", "Klebsiella pneumoniae", "Acinetobacter baumannii", "Pseudomonas aeruginosa", "Salmonella enterica"]

# Target antibiotics
TARGET_ANTIBIOTICS = ["meropenem", "ciprofloxacin", "cefotaxime"]

# Geographic filters
KENYA_COUNTRIES = ["Kenya", "Uganda", "Tanzania", "Ethiopia", "Rwanda", "South Sudan", "Somalia", "Djibouti"]
AFRICA_COUNTRIES = KENYA_COUNTRIES + [
    "Nigeria", "South Africa", "Ghana", "Zambia", "Zimbabwe", "Cameroon",
    "Senegal", "Botswana", "Malawi", "Mozambique", "Tunisia", "Algeria",
    "Egypt", "Liberia", "Sierra Leone", "Sudan", "Morocco", "Madagascar",
]

CREDENTIALS_PATH = os.path.join(PROJECT_ROOT, "credentials.json")

# =====================================================================
# Source 1: NCBI BigQuery — AST + Country
# =====================================================================

def query_bigquery_kenya(client, antibiotic, limit=5000):
    """Query BigQuery for Kenyan/East African isolates with AST for a specific antibiotic."""
    country_conditions = " OR ".join([f"t.geo_loc_name LIKE '%{c}%'" for c in KENYA_COUNTRIES])
    
    sql = (
        "SELECT t.target_acc, t.taxgroup_name, t.asm_acc, t.collection_date,"
        "  t.geo_loc_name, t.isolation_source, LOWER(a.antibiotic) AS ab,"
        "  LOWER(a.phenotype) AS pheno"
        f" FROM `ncbi-pathogen-detect.pdbrowser.isolates` t"
        " CROSS JOIN UNNEST(t.AST_phenotypes) AS a"
        f" WHERE ({country_conditions})"
        f"   AND LOWER(a.antibiotic) = '{antibiotic}'"
        "   AND LOWER(a.phenotype) IN ('r', 's', 'resistant', 'susceptible', 'i', 'intermediate')"
        "   AND t.asm_acc IS NOT NULL"
        "   AND t.taxgroup_name IN ('Escherichia coli and Shigella', 'Klebsiella pneumoniae', 'Acinetobacter baumannii', 'Pseudomonas aeruginosa', 'Salmonella enterica')"
        " ORDER BY t.collection_date DESC"
        f" LIMIT {limit}"
    )
    
    df = client.query(sql).result().to_dataframe()
    return df


def query_bigquery_all_kenya(client, limit=10000):
    """Get all Kenyan isolates with any AST data."""
    country_conditions = " OR ".join([f"t.geo_loc_name LIKE '%{c}%'" for c in KENYA_COUNTRIES])
    
    sql = (
        "SELECT DISTINCT t.asm_acc, t.geo_loc_name, t.taxgroup_name,"
        "  t.collection_date, t.isolation_source"
        f" FROM `ncbi-pathogen-detect.pdbrowser.isolates` t"
        f" WHERE ({country_conditions})"
        "   AND t.asm_acc IS NOT NULL"
        f" LIMIT {limit}"
    )
    
    df = client.query(sql).result().to_dataframe()
    return df


def query_bigquery_africa_summary(client):
    """Get summary of all African isolates in BigQuery."""
    country_conditions = " OR ".join([f"t.geo_loc_name LIKE '%{c}%'" for c in AFRICA_COUNTRIES])
    
    sql = (
        "SELECT t.geo_loc_name, t.taxgroup_name, COUNT(DISTINCT t.asm_acc) as n_genomes,"
        "  COUNT(*) as n_ast_records"
        f" FROM `ncbi-pathogen-detect.pdbrowser.isolates` t"
        f" WHERE ({country_conditions})"
        "   AND t.asm_acc IS NOT NULL"
        " GROUP BY t.geo_loc_name, t.taxgroup_name"
        " ORDER BY n_genomes DESC"
        " LIMIT 100"
    )
    
    df = client.query(sql).result().to_dataframe()
    return df


# =====================================================================
# Source 2: NCBI Datasets API — Download Genomes
# =====================================================================

def download_genome_ncbi(asm_acc, output_dir, timeout=120, retries=3):
    """Download a genome FASTA from NCBI Datasets API."""
    url = f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/{asm_acc}"
    
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                # Extract FASTA from the response
                for genome in data.get("genome", {}).get("data", []):
                    for accession in genome.get("accessions", []):
                        if accession.get("accession") == asm_acc:
                            fasta_url = accession.get("fasta_url")
                            if fasta_url:
                                fa_r = requests.get(fasta_url, timeout=timeout)
                                if fa_r.status_code == 200:
                                    out_path = os.path.join(output_dir, f"{asm_acc}.fna")
                                    with open(out_path, "wb") as f:
                                        f.write(fa_r.content)
                                    return asm_acc, True
                return asm_acc, False
            elif r.status_code == 429:
                wait = 10 * attempt
                print(f"    [RATE LIMIT] Waiting {wait}s for {asm_acc}")
                time.sleep(wait)
            else:
                print(f"    [HTTP {r.status_code}] {asm_acc} (attempt {attempt})")
                if attempt < retries:
                    time.sleep(2)
        except Exception as e:
            print(f"    [ERROR] {asm_acc}: {e} (attempt {attempt})")
            if attempt < retries:
                time.sleep(5)
    
    return asm_acc, False


def download_genomes_batch(asm_accs, output_dir, workers=4, limit=None):
    """Download genomes in parallel."""
    if limit:
        asm_accs = asm_accs[:limit]
    
    # Skip already downloaded
    existing = set(
        fname.rsplit(".", 1)[0]
        for fname in os.listdir(output_dir)
        if fname.endswith((".fna", ".fasta", ".fa"))
    )
    todo = [acc for acc in asm_accs if acc not in existing]
    
    print(f"  Total to process: {len(asm_accs)}")
    print(f"  Already downloaded: {len(existing)}")
    print(f"  To download: {len(todo)}")
    
    if not todo:
        print("  Nothing to download.")
        return
    
    n_ok, n_fail = 0, 0
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(download_genome_ncbi, acc, output_dir): acc for acc in todo}
        for future in as_completed(futures):
            acc, ok = future.result()
            if ok:
                n_ok += 1
            else:
                n_fail += 1
            elapsed = time.time() - start
            rate = (n_ok + n_fail) / elapsed if elapsed > 0 else 0
            remaining = len(todo) - n_ok - n_fail
            eta = remaining / rate if rate > 0 else 0
            print(f"  [{n_ok + n_fail}/{len(todo)}] {acc} {'OK' if ok else 'FAIL'}  "
                  f"(rate: {rate:.1f}/s  ETA: {eta:.0f}s)")
    
    print(f"  Downloaded: {n_ok}, Failed: {n_fail}")
    return n_ok, n_fail


# =====================================================================
# Source 3: BV-BRC — E. coli AST with geographic inference
# =====================================================================

def query_bvbrc_kenya_e_coli(limit=2000):
    """
    Query BV-BRC for E. coli with AST data.
    BV-BRC doesn't store country directly, but we can infer from publication sources.
    """
    # BV-BRC API for E. coli AST
    url = "https://bvbrc.org/api/search/"
    
    # We'll use the existing BV-BRC data file instead
    bvbrc_csv = os.path.join(DATA_DIR, "BVBRC_genome_amr.csv")
    if not os.path.exists(bvbrc_csv):
        print("  BV-BRC CSV not found at data/BVBRC_genome_amr.csv")
        return pd.DataFrame()
    
    df = pd.read_csv(bvbrc_csv)
    
    # The BV-BRC data is from PMID 38219757 (European E. coli)
    # Check if any records mention African countries in the evidence column
    african_keywords = ["kenya", "nigeria", "south africa", "tunisia", "ethiopia", "ghana", "uganda", "tanzania", "africa"]
    df["evidence_lower"] = df["Evidence"].astype(str).str.lower()
    mask = df["evidence_lower"].apply(lambda x: any(k in x for k in african_keywords))
    african_rows = df[mask]
    
    print(f"  BV-BRC total rows: {len(df)}")
    print(f"  Potential African references in Evidence: {len(african_rows)}")
    
    return african_rows


# =====================================================================
# Source 4: Cross-reference with existing training set
# =====================================================================

def get_existing_training_asm_accs():
    """Load all asm_acc values from existing metadata CSVs."""
    all_asm = {}
    for f in ["data/metadata_meropenem.csv", "data/metadata_ciprofloxacin.csv", "data/metadata_cefotaxime.csv"]:
        path = os.path.join(PROJECT_ROOT, f)
        if not os.path.exists(path):
            continue
        with open(path) as fh:
            for row in csv.DictReader(fh):
                acc = row["asm_acc"]
                ab = row["antibiotic"]
                if acc not in all_asm:
                    all_asm[acc] = {"taxgroup": row["taxgroup_name"], "abs": set()}
                all_asm[acc]["abs"].add(ab)
    return all_asm


def find_new_kenyan_isolates(kenya_df, existing_asm_accs):
    """Find Kenyan isolates not already in the training set."""
    new_accs = []
    for _, row in kenya_df.iterrows():
        acc = row.get("asm_acc")
        if acc and acc not in existing_asm_accs:
            new_accs.append({
                "asm_acc": acc,
                "taxgroup": row.get("taxgroup_name", ""),
                "country": row.get("geo_loc_name", ""),
                "antibiotic": row.get("ab", ""),
                "phenotype": row.get("pheno", ""),
                "date": str(row.get("collection_date", ""))[:10] if pd.notna(row.get("collection_date")) else "",
            })
    return new_accs


# =====================================================================
# Report Generation
# =====================================================================

def generate_report(kenya_ast_df, africa_summary_df, existing_asm_accs, new_isolates):
    """Generate a comprehensive report of findings."""
    report = []
    report.append("=" * 70)
    report.append("  BACTOAI — KENYA GENOME ENRICHMENT REPORT")
    report.append(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 70)
    
    # Existing training set breakdown
    report.append(f"\n## Existing Training Set")
    report.append(f"  Total unique asm_acc: {len(existing_asm_accs)}")
    
    # Kenya-specific AST counts
    if not kenya_ast_df.empty:
        report.append(f"\n## Kenya AST Data (BigQuery)")
        report.append(f"  Total AST records: {len(kenya_ast_df)}")
        report.append(f"  Unique genomes: {kenya_ast_df['asm_acc'].nunique()}")
        
        # By antibiotic
        report.append(f"\n  By antibiotic:")
        for ab in TARGET_ANTIBIOTICS:
            ab_df = kenya_ast_df[kenya_ast_df["ab"] == ab]
            if not ab_df.empty:
                n_res = (ab_df["pheno"].isin(["r", "resistant"])).sum()
                n_sus = (ab_df["pheno"].isin(["s", "susceptible"])).sum()
                total = len(ab_df)
                rate = n_res / total if total > 0 else 0
                report.append(f"    {ab}: {total} records | {n_res}R / {n_sus}S | rate={rate:.1%}")
        
        # By species
        report.append(f"\n  By species:")
        for species, grp in kenya_ast_df.groupby("taxgroup_name"):
            report.append(f"    {species}: {len(grp)} records")
        
        # By location
        report.append(f"\n  By location:")
        for loc, grp in kenya_ast_df.groupby("geo_loc_name"):
            report.append(f"    {loc}: {len(grp)} records")
    
    # Africa summary
    if not africa_summary_df.empty:
        report.append(f"\n## All of Africa (BigQuery Summary)")
        total_african_genomes = africa_summary_df["n_genomes"].sum()
        total_african_records = africa_summary_df["n_ast_records"].sum()
        report.append(f"  Total African genomes: {total_african_genomes}")
        report.append(f"  Total African AST records: {total_african_records}")
        
        report.append(f"\n  Top countries:")
        for _, row in africa_summary_df.head(10).iterrows():
            report.append(f"    {row['geo_loc_name']}: {row['n_genomes']} genomes, {row['n_ast_records']} AST records")
    
    # New isolates available for training
    report.append(f"\n## New Isolates Available for Enrichment")
    report.append(f"  Kenyan genomes not in current training: {len(new_isolates)}")
    
    if new_isolates:
        # Count by antibiotic
        by_ab = {}
        for iso in new_isolates:
            ab = iso["antibiotic"]
            if ab not in by_ab:
                by_ab[ab] = {"total": 0, "resistant": 0, "susceptible": 0}
            by_ab[ab]["total"] += 1
            if iso["phenotype"] in ("r", "resistant"):
                by_ab[ab]["resistant"] += 1
            elif iso["phenotype"] in ("s", "susceptible"):
                by_ab[ab]["susceptible"] += 1
        
        report.append(f"\n  By antibiotic:")
        for ab, counts in sorted(by_ab.items()):
            report.append(f"    {ab}: {counts['total']} new isolates ({counts['resistant']}R / {counts['susceptible']}S)")
        
        # Save new isolate list
        new_file = os.path.join(OUTPUT_DIR, f"new_kenyan_isolates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        pd.DataFrame(new_isolates).to_csv(new_file, index=False)
        report.append(f"\n  Full list saved to: {new_file}")
    
    # Validation Q7 and Q28 answers
    report.append(f"\n## Answers to Validation Questions")
    report.append(f"\n  Q7: How many African/Kenyan isolates are in the training data?")
    if not kenya_ast_df.empty:
        kenya_in_training = len(set(kenya_ast_df["asm_acc"].unique()) & set(existing_asm_accs.keys()))
        africa_in_training = 0  # Would need full Africa query
        report.append(f"    Kenya in training: {kenya_in_training} isolates")
        report.append(f"    Total African in training: needs full Africa query")
        report.append(f"    Percentage of training set: {kenya_in_training / len(existing_asm_accs) * 100:.1f}%")
    
    report.append(f"\n  Q28: How many Kenyan/East African isolates with AST are publicly available?")
    if not kenya_ast_df.empty:
        report.append(f"    Kenyan genomes in BigQuery: {kenya_ast_df['asm_acc'].nunique()}")
        report.append(f"    Kenyan AST records: {len(kenya_ast_df)}")
    
    return "\n".join(report)


# =====================================================================
# Main
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Kenya Genome Enrichment Pipeline for BactoAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true", help="Query only, no downloads")
    parser.add_argument("--download", action="store_true", help="Download new genomes")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--all", action="store_true", help="Run everything")
    parser.add_argument("--limit", type=int, default=5000, help="Max rows per query")
    parser.add_argument("--workers", type=int, default=4, help="Download workers")
    args = parser.parse_args()
    
    run_all = args.all or args.dry_run or args.download or args.report
    
    print("=" * 70)
    print("  BACTOAI KENYA GENOME ENRICHMENT")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    # Load existing training set
    print("\n[1] Loading existing training set...")
    existing_asm_accs = get_existing_training_asm_accs()
    print(f"  {len(existing_asm_accs)} unique asm_acc values")
    
    # Connect to BigQuery
    print("\n[2] Connecting to BigQuery...")
    try:
        client = bigquery.Client.from_service_account_json(CREDENTIALS_PATH, project="bacto-ai")
        client.query("SELECT 1 AS test").result()
        print("  [OK] Connected")
    except Exception as e:
        print(f"  [ERROR] BigQuery connection failed: {e}")
        print("  Skipping BigQuery queries.")
        client = None
    
    # Query Kenya AST data
    kenya_ast_df = pd.DataFrame()
    africa_summary_df = pd.DataFrame()
    
    if client:
        print("\n[3] Querying Kenya AST data from BigQuery...")
        for ab in TARGET_ANTIBIOTICS:
            df = query_bigquery_kenya(client, ab, limit=args.limit)
            if not df.empty:
                kenya_ast_df = pd.concat([kenya_ast_df, df], ignore_index=True)
            print(f"  {ab}: {len(df)} records")
        
        print("\n[4] Querying Africa-wide summary...")
        africa_summary_df = query_bigquery_africa_summary(client)
        print(f"  {len(africa_summary_df)} country-species combinations")
    
    # Query BV-BRC for African E. coli
    print("\n[5] Checking BV-BRC for African references...")
    bvbrc_african = query_bvbrc_kenya_e_coli()
    
    # Find new isolates
    new_isolates = []
    if not kenya_ast_df.empty:
        new_isolates = find_new_kenyan_isolates(kenya_ast_df, existing_asm_accs)
        print(f"\n[6] Found {len(new_isolates)} new Kenyan isolates not in training set")
    
    # Generate report
    if args.report or args.dry_run or args.all:
        print("\n" + generate_report(kenya_ast_df, africa_summary_df, existing_asm_accs, new_isolates))
    
    # Download genomes
    if args.download and new_isolates:
        print("\n[7] Downloading new Kenyan genomes...")
        new_asm_accs = [iso["asm_acc"] for iso in new_isolates]
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        download_genomes_batch(new_asm_accs, OUTPUT_DIR, workers=args.workers)
        
        # Also save the enrichment metadata
        metadata_file = os.path.join(OUTPUT_DIR, "enrichment_metadata.csv")
        pd.DataFrame(new_isolates).to_csv(metadata_file, index=False)
        print(f"  Metadata saved to: {metadata_file}")
    
    print("\n" + "=" * 70)
    print("  DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
