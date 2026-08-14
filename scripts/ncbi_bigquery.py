"""
NCBI BigQuery Enrichment Script for BactoAI
=============================================
Queries NCBI Pathogen Detection data via Google BigQuery to extract:
1. Geographic resistance prevalence priors (for Bayesian modeling)
2. Additional AST data to enrich existing metadata without modifying it

WARNING: This script does NOT modify existing CSV files.
All outputs are written to NEW files in data/bigquery_output/.

BigQuery Schema Notes:
- AST_phenotypes is a RECORD (nested array) with fields: phenotype, antibiotic
- Use UNNEST(AST_phenotypes) to flatten it
- geo_loc_name, collection_date, isolation_source are top-level STRING fields

Usage:
    python scripts/ncbi_bigquery.py --priors
    python scripts/ncbi_bigquery.py --ast-enrich
    python scripts/ncbi_bigquery.py --all
    python scripts/ncbi_bigquery.py --priors --country Kenya
    python scripts/ncbi_bigquery.py --ast-enrich --antibiotic meropenem --limit 1000

Created: 2026-08-05
"""

import os
import sys
import argparse
import json
import warnings
from datetime import datetime

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

# =====================================================================
# Configuration
# =====================================================================
OUTPUT_DIR = os.path.join("data", "bigquery_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROJECT_ID = "bacto-ai"
DATASET = "ncbi-pathogen-detect"
TABLE = "pdbrowser.isolates"

# Target antibiotics for enrichment
TARGET_ANTIBIOTICS = [
    "meropenem", "imipenem", "ertapenem",
    "ciprofloxacin", "levofloxacin",
    "cefotaxime", "ceftriaxone", "ceftazidime",
    "gentamicin", "amikacin", "tobramycin",
    "ampicillin", "piperacillin-tazobactam",
    "trimethoprim-sulfamethoxazole", "colistin",
]

# Geographic regions of interest (for Kenya deployment)
INTERESTED_COUNTRIES = [
    "Kenya", "Uganda", "Tanzania", "Ethiopia", "Nigeria",
    "South Africa", "Ghana", "Rwanda", "Zambia", "Zimbabwe",
    "India", "Brazil", "United States", "United Kingdom",
]

# =====================================================================
# BigQuery Helper
# =====================================================================
def get_bigquery_client():
    """Create BigQuery client using credentials.json."""
    from google.cloud import bigquery

    creds_path = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
    if not os.path.exists(creds_path):
        creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")

    if os.path.exists(creds_path):
        client = bigquery.Client.from_service_account_json(
            creds_path, project=PROJECT_ID
        )
        print(f"  [OK] Authenticated via service account: {creds_path}")
    else:
        client = bigquery.Client(project=PROJECT_ID)
        print("  [OK] Using default application credentials")

    return client


def run_query(client, sql, max_results=10000):
    """Run a BigQuery SQL query and return results as a pandas DataFrame."""
    print(f"  Running query ({max_results} max results)...")
    query_job = client.query(sql)
    results = query_job.result()
    rows = list(results)
    if not rows:
        print("  No results returned.")
        return pd.DataFrame()

    df = pd.DataFrame(
        [dict(row) for row in rows],
        columns=list(rows[0].keys())
    )
    print(f"  Returned {len(df)} rows")
    return df


# =====================================================================
# Query 1: Geographic Prevalence Priors (for Bayesian Model)
# =====================================================================
def query_geographic_priors(client, countries=None, limit=50000):
    """
    Query NCBI BigQuery for geographic resistance prevalence.
    Uses UNNEST to flatten AST_phenotypes RECORD array.
    """
    if countries is None:
        countries = INTERESTED_COUNTRIES

    country_conditions = " OR ".join(
        [f"t.geo_loc_name LIKE '%{c}%'" for c in countries]
    )

    # BigQuery requires CROSS JOIN UNNEST for array fields
    sql = (
        "SELECT "
        "  t.geo_loc_name AS country, "
        "  LOWER(a.antibiotic) AS antibiotic, "
        "  COUNT(*) AS total_tests, "
        "  SUM(CASE WHEN LOWER(a.phenotype) IN ('r', 'resistant') THEN 1 ELSE 0 END) AS resistant_count, "
        "  SUM(CASE WHEN LOWER(a.phenotype) IN ('s', 'susceptible') THEN 1 ELSE 0 END) AS susceptible_count "
        f"FROM `{DATASET}.{TABLE}` t "
        "CROSS JOIN UNNEST(t.AST_phenotypes) AS a "
        f"WHERE ({country_conditions}) "
        "  AND a.antibiotic IS NOT NULL "
        "  AND LOWER(a.phenotype) IN ('r', 's', 'resistant', 'susceptible') "
        "GROUP BY country, antibiotic "
        "HAVING total_tests >= 10 "
        "ORDER BY country, antibiotic "
        f"LIMIT {limit}"
    )

    df = run_query(client, sql, limit)
    if df.empty:
        print("  No geographic prior data found.")
        return df

    df["resistance_rate"] = (df["resistant_count"] + 1) / (df["total_tests"] + 2)
    df["resistance_rate_ci_lower"] = df.apply(
        lambda r: max(0, r["resistance_rate"] - 1.96 * np.sqrt(
            r["resistance_rate"] * (1 - r["resistance_rate"]) / max(r["total_tests"], 1)
        )),
        axis=1
    )
    df["resistance_rate_ci_upper"] = df.apply(
        lambda r: min(1, r["resistance_rate"] + 1.96 * np.sqrt(
            r["resistance_rate"] * (1 - r["resistance_rate"]) / max(r["total_tests"], 1)
        )),
        axis=1
    )

    df["resistance_rate"] = df["resistance_rate"].round(4)
    df["resistance_rate_ci_lower"] = df["resistance_rate_ci_lower"].round(4)
    df["resistance_rate_ci_upper"] = df["resistance_rate_ci_upper"].round(4)

    return df


def query_country_antibiotic_matrix(client, limit=50000):
    """Pivot table: country x antibiotic resistance rates."""
    sql = (
        "SELECT "
        "  t.geo_loc_name AS country, "
        "  SUM(CASE WHEN LOWER(a.antibiotic) = 'meropenem' AND LOWER(a.phenotype) IN ('r', 'resistant') THEN 1 ELSE 0 END) AS meropenem_res, "
        "  SUM(CASE WHEN LOWER(a.antibiotic) = 'meropenem' AND LOWER(a.phenotype) IN ('s', 'susceptible') THEN 1 ELSE 0 END) AS meropenem_sus, "
        "  SUM(CASE WHEN LOWER(a.antibiotic) = 'ciprofloxacin' AND LOWER(a.phenotype) IN ('r', 'resistant') THEN 1 ELSE 0 END) AS ciprofloxacin_res, "
        "  SUM(CASE WHEN LOWER(a.antibiotic) = 'ciprofloxacin' AND LOWER(a.phenotype) IN ('s', 'susceptible') THEN 1 ELSE 0 END) AS ciprofloxacin_sus, "
        "  SUM(CASE WHEN LOWER(a.antibiotic) = 'cefotaxime' AND LOWER(a.phenotype) IN ('r', 'resistant') THEN 1 ELSE 0 END) AS cefotaxime_res, "
        "  SUM(CASE WHEN LOWER(a.antibiotic) = 'cefotaxime' AND LOWER(a.phenotype) IN ('s', 'susceptible') THEN 1 ELSE 0 END) AS cefotaxime_sus, "
        "  COUNT(*) AS total "
        f"FROM `{DATASET}.{TABLE}` t "
        "CROSS JOIN UNNEST(t.AST_phenotypes) AS a "
        "WHERE t.geo_loc_name IS NOT NULL "
        "  AND LOWER(a.phenotype) IN ('r', 's', 'resistant', 'susceptible') "
        "  AND LOWER(a.antibiotic) IN ('meropenem', 'ciprofloxacin', 'cefotaxime') "
        "GROUP BY country "
        "HAVING total >= 20 "
        "ORDER BY total DESC "
        f"LIMIT {limit}"
    )

    df = run_query(client, sql, limit)
    if df.empty:
        return df

    for ab in ["meropenem", "ciprofloxacin", "cefotaxime"]:
        df[f"{ab}_rate"] = (df[f"{ab}_res"] + 1) / (df[f"{ab}_res"] + df[f"{ab}_sus"] + 2)
        df[f"{ab}_rate"] = df[f"{ab}_rate"].round(4)

    return df


# =====================================================================
# Query 2: AST Enrichment
# =====================================================================
def query_ast_enrichment(client, antibiotic, limit=5000, country_filter=None):
    """Query additional isolates for a specific antibiotic."""
    ab_lower = antibiotic.lower()

    sql_parts = [
        "SELECT",
        "  t.target_acc,",
        "  t.taxgroup_name,",
        "  t.asm_acc,",
        "  LOWER(a.antibiotic) AS ab_name,",
        "  LOWER(a.phenotype) AS ab_phenotype,",
        "  t.collection_date,",
        "  t.geo_loc_name,",
        "  t.isolation_source,",
        "  t.host",
        f"FROM `{DATASET}.{TABLE}` t",
        "CROSS JOIN UNNEST(t.AST_phenotypes) AS a",
        f"WHERE LOWER(a.antibiotic) = '{ab_lower}'",
        "  AND LOWER(a.phenotype) IN ('r', 's', 'resistant', 'susceptible', 'i', 'intermediate')",
        "  AND t.asm_acc IS NOT NULL",
    ]

    if country_filter:
        sql_parts.append(f"AND t.geo_loc_name LIKE '%{country_filter}%'")

    sql_parts.append("ORDER BY t.collection_date DESC")
    sql_parts.append(f"LIMIT {limit}")

    sql = "\n".join(sql_parts)

    df = run_query(client, sql, limit)
    if df.empty:
        print(f"  No additional {antibiotic} isolates found.")
        return df

    def parse_resistance(phenotype):
        if pd.isna(phenotype):
            return np.nan
        phen = str(phenotype).lower().strip()
        if phen in ("r", "resistant"):
            return 1
        elif phen in ("s", "susceptible"):
            return 0
        elif phen in ("i", "intermediate"):
            return 0.5
        return np.nan

    df["resistant"] = df["ab_phenotype"].apply(parse_resistance)
    df["antibiotic"] = antibiotic
    df["phenotype"] = df["resistant"].apply(
        lambda x: "resistant" if x == 1 else "susceptible" if x == 0 else "intermediate"
    )

    df = df[["target_acc", "taxgroup_name", "antibiotic", "phenotype",
             "asm_acc", "resistant", "collection_date",
             "geo_loc_name", "isolation_source"]]
    df = df.dropna(subset=["resistant"])

    return df


def query_multiantibiotic_panel(client, limit=5000):
    """Query isolates with full AST panels."""
    sql = (
        "SELECT"
        "  t.target_acc, t.taxgroup_name, t.asm_acc, t.collection_date,"
        "  t.geo_loc_name, t.isolation_source, a.antibiotic, a.phenotype"
        f"FROM `{DATASET}.{TABLE}` t"
        "CROSS JOIN UNNEST(t.AST_phenotypes) AS a"
        "WHERE LOWER(a.phenotype) IN ('r', 's', 'resistant', 'susceptible')"
        "  AND t.asm_acc IS NOT NULL"
        "  AND t.taxgroup_name IN ('Escherichia coli and Shigella', 'Klebsiella pneumoniae')"
        "ORDER BY t.collection_date DESC"
        f"LIMIT {limit}"
    )

    df = run_query(client, sql, limit)
    if df.empty:
        return df

    df = df.dropna(subset=["antibiotic", "phenotype"])
    df["ab_lower"] = df["antibiotic"].str.lower()
    df["pheno_lower"] = df["phenotype"].str.lower()

    def pheno_to_num(p):
        if p in ("r", "resistant"):
            return 1
        elif p in ("s", "susceptible"):
            return 0
        return np.nan

    df["resistance"] = df["pheno_lower"].apply(pheno_to_num)

    pivot = df.pivot_table(
        index=["target_acc", "taxgroup_name", "asm_acc", "collection_date",
               "geo_loc_name", "isolation_source"],
        columns="ab_lower",
        values="resistance",
        aggfunc="first"
    ).reset_index()

    pivot.columns = [
        f"AST_{c}" if c not in ["target_acc", "taxgroup_name", "asm_acc",
                                 "collection_date", "geo_loc_name", "isolation_source"]
        else c for c in pivot.columns
    ]

    return pivot


# =====================================================================
# Main
# =====================================================================
def main():
    parser = argparse.ArgumentParser(
        description="NCBI BigQuery enrichment for BactoAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/ncbi_bigquery.py --priors
  python scripts/ncbi_bigquery.py --priors --country Kenya
  python scripts/ncbi_bigquery.py --ast-enrich --antibiotic meropenem
  python scripts/ncbi_bigquery.py --ast-enrich --antibiotic meropenem --country Kenya
  python scripts/ncbi_bigquery.py --multiantibiotic
  python scripts/ncbi_bigquery.py --all
        """
    )

    parser.add_argument("--priors", action="store_true",
                        help="Query geographic resistance prevalence (for Bayesian priors)")
    parser.add_argument("--ast-enrich", action="store_true",
                        help="Query additional AST data for existing antibiotics")
    parser.add_argument("--multiantibiotic", action="store_true",
                        help="Query full AST panels (multiple antibiotics per isolate)")
    parser.add_argument("--all", action="store_true",
                        help="Run all queries")
    parser.add_argument("--country", nargs="*", default=None,
                        help="Filter by country name(s), e.g., Kenya Nigeria")
    parser.add_argument("--antibiotic", default=None,
                        choices=TARGET_ANTIBIOTICS,
                        help="Specific antibiotic for AST enrichment")
    parser.add_argument("--limit", type=int, default=5000,
                        help="Max rows to return (default: 5000)")
    parser.add_argument("--output-dir", default=OUTPUT_DIR,
                        help="Output directory (default: data/bigquery_output)")

    args = parser.parse_args()

    print("=" * 70)
    print("  NCBI BIGQUERY ENRICHMENT FOR BACTOAI")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    if args.all:
        args.priors = True
        args.ast_enrich = True
        args.multiantibiotic = True

    if not any([args.priors, args.ast_enrich, args.multiantibiotic]):
        print("  Error: Specify --priors, --ast-enrich, --multiantibiotic, or --all")
        sys.exit(1)

    # Connect to BigQuery
    print("\n[1/3] Connecting to BigQuery...")
    try:
        client = get_bigquery_client()
        client.query("SELECT 1 AS test").result()
        print("  [OK] Connection successful")
    except Exception as e:
        print(f"  [ERROR] BigQuery connection failed: {e}")
        print("\n  Make sure credentials.json is in the project root.")
        sys.exit(1)

    results = {}

    # =================================================================
    # Query 1: Geographic Priors
    # =================================================================
    if args.priors:
        print("\n[2/3] Querying geographic resistance priors...")
        countries = args.country if args.country else None

        df_priors = query_geographic_priors(client, countries=countries, limit=args.limit)
        if not df_priors.empty:
            priors_file = os.path.join(args.output_dir, "geographic_priors.csv")
            df_priors.to_csv(priors_file, index=False)
            results["geographic_priors"] = priors_file
            print(f"  [SAVED] {priors_file} ({len(df_priors)} rows)")

            priors_json = os.path.join(args.output_dir, "geographic_priors.json")
            priors_dict = {
                f"{row['country']}__{row['antibiotic']}": row["resistance_rate"]
                for _, row in df_priors.iterrows()
            }
            with open(priors_json, "w") as f:
                json.dump(priors_dict, f, indent=2)
            print(f"  [SAVED] {priors_json}")

        df_pivot = query_country_antibiotic_matrix(client, limit=args.limit)
        if not df_pivot.empty:
            pivot_file = os.path.join(args.output_dir, "country_antibiotic_matrix.csv")
            df_pivot.to_csv(pivot_file, index=False)
            results["country_antibiotic_matrix"] = pivot_file
            print(f"  [SAVED] {pivot_file} ({len(df_pivot)} rows)")

            pivot_json = os.path.join(args.output_dir, "country_antibiotic_matrix.json")
            pivot_dict = df_pivot.set_index("country")[
                [f"{ab}_rate" for ab in ["meropenem", "ciprofloxacin", "cefotaxime"]]
            ].to_dict(orient="index")
            with open(pivot_json, "w") as f:
                json.dump(pivot_dict, f, indent=2)
            print(f"  [SAVED] {pivot_json}")

    # =================================================================
    # Query 2: AST Enrichment
    # =================================================================
    if args.ast_enrich:
        print("\n[3/3] Querying AST enrichment data...")
        antibiotics = [args.antibiotic] if args.antibiotic else TARGET_ANTIBIOTICS[:3]

        for ab in antibiotics:
            print(f"\n  --- {ab.upper()} ---")
            country_filter = args.country[0] if args.country else None
            df_enrich = query_ast_enrichment(client, ab, limit=args.limit,
                                             country_filter=country_filter)

            if not df_enrich.empty:
                enrich_file = os.path.join(args.output_dir, f"enrichment_{ab}.csv")
                df_enrich.to_csv(enrich_file, index=False)
                results[f"enrichment_{ab}"] = enrich_file
                print(f"  [SAVED] {enrich_file} ({len(df_enrich)} rows)")

                n_res = (df_enrich["resistant"] == 1).sum()
                n_sus = (df_enrich["resistant"] == 0).sum()
                print(f"  Balance: {n_res} resistant, {n_sus} susceptible")

                if "geo_loc_name" in df_enrich.columns:
                    unique_countries = df_enrich["geo_loc_name"].dropna().unique()
                    print(f"  Countries: {len(unique_countries)} unique")

    # =================================================================
    # Query 3: Multi-antibiotic Panel
    # =================================================================
    if args.multiantibiotic:
        print("\n[MULTI] Querying full AST panels...")
        df_multi = query_multiantibiotic_panel(client, limit=args.limit)

        if not df_multi.empty:
            multi_file = os.path.join(args.output_dir, "multi_antibiotic_panels.csv")
            df_multi.to_csv(multi_file, index=False)
            results["multi_antibiotic"] = multi_file
            print(f"  [SAVED] {multi_file} ({len(df_multi)} rows)")

            ast_cols = [c for c in df_multi.columns if c.startswith("AST_")]
            print(f"  Antibiotics in panels: {len(ast_cols)}")
            for col in ast_cols[:10]:
                n_nonnull = df_multi[col].notna().sum()
                print(f"    {col}: {n_nonnull} isolates")

    # =================================================================
    # Summary
    # =================================================================
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    if results:
        print(f"\n  Files saved to: {os.path.abspath(args.output_dir)}")
        for name, path in results.items():
            print(f"    {name}: {path}")

        print(f"\n  Next steps:")
        print("    1. Review the saved CSV files in data/bigquery_output/")
        print("    2. For Bayesian priors: Load geographic_priors.json in your model")
        print("    3. For enrichment: Merge with existing metadata CSVs (see guide below)")
        print("    4. Download genomes for new asm_acc values using NCBI Datasets CLI")
    else:
        print("\n  No results returned. Check your BigQuery permissions.")

    print("\n" + "=" * 70)
    print("  ENRICHMENT GUIDE")
    print("=" * 70)
    print("""
  ## Geographic Priors (geographic_priors.csv / .json)
  Use as PRIOR probabilities in Bayesian model:

    import json
    with open("data/bigquery_output/geographic_priors.json") as f:
        priors = json.load(f)
    kenya_mero_prior = priors.get(("Kenya", "meropenem"), 0.30)

  ## Country-Antibiotic Matrix (country_antibiotic_matrix.csv)
  Better for quick reference:

    import pandas as pd
    df = pd.read_csv("data/bigquery_output/country_antibiotic_matrix.csv")
    kenya_row = df[df["country"] == "Kenya"]

  ## AST Enrichment (enrichment_meropenem.csv, etc.)
  To MERGE with existing metadata (DO NOT overwrite):

    import pandas as pd
    existing = pd.read_csv("data/metadata_meropenem.csv")
    new = pd.read_csv("data/bigquery_output/enrichment_meropenem.csv")
    existing_ids = set(existing["asm_acc"])
    new_only = new[~new["asm_acc"].isin(existing_ids)]
    combined = pd.concat([existing, new_only], ignore_index=True)
    combined.to_csv("data/metadata_meropenem_v2.csv", index=False)

  ## Multi-antibiotic Panels
    df = pd.read_csv("data/bigquery_output/multi_antibiotic_panels.csv")
    # Columns: AST_meropenem, AST_ciprofloxacin, etc. (0/1)
    """)

    print(f"\n  Done! {datetime.now().strftime('%H:%M:%S')}")
    return results


if __name__ == "__main__":
    results = main()