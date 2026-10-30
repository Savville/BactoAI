#!/bin/bash
set -e
cd /mnt/c/Users/User/Documents/RESEARCH/Bacto_AI

echo "=== Setting up WSL environment ==="
# Create venv if not exists
if [ ! -d ".venv-wsl" ]; then
    python3 -m venv .venv-wsl
fi
source .venv-wsl/bin/activate

echo "Installing Python packages..."
pip install pandas numpy scikit-learn xgboost google-cloud-bigquery scipy biopython openpyxl joblib --quiet

echo "Verifying..."
python3 -c "import pandas,numpy,sklearn,xgboost; print('pandas:', pandas.__version__, 'numpy:', numpy.__version__, 'sklearn:', sklearn.__version__, 'xgboost:', xgboost.__version__)"
python3 -c "from google.cloud import bigquery; print('bigquery OK')"

echo ""
echo "=== Testing BigQuery connection ==="
python3 -c "
from google.cloud import bigquery
client = bigquery.Client.from_service_account_json('credentials.json', project='bacto-ai')
df = client.query(\"SELECT COUNT(*) as n FROM \`ncbi-pathogen-detect.pdbrowser.isolates\` WHERE geo_loc_name LIKE '%Kenya%' AND asm_acc IS NOT NULL\").result().to_dataframe()
print(f'Kenya genomes: {int(df[\"n\"].iloc[0]):,}')
"

echo ""
echo "=== Running Q24 bootstrap CIs ==="
python3 scripts/compute_q24_cis.py

echo ""
echo "=== Checking AMRFinderPlus availability ==="
which amrfinder 2>/dev/null && amrfinder --version || echo "AMRFinderPlus NOT found"
echo ""
echo "Try installing via conda:"
echo "  conda install -c bioconda amrfinderplus"
echo ""
echo "Or via Docker (if available):"
echo "  docker pull ncbitaxonomy/amrfinder"
