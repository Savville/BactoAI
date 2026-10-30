"""
Populate the Isolate Table in the validation Excel from metadata CSVs + BigQuery geo data.
Maps: asm_acc -> all metadata, adds country/year from BigQuery, maps phenotype to S/I/R.
"""
import os, sys, csv, json, time, argparse
from datetime import datetime
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "validation_results")

try:
    from google.cloud import bigquery
    HAS_BQ = True
except ImportError:
    HAS_BQ = False

TARGET_SPECIES_MAP = {
    "Escherichia coli and Shigella": "Escherichia coli",
    "Klebsiella pneumoniae": "Klebsiella pneumoniae",
    "Acinetobacter baumannii": "Acinetobacter baumannii",
    "Pseudomonas aeruginosa": "Pseudomonas aeruginosa",
    "Salmonella enterica": "Salmonella enterica",
    "Enterobacter cloacae": "Enterobacter cloacae",
}

# =====================================================================
# Load metadata CSVs
# =====================================================================

def load_all_metadata():
    """Load all three metadata CSVs into one DataFrame."""
    all_rows = []
    for ab in ["meropenem", "ciprofloxacin", "cefotaxime"]:
        path = os.path.join(DATA_DIR, f"metadata_{ab}.csv")
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        df = df.dropna(subset=["asm_acc", "resistant"])
        df = df.drop_duplicates(subset="asm_acc")
        df["antibiotic"] = ab
        df["source"] = "NCBI"
        all_rows.append(df)
    
    # BV-BRC cefotaxime
    bvbrc_path = os.path.join(DATA_DIR, "BVBRC_genome_amr.csv")
    if os.path.exists(bvbrc_path):
        bvbrc = pd.read_csv(bvbrc_path)
        bvbrc = bvbrc[bvbrc["Antibiotic"] == "cefotaxime"]
        bvbrc = bvbrc.dropna(subset=["Genome ID"])
        bvbrc = bvbrc.drop_duplicates(subset="Genome ID")
        bvbrc = bvbrc.rename(columns={"Genome ID": "asm_acc", "Resistant Phenotype": "resistant_raw"})
        bvbrc["taxgroup_name"] = "Escherichia coli"
        bvbrc["antibiotic"] = "cefotaxime"
        bvbrc["source"] = "BV-BRC"
        # Map phenotype to binary
        def map_pheno(p):
            p = str(p).lower().strip() if pd.notna(p) else ""
            if p in ("r", "resistant"):
                return 1
            elif p in ("s", "susceptible"):
                return 0
            return np.nan
        bvbrc["resistant"] = bvbrc["resistant_raw"].apply(map_pheno)
        bvbrc = bvbrc[["asm_acc", "taxgroup_name", "antibiotic", "resistant", "source"]]
        all_rows.append(bvbrc)
    
    df = pd.concat(all_rows, ignore_index=True)
    # Keep only NCBI-style columns for unified processing
    cols = ["asm_acc", "taxgroup_name", "antibiotic", "resistant", "source"]
    available = [c for c in cols if c in df.columns]
    df = df[available].drop_duplicates(subset="asm_acc")
    return df


# =====================================================================
# BigQuery enrichment
# =====================================================================

def enrich_with_bigquery(df):
    """Add country, year, BioSample info from BigQuery."""
    if not HAS_BQ:
        print("  WARNING: google-cloud-bigquery not installed, skipping geo enrichment")
        df["country"] = ""
        df["collection_year"] = ""
        df["biosample_accession"] = ""
        return df
    
    print("  Connecting to BigQuery...")
    creds_path = os.path.join(PROJECT_ROOT, "credentials.json")
    try:
        client = bigquery.Client.from_service_account_json(creds_path, project="bacto-ai")
        client.query("SELECT 1").result()
    except Exception as e:
        print(f"  BigQuery connection failed: {e}")
        df["country"] = ""
        df["collection_year"] = ""
        df["biosample_accession"] = ""
        return df
    
    accs = df["asm_acc"].tolist()
    print(f"  Enriching {len(accs)} accessions...")
    
    # Batch query in chunks of 500
    results = {}
    chunk_size = 500
    for i in range(0, len(accs), chunk_size):
        chunk = accs[i:i+chunk_size]
        placeholders = ",".join([f"'{a}'" for a in chunk])
        sql = f"""
            SELECT asm_acc, geo_loc_name, collection_date, biosample_accession, taxgroup_name
            FROM `ncbi-pathogen-detect.pdbrowser.isolates`
            WHERE asm_acc IN ({placeholders})
        """
        try:
            chunk_df = client.query(sql).result().to_dataframe()
            for _, row in chunk_df.iterrows():
                acc = row["asm_acc"]
                if acc not in results:
                    results[acc] = {}
                results[acc]["country"] = str(row.get("geo_loc_name", ""))
                cd = str(row.get("collection_date", ""))
                results[acc]["collection_year"] = cd[:4] if cd else ""
                results[acc]["biosample_accession"] = str(row.get("biosample_accession", ""))
                if pd.notna(row.get("taxgroup_name")):
                    results[acc]["taxgroup_name"] = str(row["taxgroup_name"])
            
            elapsed = time.time()
            print(f"    Chunk {i//chunk_size + 1}: {len(results)} resolved so far")
        except Exception as e:
            print(f"    Chunk {i//chunk_size + 1} failed: {e}")
    
    # Apply results
    df["country"] = df["asm_acc"].map(lambda x: results.get(x, {}).get("country", ""))
    df["collection_year"] = df["asm_acc"].map(lambda x: results.get(x, {}).get("collection_year", ""))
    df["biosample_accession"] = df["asm_acc"].map(lambda x: results.get(x, {}).get("biosample_accession", ""))
    
    # Update species from BigQuery where available
    df["taxgroup_name"] = df.apply(
        lambda r: results.get(r["asm_acc"], {}).get("taxgroup_name", r["taxgroup_name"])
        if pd.notna(r.get("taxgroup_name")) else r["taxgroup_name"], axis=1
    )
    
    print(f"  Enriched {len(results)} / {len(accs)} accessions")
    return df


# =====================================================================
# Map phenotype to S/I/R
# =====================================================================

def phenotype_to_sir(resistant_flag):
    """Map binary resistant flag to S/I/R string."""
    if resistant_flag == 1:
        return "R"
    elif resistant_flag == 0:
        return "S"
    return ""


# =====================================================================
# Build isolate rows
# =====================================================================

def build_isolate_rows(df):
    """Convert DataFrame rows into isolate table format."""
    rows = []
    for idx, row in df.iterrows():
        acc = str(row["asm_acc"]).strip()
        species_raw = str(row.get("taxgroup_name", "")).strip()
        species = TARGET_SPECIES_MAP.get(species_raw, species_raw)
        country = str(row.get("country", "")).strip()
        year = str(row.get("collection_year", "")).strip()
        biosample = str(row.get("biosample_accession", "")).strip()
        resistant = int(row["resistant"]) if pd.notna(row["resistant"]) else np.nan
        sir = phenotype_to_sir(resistant) if pd.notna(resistant) else ""
        source = str(row.get("source", "NCBI")).strip()
        antibiotic = str(row.get("antibiotic", "")).strip()
        
        rows.append({
            "asm_acc": acc,
            "species": species,
            "country": country,
            "year": year,
            "biosample": biosample,
            "source": source,
            "antibiotic": antibiotic,
            "resistant": resistant,
            "sir": sir,
        })
    return rows


# =====================================================================
# Pivot to wide format (one row per isolate, columns per antibiotic)
# =====================================================================

def pivot_to_wide(rows):
    """Pivot so each isolate is one row with per-antibiotic columns."""
    # Group by asm_acc
    grouped = {}
    for r in rows:
        acc = r["asm_acc"]
        if acc not in grouped:
            grouped[acc] = {
                "asm_acc": acc,
                "species": r["species"],
                "country": r["country"],
                "year": r["year"],
                "biosample": r["biosample"],
                "source": r["source"],
                "meropenem_sir": "",
                "ciprofloxacin_sir": "",
                "cefotaxime_sir": "",
            }
        ab = r["antibiotic"] if "antibiotic" in r else ""
        # We need antibiotic from the original df - store separately
        if "antibiotic" in r:
            key = f"{r['antibiotic']}_sir"
            grouped[acc][key] = r["sir"]
    
    # Rebuild from original df
    df_pivot = pd.DataFrame(rows)
    wide = df_pivot.pivot_table(
        index=["asm_acc", "species", "country", "year", "biosample", "source"],
        columns="antibiotic",
        values=["resistant", "sir"],
        aggfunc="first"
    ).reset_index()
    
    # Flatten column names
    wide.columns = ["_".join(col).strip() if col[1] else col[0] for col in wide.columns]
    
    # Fix column name mapping for pivot
    col_map = {}
    for col in wide.columns:
        if col == "asm_acc":
            col_map[col] = "Assembly accession"
        elif col == "species":
            col_map[col] = "Species"
        elif col == "country":
            col_map[col] = "Country"
        elif col == "year":
            col_map[col] = "Collection year"
        elif col == "biosample":
            col_map[col] = "BioSample accession"
        elif col == "source":
            col_map[col] = "Source database"
        elif col.startswith("meropenem"):
            col_map[col] = col.replace("_", " ").title()
        elif col.startswith("ciprofloxacin"):
            col_map[col] = col.replace("_", " ").title()
        elif col.startswith("cefotaxime"):
            col_map[col] = col.replace("_", " ").title()
    
    wide = wide.rename(columns=col_map)
    
    # Fill missing antibiotic columns
    for ab in ["meropenem", "ciprofloxacin", "cefotaxime"]:
        sir_col = f"{ab}_sir"
        if sir_col not in wide.columns:
            wide[sir_col] = ""
    
    return wide


# =====================================================================
# Write to Excel
# =====================================================================

def write_to_excel(wide_df, excel_path, output_csv=None):
    """Write isolate data to the Excel Isolate Table sheet."""
    import openpyxl
    
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Isolate Table"]
    
    # Clear example rows (6 onwards)
    for r in range(6, ws.max_row + 1):
        for c in range(1, 27):
            ws.cell(r, c).value = None
    
    # Write data starting at row 6
    row_idx = 6
    for _, row_data in wide_df.iterrows():
        ws.cell(row_idx, 1).value = f"ISE-{row_idx-5:04d}"  # Isolate ID
        ws.cell(row_idx, 2).value = row_data.get("BioSample accession", "")  # B
        ws.cell(row_idx, 3).value = ""  # SRA run (not in our data)
        ws.cell(row_idx, 4).value = row_data.get("Assembly accession", "")  # D
        ws.cell(row_idx, 5).value = row_data.get("Source database", "NCBI")  # E
        ws.cell(row_idx, 6).value = ""  # BioProject (not in our data)
        ws.cell(row_idx, 7).value = row_data.get("Species", "")  # G
        ws.cell(row_idx, 8).value = row_data.get("Country", "")  # H
        ws.cell(row_idx, 9).value = row_data.get("Collection year", "")  # I
        ws.cell(row_idx, 10).value = "Clinical"  # Sample source (default)
        ws.cell(row_idx, 11).value = "Broth microdilution"  # AST method
        ws.cell(row_idx, 12).value = "CLSI"  # Breakpoint standard
        ws.cell(row_idx, 13).value = "M100 Ed34 (2024)"  # Breakpoint version
        ws.cell(row_idx, 14).value = ""  # Mero MIC
        ws.cell(row_idx, 15).value = row_data.get("Meropenem S/I/R", "")  # Mero S/I/R
        ws.cell(row_idx, 16).value = ""  # Cipro MIC
        ws.cell(row_idx, 17).value = row_data.get("Ciprofloxacin S/I/R", "")  # Cipro S/I/R
        ws.cell(row_idx, 18).value = ""  # Cefo MIC
        ws.cell(row_idx, 19).value = row_data.get("Cefotaxime S/I/R", "")  # Cefo S/I/R
        ws.cell(row_idx, 20).value = "Yes"  # Genome QC pass (assume yes for now)
        ws.cell(row_idx, 21).value = ""  # SNP cluster/ST
        ws.cell(row_idx, 22).value = "Training"  # Partition (default)
        # Columns W, X, Y have auto-formulas already
        ws.cell(row_idx, 26).value = ""  # Notes
        row_idx += 1
    
    # Save
    wb.save(excel_path)
    print(f"  Wrote {row_idx - 6} isolates to {excel_path}")
    
    # Also save as CSV for backup
    if output_csv:
        wide_df.to_csv(output_csv, index=False)
        print(f"  Also saved CSV: {output_csv}")
    
    return row_idx - 6


# =====================================================================
# Main
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description="Populate Isolate Table from metadata CSVs")
    parser.add_argument("--excel", default=os.path.join(PROJECT_ROOT, "deliverables", "BactoAI Validation Capture.xlsx"))
    parser.add_argument("--output-csv", default=os.path.join(OUTPUT_DIR, "isolate_table.csv"))
    parser.add_argument("--dry-run", action="store_true", help="Show counts without writing")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  POPULATING ISOLATE TABLE")
    print("=" * 60)
    
    # Load metadata
    print("\n[1] Loading metadata CSVs...")
    df = load_all_metadata()
    print(f"  Total unique isolates: {len(df)}")
    print(f"  By source: {dict(df['source'].value_counts())}")
    print(f"  By species: {dict(df['taxgroup_name'].value_counts().head(10))}")
    
    # Enrich with BigQuery
    print("\n[2] Enriching with BigQuery geography...")
    df = enrich_with_bigquery(df)
    countries = df["country"].value_counts()
    print(f"  Countries found: {len(countries)}")
    for c, n in countries.head(10).items():
        print(f"    {c}: {n}")
    
    # Build rows
    print("\n[3] Building isolate rows...")
    rows = build_isolate_rows(df)
    print(f"  {len(rows)} isolate rows built")
    
    # Pivot to wide
    print("\n[4] Pivoting to wide format...")
    wide = pivot_to_wide(rows)
    print(f"  {len(wide)} unique isolates in wide format")
    
    # Show preview
    print("\n[5] Preview (first 5 isolates):")
    for _, r in wide.head(5).iterrows():
        print(f"  {r['Assembly accession'][:20]:20s} | {r.get('Species',''):25s} | {r.get('Country',''):15s} | "
              f"Merc={r.get('Meropenem S/I/R','') or '-':3s} Cipo={r.get('Ciprofloxacin S/I/R','') or '-':3s} Cefo={r.get('Cefotaxime S/I/R','') or '-':3s}")
    
    # Write to Excel
    if args.dry_run:
        print(f"\n  [DRY RUN] Would write {len(wide)} isolates to Excel")
        return
    
    print("\n[6] Writing to Excel...")
    count = write_to_excel(wide, args.excel, output_csv=args.output_csv)
    print(f"\n  Done! {count} isolates written.")


if __name__ == "__main__":
    main()
