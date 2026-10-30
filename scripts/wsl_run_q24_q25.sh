#!/bin/bash
set -e
cd /mnt/c/Users/User/Documents/RESEARCH/Bacto_AI
export PATH="$HOME/.local/bin:$PATH"

echo "=== Q24: Bootstrap CIs ==="
python3 scripts/compute_q24_cis.py

echo ""
echo "=== Q25: AMRFinderPlus ==="
# Check current status
which amrfinder 2>/dev/null && amrfinder --version || echo "AMRFinderPlus: NOT INSTALLED"
echo ""

# Try to download and install AMRFinderPlus
echo "Attempting to install AMRFinderPlus..."
mkdir -p /tmp/amrfinder_install
cd /tmp/amrfinder_install

# Download latest release
curl -sL 'https://api.github.com/repos/NCBIAMRFinder/amrfinder/releases/latest' -o release.json 2>/dev/null || {
    echo "GitHub API failed, trying direct download..."
    # Fallback: known URL pattern
    curl -sL 'https://github.com/NCBIAMRFinder/amrfinder/releases/download/3.12.2/amrfinder-linux-64bit.tar.gz' -o amrfinder.tar.gz 2>/dev/null
}

# Extract and install
if [ -f release.json ]; then
    python3 -c "
import json, urllib.request, os
with open('release.json') as f:
    d = json.load(f)
for a in d.get('assets', []):
    name = a['name']
    url = a['browser_download_url']
    if 'linux' in name.lower() and 'tar' in name.lower():
        print(f'Downloading {name}...')
        urllib.request.urlretrieve(url, name)
        break
"
fi

# Find the tarball
TARBALL=$(ls amrfinder-linux*.tar.gz 2>/dev/null | head -1)
if [ -z "$TARBALL" ]; then
    TARBALL=$(ls *.tar.gz 2>/dev/null | head -1)
fi

if [ -n "$TARBALL" ]; then
    echo "Extracting $TARBALL..."
    tar xzf "$TARBALL"
    # Find the binary
    BINARY=$(find . -name 'amrfinder' -type f 2>/dev/null | head -1)
    if [ -n "$BINARY" ]; then
        echo "Installing to ~/.local/bin..."
        mkdir -p ~/.local/bin
        cp "$BINARY" ~/.local/bin/amrfinder
        chmod +x ~/.local/bin/amrfinder
        # Copy database
        DB_DIR=$(find . -name 'protein.fasta' -type d 2>/dev/null | head -1)
        if [ -n "$DB_DIR" ]; then
            cp -r "$DB_DIR" ~/.local/bin/amrfinder_db 2>/dev/null || true
        fi
        echo "AMRFinderPlus installed!"
        amrfinder --version
    else
        echo "Binary not found in tarball"
        ls -la
    fi
else
    echo "No tarball found. Listing release assets:"
    python3 -c "
import json
try:
    with open('release.json') as f:
        d = json.load(f)
    for a in d.get('assets', []):
        print(f\"  {a['name']} ({a['size']//1024} KB)\")
except:
    pass
"
fi

echo ""
echo "=== Running AMRFinderPlus on test genomes ==="
if command -v amrfinder &>/dev/null; then
    # Run on first 5 test genomes as a sample
    echo "Running on sample genomes..."
    mkdir -p validation_results/amrfinder_results
    for f in data/genomes/*.fna; do
        [ -f "$f" ] || continue
        base=$(basename "$f" .fna)
        out="validation_results/amrfinder_results/${base}.genes.txt"
        if [ ! -f "$out" ]; then
            amrfinder --upper_case_feature true "$f" --output validation_results/amrfinder_results/ --gene_output "$out" 2>/dev/null || echo "Failed: $base"
        fi
    done
    echo "Done. Results in validation_results/amrfinder_results/"
else
    echo "AMRFinderPlus not available. Skipping comparison."
    echo "To install manually:"
    echo "  conda install -c bioconda amrfinderplus"
    echo "  # OR download from: https://github.com/NCBIAMRFinder/amrfinder"
fi
