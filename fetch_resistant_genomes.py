import os
import zipfile
import urllib.request
import pandas as pd
import time
from google.oauth2 import service_account
from google.cloud import bigquery

# =====================================================================
# Config
# =====================================================================
GENOMES_DIR = os.path.join("data", "genomes")
METADATA_FILE = os.path.join("data", "Ecoli_Carbapenem_Metadata.csv")
RESISTANT_METADATA_FILE = os.path.join("data", "Ecoli_Resistant_Metadata.csv")
os.makedirs(GENOMES_DIR, exist_ok=True)

# =====================================================================
# Connect to BigQuery
# =====================================================================
credentials_path = os.path.join(os.getcwd(), "credentials.json")
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# =====================================================================
# Query: Get as many RESISTANT E.coli meropenem samples as possible
# =====================================================================
print("Querying BigQuery for RESISTANT meropenem isolates...")
query = """
SELECT 
    target_acc, 
    taxgroup_name, 
    (SELECT phenotype FROM UNNEST(AST_phenotypes) WHERE antibiotic = 'meropenem' LIMIT 1) AS meropenem_phenotype,
    asm_acc
FROM 
    `ncbi-pathogen-detect.pdbrowser.isolates` 
WHERE 
    taxgroup_name = 'E.coli and Shigella' 
    AND EXISTS(
        SELECT 1 FROM UNNEST(AST_phenotypes) p 
        WHERE p.antibiotic = 'meropenem' AND p.phenotype = 'resistant'
    )
    AND asm_acc IS NOT NULL
LIMIT 500;
"""

df_resistant = client.query(query).to_dataframe()
print(f"Found {len(df_resistant)} resistant E.coli meropenem isolates in NCBI.")

# Assign label
df_resistant['resistant'] = 1

# =====================================================================
# Merge with existing metadata (avoid duplicates)
# =====================================================================
df_existing = pd.read_csv(METADATA_FILE)
existing_accs = set(df_existing['asm_acc'].dropna().tolist())

df_new = df_resistant[~df_resistant['asm_acc'].isin(existing_accs)].copy()
print(f"New resistant isolates not yet in dataset: {len(df_new)}")

if df_new.empty:
    print("All resistant isolates are already in your dataset. Nothing to add.")
    exit()

# Save the resistant-only metadata for reference
df_new.to_csv(RESISTANT_METADATA_FILE, index=False)
print(f"Saved to {RESISTANT_METADATA_FILE}")

# =====================================================================
# Download Genomes for the new resistant isolates
# =====================================================================
print(f"\nDownloading {len(df_new)} resistant genome FASTA files...")
print("-" * 55)

failed = []
for i, (_, row) in enumerate(df_new.iterrows()):
    asm_acc = row['asm_acc']
    dest_file = os.path.join(GENOMES_DIR, f"{asm_acc}.fna")
    zip_path  = os.path.join(GENOMES_DIR, f"{asm_acc}.zip")
    fasta_url = (
        f"https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/"
        f"{asm_acc}/download?include_annotation_type=GENOME_FASTA"
    )

    if os.path.exists(dest_file):
        print(f"[{i+1}/{len(df_new)}] {asm_acc} — already exists, skipping.")
        continue

    print(f"[{i+1}/{len(df_new)}] Downloading {asm_acc} (resistant)...", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(fasta_url, zip_path)
        extracted = False
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.namelist():
                if member.endswith(".fna"):
                    with zf.open(member) as src, open(dest_file, "wb") as dst:
                        dst.write(src.read())
                    extracted = True
                    break
        os.remove(zip_path)
        if extracted:
            size_kb = os.path.getsize(dest_file) / 1024
            print(f"OK ({size_kb:.0f} KB)")
        else:
            print("WARNING: no .fna inside zip.")
            failed.append(asm_acc)
    except Exception as e:
        print(f"FAILED: {e}")
        failed.append(asm_acc)
        if os.path.exists(zip_path):
            os.remove(zip_path)

    time.sleep(0.3)

# =====================================================================
# Merge into the main metadata CSV
# =====================================================================
print("\nUpdating main metadata CSV...")
df_combined = pd.concat([df_existing, df_new], ignore_index=True)
df_combined.to_csv(METADATA_FILE, index=False)

# Final class balance report
counts = df_combined['resistant'].value_counts()
print("\n" + "=" * 45)
print("UPDATED DATASET CLASS BALANCE")
print("=" * 45)
print(f"  Susceptible (0) : {counts.get(0.0, 0)}")
print(f"  Resistant   (1) : {counts.get(1.0, 0)}")
print(f"  Total           : {len(df_combined)}")
print(f"\nFailed downloads  : {len(failed)}")
print("=" * 45)
print("\nDataset is ready. Run:  python bactoai_pipeline.py --train")
