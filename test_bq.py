import os
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery

credentials_path = os.path.join(os.getcwd(), "credentials.json")
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

query = """
    SELECT target_acc, taxgroup_name, asm_acc
    FROM `ncbi-pathogen-detect.pdbrowser.isolates` 
    WHERE taxgroup_name LIKE '%coli%' 
    AND EXISTS(SELECT 1 FROM UNNEST(AST_phenotypes) p WHERE p.antibiotic = 'meropenem' AND p.phenotype IN ('resistant', 'susceptible'))
    LIMIT 10;
"""
df = client.query(query).to_dataframe()
print(df.head())
print("Unique taxgroups:", df['taxgroup_name'].unique() if not df.empty else "None")
