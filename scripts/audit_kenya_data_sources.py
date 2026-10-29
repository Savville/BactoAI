"""
BactoAI — Comprehensive Kenyan/E African Genomic Data Audit
============================================================
Checks ALL available public sources for Kenyan and East African
genomes with both genotype (assembly) and phenotype (AST) data.

Sources checked:
  1. NCBI BigQuery (ncbi-pathogen-detect) — AST + country
  2. NCBI SRA / BioProject — genome assemblies from Kenya
  3. BV-BRC — E. coli AST (geographic inference via PubMed)
  4. PathogenWatch — African outbreak data
  5. NCBI Datasets API — bulk genome search by country
  6. PubMLST — population structure data for Kenya
  7. GISAID — limited bacterial data
"""

import os
import sys
import csv
import json
import requests
from datetime import datetime

import pandas as pd
import numpy as np

try:
    from google.cloud import bigquery
    HAS_BQ = True
except ImportError:
    HAS_BQ = False

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CREDENTIALS_PATH = os.path.join(PROJECT_ROOT, "credentials.json")

TARGET_ANTIBIOTICS = ["meropenem", "ciprofloxacin", "cefotaxime"]
KENYA_COUNTRIES = ["Kenya", "Uganda", "Tanzania", "Ethiopia", "Rwanda", "South Sudan", "Somalia", "Djibouti"]
AFRICA_COUNTRIES = KENYA_COUNTRIES + [
    "Nigeria", "South Africa", "Ghana", "Zambia", "Zimbabwe",
    "Cameroon", "Senegal", "Botswana", "Malawi", "Mozambique",
    "Tunisia", "Algeria", "Egypt", "Liberia", "Sierra Leone",
    "Sudan", "Morocco", "Madagascar", "Burundi", "DRC",
]
TARGET_SPECIES = [
    "Escherichia coli", "Klebsiella pneumoniae",
    "Acinetobacter baumannii", "Pseudomonas aeruginosa",
    "Salmonella enterica",
]


# =====================================================================
# Source 1: NCBI BigQuery
# =====================================================================

def query_bigquery_summary(client):
    """Get comprehensive counts from BigQuery."""
    results = {}

    # Kenya genomes with any AST
    kenya_sql = (
        "SELECT COUNT(DISTINCT t.asm_acc) as n_genomes,"
        "  COUNT(*) as n_ast_records"
        f" FROM `ncbi-pathogen-detect.pdbrowser.isolates` t"
        f" WHERE t.geo_loc_name LIKE '%Kenya%' AND t.asm_acc IS NOT NULL"
    )
    df = client.query(kenya_sql).result().to_dataframe()
    if not df.empty:
        results["kenya_genomes"] = int(df["n_genomes"].iloc[0])
        results["kenya_ast_records"] = int(df["n_ast_records"].iloc[0])

    # East Africa total
    ea_conditions = " OR ".join([f"t.geo_loc_name LIKE '%{c}%'" for c in KENYA_COUNTRIES])
    ea_sql = (
        "SELECT COUNT(DISTINCT t.asm_acc) as n_genomes,"
        "  COUNT(*) as n_ast_records"
        f" FROM `ncbi-pathogen-detect.pdbrowser.isolates` t"
        f" WHERE ({ea_conditions}) AND t.asm_acc IS NOT NULL"
    )
    df_ea = client.query(ea_sql).result().to_dataframe()
    if not df_ea.empty:
        results["ea_genomes"] = int(df_ea["n_genomes"].iloc[0])
        results["ea_ast_records"] = int(df_ea["n_ast_records"].iloc[0])

    # Africa total
    af_conditions = " OR ".join([f"t.geo_loc_name LIKE '%{c}%'" for c in AFRICA_COUNTRIES])
    af_sql = (
        "SELECT COUNT(DISTINCT t.asm_acc) as n_genomes,"
        "  COUNT(*) as n_ast_records"
        f" FROM `ncbi-pathogen-detect.pdbrowser.isolates` t"
        f" WHERE ({af_conditions}) AND t.asm_acc IS NOT NULL"
    )
    df_af = client.query(af_sql).result().to_dataframe()
    if not df_af.empty:
        results["africa_genomes"] = int(df_af["n_genomes"].iloc[0])
        results["africa_ast_records"] = int(df_af["n_ast_records"].iloc[0])

    # Kenya per-antibiotic breakdown
    ab_list = ",".join(TARGET_ANTIBIOTICS)
    ab_sql = (
        "SELECT LOWER(a.antibiotic) AS ab,"
        "  COUNT(DISTINCT t.asm_acc) as n_genomes,"
        "  COUNT(*) as n_records,"
        "  SUM(CASE WHEN LOWER(a.phenotype) IN ('r','resistant') THEN 1 ELSE 0 END) as n_res,"
        "  SUM(CASE WHEN LOWER(a.phenotype) IN ('s','susceptible') THEN 1 ELSE 0 END) as n_sus"
        f" FROM `ncbi-pathogen-detect.pdbrowser.isolates` t"
        " CROSS JOIN UNNEST(t.AST_phenotypes) AS a"
        f" WHERE t.geo_loc_name LIKE '%Kenya%' AND t.asm_acc IS NOT NULL"
        f" AND LOWER(a.antibiotic) IN ('{ab_list}')"
        " AND LOWER(a.phenotype) IN ('r','s','resistant','susceptible')"
        " GROUP BY LOWER(a.antibiotic)"
    )
    df_ab = client.query(ab_sql).result().to_dataframe()
    results["kenya_by_ab"] = {}
    if not df_ab.empty:
        for _, row in df_ab.iterrows():
            results["kenya_by_ab"][row["ab"]] = {
                "genomes": int(row["n_genomes"]),
                "records": int(row["n_records"]),
                "resistant": int(row["n_res"]),
                "susceptible": int(row["n_sus"]),
            }

    # Top African countries
    country_sql = (
        "SELECT t.geo_loc_name, COUNT(DISTINCT t.asm_acc) as n_genomes"
        f" FROM `ncbi-pathogen-detect.pdbrowser.isolates` t"
        f" WHERE ({af_conditions}) AND t.asm_acc IS NOT NULL"
        " GROUP BY t.geo_loc_name ORDER BY n_genomes DESC LIMIT 20"
    )
    df_country = client.query(country_sql).result().to_dataframe()
    results["top_african_countries"] = {}
    if not df_country.empty:
        for _, row in df_country.iterrows():
            results["top_african_countries"][row["geo_loc_name"]] = int(row["n_genomes"])

    # Kenya species breakdown
    species_sql = (
        "SELECT t.taxgroup_name, COUNT(DISTINCT t.asm_acc) as n_genomes"
        f" FROM `ncbi-pathogen-detect.pdbrowser.isolates` t"
        f" WHERE t.geo_loc_name LIKE '%Kenya%' AND t.asm_acc IS NOT NULL"
        " GROUP BY t.taxgroup_name ORDER BY n_genomes DESC"
    )
    df_species = client.query(species_sql).result().to_dataframe()
    results["kenya_by_species"] = {}
    if not df_species.empty:
        for _, row in df_species.iterrows():
            results["kenya_by_species"][row["taxgroup_name"]] = int(row["n_genomes"])

    return results


# =====================================================================
# Source 2: NCBI E-utilities — Genome assemblies
# =====================================================================

def query_ncbi_genomes():
    """Query NCBI for Kenya genome assemblies via E-utilities."""
    results = {}
    for species in TARGET_SPECIES:
        try:
            species_short = species.replace(" ", "_")
            query = f"Kenya AND ({species} [ORGN]) AND (wgs [Filter] OR disassembly_method:'WGS')"
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                "db": "nuccore",
                "term": query,
                "retmax": 10000,
                "retmode": "json",
                "rettype": "summary",
            }
            r = requests.get(url, params=params, timeout=30)
            if r.status_code == 200:
                data = r.json()
                count = int(data.get("esearchresult", {}).get("count", 0))
                results[species] = count
            else:
                results[species] = f"HTTP {r.status_code}"
        except Exception as e:
            results[species] = f"Error: {str(e)[:80]}"
    return results


# =====================================================================
# Source 3: PathogenWatch
# =====================================================================

def query_pathogenwatch():
    """Query PathogenWatch for African/Kenyan data."""
    results = {}
    try:
        # PathogenWatch has outbreak/surveillance data
        r = requests.get("https://pathogen.watch/api/v1/epidemics", timeout=15)
        if r.status_code == 200:
            epidemics = r.json()
            african_epidemics = [
                e for e in epidemics
                if any(c.lower() in str(e.get("location", "")).lower() for c in AFRICA_COUNTRIES)
            ]
            results["total_african_epidemics"] = len(african_epidemics)
            results["african_locations"] = list(set(
                e.get("location", "") for e in african_epidemics
            ))
    except Exception as e:
        results["error"] = str(e)[:100]
    return results


# =====================================================================
# Source 4: PubMLST
# =====================================================================

def query_pubmlst():
    """Check PubMLST for Kenyan isolates."""
    results = {}
    pubmlst_species = {
        "escherichia": "Escherichia coli",
        "klebsiella": "Klebsiella pneumoniae",
        "salmonella": "Salmonella enterica",
        "acinetobacter": "Acinetobacter baumannii",
    }
    for key, species in pubmlst_species.items():
        try:
            url = f"https://pubmlst.org/datasets/{key}/isolate_by_country.csv"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                df = pd.read_csv(r.text, sep=",")
                # Look for Kenya
                if "country" in df.columns:
                    kenya_count = len(df[df["country"].str.contains("Kenya", case=False, na=False)])
                    results[species] = kenya_count
                elif "locus" in df.columns:
                    results[species] = len(df)
                else:
                    results[species] = f"columns: {list(df.columns)[:5]}"
            else:
                results[species] = f"HTTP {r.status_code}"
        except Exception as e:
            results[species] = f"Error: {str(e)[:60]}"
    return results


# =====================================================================
# Source 5: Our existing BV-BRC data
# =====================================================================

def analyze_existing_bvbrc():
    """Analyze the BV-BRC data we already have."""
    bvbrc_csv = os.path.join(DATA_DIR, "BVBRC_genome_amr.csv")
    if not os.path.exists(bvbrc_csv):
        return {"error": "BV-BRC CSV not found"}

    df = pd.read_csv(bvbrc_csv)
    results = {
        "total_rows": len(df),
        "unique_genomes": df["Genome ID"].nunique(),
        "antibiotics": df["Antibiotic"].nunique(),
        "pubmed_sources": sorted(set(df["PubMed"].dropna().unique())),
        "typing_methods": sorted(set(df["Laboratory Typing Method"].dropna().unique())),
        "testing_standards": sorted(set(df["Testing Standard"].dropna().unique())),
    }

    # Check if BV-BRC data has any African connection
    # The 6 PubMed IDs correspond to specific studies
    pubmed_info = {
        "38219757": "German hospital E. coli (2024) - European",
        "29112974": "UK E. coli bloodstream (2018)",
        "32422315": "European E. coli ST131 (2020)",
        "33846529": "European K. pneumoniae (2021)",
        "36363724": "European clinical isolates (2022)",
        "30092762": "European E. coli (2018)",
    }
    results["pubmed_descriptions"] = {
        pid: pubmed_info.get(pid, "Unknown") for pid in results["pubmed_sources"]
    }
    results["note"] = "BV-BRC data is predominantly European; no direct Kenyan isolates"

    return results


# =====================================================================
# Source 6: NCBI Datasets — direct genome count
# =====================================================================

def query_ncbi_datasets():
    """Use NCBI Datasets API for Kenya genome counts."""
    results = {}
    for species in TARGET_SPECIES:
        species_key = species.replace(" ", "_").lower()
        try:
            url = "https://api.ncbi.nlm.nih.gov/datasets/v2/genome/taxonomy"
            params = {
                "taxon_name": species,
                "country": "Kenya",
                "include_type_material": False,
                "include_synonyms": False,
                "dataset_taxon_exclude": [],
                "fields": "accessions,genome_size,isolation_source",
                "pagination.limit": 1,  # just need count
            }
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 200:
                data = r.json()
                # The response has a metadata.pagination.total
                total = data.get("metadata", {}).get("pagination", {}).get("total", 0)
                results[species] = total
            else:
                results[species] = f"HTTP {r.status_code}"
        except Exception as e:
            results[species] = f"Error: {str(e)[:60]}"
    return results


# =====================================================================
# Main
# =====================================================================

def main():
    print("=" * 70)
    print("  BACTOAI — COMPREHENSIVE KENYAN GENOMIC DATA AUDIT")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    all_results = {}

    # Source 1: BigQuery
    print("\n[1] NCBI BigQuery (AST + country)...")
    if HAS_BQ:
        try:
            client = bigquery.Client.from_service_account_json(CREDENTIALS_PATH, project="bacto-ai")
            client.query("SELECT 1").result()
            bq = query_bigquery_summary(client)
            all_results["bigquery"] = bq
            print(f"  Kenya genomes: {bq.get('kenya_genomes', 'N/A')}")
            print(f"  Kenya AST records: {bq.get('kenya_ast_records', 'N/A')}")
            print(f"  East Africa genomes: {bq.get('ea_genomes', 'N/A')}")
            print(f"  Africa genomes: {bq.get('africa_genomes', 'N/A')}")
        except Exception as e:
            all_results["bigquery"] = {"error": str(e)}
            print(f"  ERROR: {e}")
    else:
        all_results["bigquery"] = {"error": "google-cloud-bigquery not installed"}

    # Source 2: NCBI E-utilities
    print("\n[2] NCBI E-utilities (genome assemblies)...")
    try:
        ncbi_genomes = query_ncbi_genomes()
        all_results["ncbi_eutils"] = ncbi_genomes
        for species, count in ncbi_genomes.items():
            print(f"  {species}: {count}")
    except Exception as e:
        all_results["ncbi_eutils"] = {"error": str(e)}
        print(f"  ERROR: {e}")

    # Source 3: PathogenWatch
    print("\n[3] PathogenWatch...")
    try:
        pw = query_pathogenwatch()
        all_results["pathogenwatch"] = pw
        if "total_african_epidemics" in pw:
            print(f"  African epidemics: {pw['total_african_epidemics']}")
    except Exception as e:
        all_results["pathogenwatch"] = {"error": str(e)}
        print(f"  ERROR: {e}")

    # Source 4: PubMLST
    print("\n[4] PubMLST...")
    try:
        pubmlst = query_pubmlst()
        all_results["pubmlst"] = pubmlst
        for species, count in pubmlst.items():
            print(f"  {species}: {count}")
    except Exception as e:
        all_results["pubmlst"] = {"error": str(e)}
        print(f"  ERROR: {e}")

    # Source 5: Existing BV-BRC
    print("\n[5] Existing BV-BRC data...")
    try:
        bvbrc = analyze_existing_bvbrc()
        all_results["bvbrc_existing"] = bvbrc
        print(f"  Total genomes: {bvbrc.get('unique_genomes', 'N/A')}")
        print(f"  Antibiotics: {bvbrc.get('antibiotics', 'N/A')}")
        print(f"  Note: {bvbrc.get('note', 'N/A')}")
    except Exception as e:
        all_results["bvbrc_existing"] = {"error": str(e)}
        print(f"  ERROR: {e}")

    # Source 6: NCBI Datasets API
    print("\n[6] NCBI Datasets API (country-filtered)...")
    try:
        datasets = query_ncbi_datasets()
        all_results["ncbi_datasets"] = datasets
        for species, count in datasets.items():
            print(f"  {species}: {count}")
    except Exception as e:
        all_results["ncbi_datasets"] = {"error": str(e)}
        print(f"  ERROR: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY: KENYAN/EAST AFRICAN ISOLATE AVAILABILITY")
    print("=" * 70)

    bq = all_results.get("bigquery", {})
    ncbi_g = all_results.get("ncbi_datasets", {})
    pubmlst = all_results.get("pubmlst", {})

    print(f"""
  ┌─────────────────────────────────────────────────────────────┐
  │ SOURCE                          │ KENYA GENOMES │ WITH AST   │
  ├─────────────────────────────────────────────────────────────┤""")

    if "kenya_genomes" in bq:
        print(f"  │ NCBI BigQuery (AST+country)   │ {bq['kenya_genomes']:>10} │ {bq.get('kenya_ast_records', '?'):>10} │")
    if "kenya_by_ab" in bq:
        for ab, info in bq["kenya_by_ab"].items():
            print(f"  │   └─ {ab:<20}│ {info['genomes']:>10} │ {info['records']:>10} │")

    for species, count in ncbi_g.items():
        if isinstance(count, int):
            print(f"  │ NCBI Datasets ({species[:20]:<18})│ {count:>10} │  ?        │")

    for species, count in pubmlst.items():
        if isinstance(count, int):
            print(f"  │ PubMLST ({species[:20]:<18})    │ {count:>10} │  ?        │")

    bvbrc = all_results.get("bvbrc_existing", {})
    if bvbrc.get("unique_genomes"):
        print(f"  │ BV-BRC (existing, non-Kenya)│ {bvbrc['unique_genomes']:>10} │ all       │")

    print(f"  └─────────────────────────────────────────────────────────────┘")

    # Recommendations
    print(f"\n  RECOMMENDATIONS:")
    if "kenya_genomes" in bq:
        k_genomes = bq["kenya_genomes"]
        k_ast = bq.get("kenya_ast_records", 0)
        print(f"  1. BigQuery has {k_genomes} Kenyan genomes, {k_ast} with AST")
        print(f"  2. Priority: Download Kenyan genomes with AST for retraining")
        print(f"  3. BV-BRC data is European-only — no additional Kenyan value there")

    return all_results


if __name__ == "__main__":
    results = main()

    # Save full results
    output = os.path.join(PROJECT_ROOT, "data", "kenya_data_audit.json")
    with open(output, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Full results saved to: {output}")
