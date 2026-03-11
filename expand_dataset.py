"""
BactoAI — Master Data Expansion Script
Fetches multi-species + multi-antibiotic resistance data from NCBI BigQuery.

Targets:
  Species  : E. coli, Klebsiella pneumoniae, + all other Gram-negatives
  Antibiotics: meropenem (Carbapenem), ciprofloxacin (Fluoroquinolone), cefotaxime (Cephalosporin)
"""

import os
import time
import zipfile
import urllib.request
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery

# =====================================================================
# Configuration
# =====================================================================
DATA_DIR    = "data"
GENOMES_DIR = os.path.join(DATA_DIR, "genomes")
os.makedirs(GENOMES_DIR, exist_ok=True)

# Target antibiotics and their output CSV files
ANTIBIOTICS = {
    "meropenem":      os.path.join(DATA_DIR, "metadata_meropenem.csv"),
    "ciprofloxacin":  os.path.join(DATA_DIR, "metadata_ciprofloxacin.csv"),
    "cefotaxime":     os.path.join(DATA_DIR, "metadata_cefotaxime.csv"),
}

# Target minimum resistant samples per antibiotic
TARGET_RESISTANT = 300
TARGET_SUSCEPTIBLE = 300

# =====================================================================
# Connect to BigQuery
# =====================================================================
credentials_path = os.path.join(os.getcwd(), "credentials.json")
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# =====================================================================
# Helper: Download a genome FASTA by accession
# =====================================================================
def download_genome(asm_acc):
    dest_file = os.path.join(GENOMES_DIR, f"{asm_acc}.fna")
    zip_path  = os.path.join(GENOMES_DIR, f"{asm_acc}.zip")

    if os.path.exists(dest_file):
        return True  # Already downloaded

    fasta_url = (
        f"https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/"
        f"{asm_acc}/download?include_annotation_type=GENOME_FASTA"
    )
    try:
        urllib.request.urlretrieve(fasta_url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.namelist():
                if member.endswith(".fna"):
                    with zf.open(member) as src, open(dest_file, "wb") as dst:
                        dst.write(src.read())
                    break
        os.remove(zip_path)
        return True
    except Exception as e:
        print(f"    FAILED {asm_acc}: {e}")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return False


# =====================================================================
# Helper: Fetch isolates from BigQuery for ONE antibiotic
# =====================================================================
def fetch_isolates(antibiotic, phenotype, limit):
    """
    Fetches isolates of ANY Gram-negative species where the given
    antibiotic has the given phenotype ('resistant' or 'susceptible').
    """
    query = f"""
    SELECT 
        target_acc,
        taxgroup_name,
        '{antibiotic}' AS antibiotic,
        (SELECT phenotype FROM UNNEST(AST_phenotypes)
             WHERE antibiotic = '{antibiotic}' LIMIT 1) AS phenotype,
        asm_acc
    FROM `ncbi-pathogen-detect.pdbrowser.isolates`
    WHERE
        -- Gram-negative bacteria only (broad filter)
        taxgroup_name IN (
            'E.coli and Shigella',
            'Klebsiella pneumoniae',
            'Klebsiella',
            'Pseudomonas aeruginosa',
            'Acinetobacter baumannii',
            'Enterobacter cloacae',
            'Enterobacter',
            'Salmonella enterica'
        )
        AND EXISTS(
            SELECT 1 FROM UNNEST(AST_phenotypes) p
            WHERE p.antibiotic = '{antibiotic}'
            AND p.phenotype = '{phenotype}'
        )
        AND asm_acc IS NOT NULL
    LIMIT {limit};
    """
    return client.query(query).to_dataframe()


# =====================================================================
# Main Expansion Loop
# =====================================================================
all_metadata = []

for antibiotic, outfile in ANTIBIOTICS.items():
    print(f"\n{'='*55}")
    print(f"  Antibiotic: {antibiotic.upper()}")
    print(f"{'='*55}")

    # --- Fetch resistant ------------------------------------------------
    print(f"  Querying RESISTANT isolates (target ≥ {TARGET_RESISTANT})...")
    df_res = fetch_isolates(antibiotic, "resistant", TARGET_RESISTANT)
    df_res['resistant'] = 1
    print(f"  Found {len(df_res)} resistant isolates.")
    if not df_res.empty:
        breakdown = df_res['taxgroup_name'].value_counts().to_dict()
        for sp, cnt in breakdown.items():
            print(f"    {sp}: {cnt}")

    # --- Fetch susceptible -----------------------------------------------
    print(f"  Querying SUSCEPTIBLE isolates (target ≥ {TARGET_SUSCEPTIBLE})...")
    df_sus = fetch_isolates(antibiotic, "susceptible", TARGET_SUSCEPTIBLE)
    df_sus['resistant'] = 0
    print(f"  Found {len(df_sus)} susceptible isolates.")

    # --- Combine & deduplicate -------------------------------------------
    df_ab = pd.concat([df_res, df_sus], ignore_index=True)
    df_ab = df_ab.drop_duplicates(subset='asm_acc')
    df_ab.to_csv(outfile, index=False)
    print(f"  Saved {len(df_ab)} rows → {outfile}")

    # --- Download Genomes ------------------------------------------------
    print(f"\n  Downloading genomes for {len(df_ab)} isolates...")
    ok, fail = 0, 0
    for i, (_, row) in enumerate(df_ab.iterrows()):
        asm_acc = row['asm_acc']
        print(f"    [{i+1}/{len(df_ab)}] {asm_acc} ({row['phenotype']})...", end=" ", flush=True)
        success = download_genome(asm_acc)
        if success:
            size = os.path.getsize(os.path.join(GENOMES_DIR, f"{asm_acc}.fna")) // 1024
            print(f"OK ({size} KB)")
            ok += 1
        else:
            print("FAILED")
            fail += 1
        time.sleep(0.2)

    print(f"\n  Downloaded: {ok} | Failed: {fail}")
    all_metadata.append(df_ab)


# =====================================================================
# Merge all antibiotics into one master metadata file
# =====================================================================
print(f"\n{'='*55}")
print("  Building master metadata file...")
master_df = pd.concat(all_metadata, ignore_index=True)

# Flag the species clearly
master_df['is_klebsiella'] = master_df['taxgroup_name'].str.contains('Klebsiella', na=False).astype(int)
master_df['is_ecoli']      = master_df['taxgroup_name'].str.contains('coli',      na=False).astype(int)

master_out = os.path.join(DATA_DIR, "master_metadata.csv")
master_df.to_csv(master_out, index=False)

print(f"\n{'='*55}")
print("  MASTER DATASET SUMMARY")
print(f"{'='*55}")
print(f"  Total isolate-antibiotic pairs: {len(master_df)}")
print(f"  Unique genomes:                 {master_df['asm_acc'].nunique()}")
print()
for ab in ANTIBIOTICS:
    sub = master_df[master_df['antibiotic'] == ab]
    r = int((sub['resistant'] == 1).sum())
    s = int((sub['resistant'] == 0).sum())
    print(f"  {ab:<20} Resistant: {r}  |  Susceptible: {s}")

print()
by_species = master_df.groupby('taxgroup_name')['asm_acc'].nunique()
print("  Genomes by species:")
for sp, cnt in by_species.items():
    print(f"    {sp}: {cnt}")

print(f"\n  Saved master metadata → {master_out}")
print(f"\n  Next: python bactoai_pipeline_v2.py --train --metadata {master_out}")
