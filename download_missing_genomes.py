import os
import zipfile
import urllib.request
import pandas as pd
import time

GENOMES_DIR = os.path.join("data", "genomes")
METADATA_FILE = os.path.join("data", "Ecoli_Carbapenem_Metadata.csv")

os.makedirs(GENOMES_DIR, exist_ok=True)

# Load metadata
df = pd.read_csv(METADATA_FILE)
df = df.dropna(subset=['asm_acc'])
total = len(df)

print(f"Total samples in metadata: {total}")

# Find what's already downloaded
downloaded = set()
for fname in os.listdir(GENOMES_DIR):
    if fname.endswith(".fna"):
        acc = fname.replace(".fna", "")
        downloaded.add(acc)

missing = [row for _, row in df.iterrows() if row['asm_acc'] not in downloaded]
failed = []

print(f"Already downloaded: {len(downloaded)}")
print(f"Missing / to download: {len(missing)}")
print("-" * 50)

for i, row in enumerate(missing):
    asm_acc = row['asm_acc']
    label = row['meropenem_phenotype']
    dest_file = os.path.join(GENOMES_DIR, f"{asm_acc}.fna")
    zip_path = os.path.join(GENOMES_DIR, f"{asm_acc}.zip")
    fasta_url = f"https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/{asm_acc}/download?include_annotation_type=GENOME_FASTA"

    print(f"[{i+1}/{len(missing)}] Downloading {asm_acc} ({label})...", end=" ", flush=True)

    try:
        urllib.request.urlretrieve(fasta_url, zip_path)

        # Unzip and extract the .fna file
        extracted = False
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith(".fna"):
                    with zip_ref.open(member) as source, open(dest_file, "wb") as target:
                        target.write(source.read())
                    extracted = True
                    break

        os.remove(zip_path)

        if extracted:
            size_kb = os.path.getsize(dest_file) / 1024
            print(f"OK ({size_kb:.0f} KB)")
        else:
            print(f"WARNING: No .fna found inside zip — skipping.")
            failed.append(asm_acc)

    except Exception as e:
        print(f"FAILED: {e}")
        failed.append(asm_acc)
        if os.path.exists(zip_path):
            os.remove(zip_path)

    # Brief pause to avoid overwhelming NCBI API
    time.sleep(0.3)

print("-" * 50)
print(f"\nDownload complete!")
print(f"  Successfully downloaded: {len(missing) - len(failed)}")
print(f"  Failed: {len(failed)}")

if failed:
    print(f"\nFailed accessions (may have no assembly):")
    for acc in failed:
        print(f"  - {acc}")

# Final count
final_count = len([f for f in os.listdir(GENOMES_DIR) if f.endswith(".fna")])
print(f"\nTotal genomes in data/genomes/: {final_count} / {total}")
