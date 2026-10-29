"""Fast Kenya audit — no per-isolate loop."""
import os, json
from google.cloud import bigquery

creds = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
client = bigquery.Client.from_service_account_json(creds, project="bacto-ai")

queries = {
    "kenya_total": "SELECT COUNT(DISTINCT t.asm_acc) as n FROM `ncbi-pathogen-detect.pdbrowser.isolates` t WHERE t.geo_loc_name LIKE '%Kenya%' AND t.asm_acc IS NOT NULL",
    "kenya_ab": """SELECT LOWER(a.antibiotic) AS ab, COUNT(DISTINCT t.asm_acc) as n_genomes, COUNT(*) as n_records,
        SUM(CASE WHEN LOWER(a.phenotype) IN ('r','resistant') THEN 1 ELSE 0 END) as n_res,
        SUM(CASE WHEN LOWER(a.phenotype) IN ('s','susceptible') THEN 1 ELSE 0 END) as n_sus
        FROM `ncbi-pathogen-detect.pdbrowser.isolates` t
        CROSS JOIN UNNEST(t.AST_phenotypes) AS a
        WHERE t.geo_loc_name LIKE '%Kenya%' AND t.asm_acc IS NOT NULL
        AND LOWER(a.antibiotic) IN ('meropenem','ciprofloxacin','cefotaxime')
        AND LOWER(a.phenotype) IN ('r','s','resistant','susceptible')
        GROUP BY LOWER(a.antibiotic)""",
    "ea_total": "SELECT COUNT(DISTINCT t.asm_acc) as n FROM `ncbi-pathogen-detect.pdbrowser.isolates` t WHERE t.geo_loc_name LIKE '%Kenya%' OR t.geo_loc_name LIKE '%Uganda%' OR t.geo_loc_name LIKE '%Tanzania%' OR t.geo_loc_name LIKE '%Ethiopia%' OR t.geo_loc_name LIKE '%Rwanda%' AND t.asm_acc IS NOT NULL",
    "af_total": "SELECT COUNT(DISTINCT t.asm_acc) as n FROM `ncbi-pathogen-detect.pdbrowser.isolates` t WHERE t.geo_loc_name LIKE '%Kenya%' OR t.geo_loc_name LIKE '%Nigeria%' OR t.geo_loc_name LIKE '%South Africa%' OR t.geo_loc_name LIKE '%Ghana%' OR t.geo_loc_name LIKE '%Zambia%' OR t.geo_loc_name LIKE '%Tunisia%' OR t.geo_loc_name LIKE '%Egypt%' AND t.asm_acc IS NOT NULL",
    "top_countries": """SELECT t.geo_loc_name, COUNT(DISTINCT t.asm_acc) as n FROM `ncbi-pathogen-detect.pdbrowser.isolates` t
        WHERE t.geo_loc_name LIKE '%Kenya%' OR t.geo_loc_name LIKE '%Nigeria%' OR t.geo_loc_name LIKE '%South Africa%' OR t.geo_loc_name LIKE '%Ghana%' OR t.geo_loc_name LIKE '%Zambia%' OR t.geo_loc_name LIKE '%Tunisia%' OR t.geo_loc_name LIKE '%Egypt%' OR t.geo_loc_name LIKE '%Ethiopia%' OR t.geo_loc_name LIKE '%Tanzania%' OR t.geo_loc_name LIKE '%Uganda%' OR t.geo_loc_name LIKE '%Rwanda%'
        AND t.asm_acc IS NOT NULL GROUP BY t.geo_loc_name ORDER BY n DESC LIMIT 15""",
    "kenya_species": """SELECT t.taxgroup_name, COUNT(DISTINCT t.asm_acc) as n FROM `ncbi-pathogen-detect.pdbrowser.isolates` t
        WHERE t.geo_loc_name LIKE '%Kenya%' AND t.asm_acc IS NOT NULL
        GROUP BY t.taxgroup_name ORDER BY n DESC""",
}

results = {}
for name, sql in queries.items():
    df = client.query(sql).result().to_dataframe()
    if df.empty:
        results[name] = 0
    elif "ab" in df.columns:
        results[name] = {row["ab"]: dict(row) for _, row in df.iterrows()}
    elif "geo_loc_name" in df.columns:
        results[name] = {row["geo_loc_name"]: int(row["n"]) for _, row in df.iterrows()}
    elif "taxgroup_name" in df.columns:
        results[name] = {row["taxgroup_name"]: int(row["n"]) for _, row in df.iterrows()}
    else:
        results[name] = int(df.iloc[0]["n"])

# Save
out = os.path.join(os.path.dirname(__file__), "..", "data", "kenya_audit_fast.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)

print("Results saved to", out)
for k, v in results.items():
    print(f"  {k}: {v}")
