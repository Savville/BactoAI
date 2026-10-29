"""
Fill the BactoAI Validation Capture Excel with answers from our analysis.
Updates the 'Guiding Questions' sheet (column E = Team response, column G = Status).
"""
import openpyxl
import json
import os
from datetime import datetime

# Load audit results
audit = json.load(open('data/kenya_audit_fast.json'))

# Key numbers
kenya_total = audit['kenya_total']  # 8462
kenya_ab = audit['kenya_ab']  # per-antibiotic
ea_total = audit['ea_total']  # 17173
af_total = audit['af_total']  # 33483
top_countries = audit['top_countries']
kenya_species = audit['kenya_species']

# Training set sizes
training_counts = {
    'meropenem': {'total': 600, 'resistant': 300, 'susceptible': 300},
    'ciprofloxacin': {'total': 600, 'resistant': 300, 'susceptible': 300},
    'cefotaxime_v3': {'total': 600, 'resistant': 300, 'susceptible': 300},
    'cefotaxime_v4_combined': {'total': 4019, 'resistant': 684, 'susceptible': 3335},
}

wb = openpyxl.load_workbook('deliverables/BactoAI Validation Capture.xlsx')
ws = wb['Guiding Questions']

# Helper to write answer
def set_answer(row, answer, status='Complete', evidence='', responsible='BactoAI Team', date=None):
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    ws.cell(row=row, column=5).value = answer  # E = Team response
    ws.cell(row=row, column=6).value = evidence  # F = Evidence
    ws.cell(row=row, column=7).value = status  # G = Status
    ws.cell(row=row, column=8).value = responsible  # H = Responsible
    ws.cell(row=row, column=9).value = date  # I = Date answered

# =====================================================================
# Q1 - Species coverage
# =====================================================================
q1_answer = (
    "One model per antibiotic (cross-species), not per species-drug pair. "
    "Species included:\n"
    "- Meropenem: A. baumannii (98), K. pneumoniae (152), E. coli/Shigella (198), "
    "P. aeruginosa (63), S. enterica (87), E. cloacae (2) = 600 isolates\n"
    "- Ciprofloxacin: E. coli/Shigella (287), S. enterica (133), A. baumannii (86), "
    "K. pneumoniae (54), P. aeruginosa (39), E. cloacae (1) = 600 isolates\n"
    "- Cefotaxime v4: E. coli/Shigella (222 NCBI + 3,419 BV-BRC), K. pneumoniae (219), "
    "A. baumannii (114), S. enterica (43), P. aeruginosa (1), E. cloacae (1) = 4,019 isolates\n"
    "See: data/metadata_*.csv, bactoai_pipeline.py, BVBRC_INTEGRATION_AND_VALIDATION_REPORT.md"
)
set_answer(5, q1_answer, 'Complete', 'metadata CSVs, pipeline code, BVBRC report')

# =====================================================================
# Q2 - Turnaround time
# =====================================================================
q2_answer = (
    "'Under ten minutes' = computational prediction time from assembled genome (FASTA) to resistance call. "
    "Specifically: k-mer extraction, feature vectorization, and inference through 5-model deep ensemble. "
    "Observed: 8-thread parallel inference on 500 genomes completed in 45 seconds (0.09s/genome). "
    "Single genome prediction: <1 second.\n\n"
    "Realistic total sample-to-result:\n"
    "1. Culture/isolation: 1-2 days\n"
    "2. DNA extraction: 2-4 hours\n"
    "3. WGS (Illumina): 12-36 hours; (Nanopore MinION): 2-8 hours\n"
    "4. Assembly: 30 min - 2 hours\n"
    "5. BactoAI prediction: <1 minute\n"
    "Total: ~2-4 days (vs 3-5 days for conventional phenotypic AST).\n"
    "See: bactoai_pipeline.py (predict_genome function timing), README.md"
)
set_answer(6, q2_answer, 'Complete', 'bactoai_pipeline.py, README.md')

# =====================================================================
# Q3 - Sequencing platform
# =====================================================================
q3_answer = (
    "Accepts: FASTA (.fna, .fasta), including gzip-compressed (.fna.gz). "
    "Input: assembled contigs (not raw reads). Platform-agnostic — training data includes "
    "both Illumina short-read and Nanopore long-read assemblies.\n\n"
    "NPHL compatibility: NPHL uses Illumina MiSeq and NextSeq, producing assembled genomes "
    "in FASTA format. Fully compatible.\n"
    "See: bactoai_pipeline.py read_fasta(), templates/index.html"
)
set_answer(7, q3_answer, 'Complete', 'bactoai_pipeline.py, app.py')

# =====================================================================
# Q4 - Other antibiotics
# =====================================================================
q4_answer = (
    "Currently deployed: meropenem, ciprofloxacin, cefotaxime only. "
    "These three were selected for clinical priority in Kenya/East Africa:\n"
    "- Meropenem: last-line carbapenem; carbapenem resistance = WHO Priority 1 Critical threat\n"
    "- Ciprofloxacin: first-line for many Gram-negatives; resistance >60% in LMIC hospitals\n"
    "- Cefotaxime: widely used empiric therapy; ESBL-mediated resistance expanding rapidly\n\n"
    "Roadmap includes expansion to: ceftriaxone, ceftazidime, gentamicin, amikacin, colistin. "
    "See: DATASET_ORGANISMS_AND_AMR_ACQUISITION_STRATEGY.md, ROADMAP.md"
)
set_answer(8, q4_answer, 'Complete', 'DATASET_ORGANISMS_AND_AMR_ACQUISITION_STRATEGY.md, roadmap')

# =====================================================================
# Q5 - NCBI resources
# =====================================================================
q5_answer = (
    "Sources:\n"
    "1. NCBI Pathogen Detection AST Browser (ncbi.nlm.nih.gov/pathogens/ast) — primary source, 600 isolates/drug\n"
    "2. NCBI Isolates Browser (ncbi.nlm.nih.gov/pathogens/isolates) — metadata, SNP clusters, country\n"
    "3. NCBI SRA and GenBank — genome assemblies via accession (GCA_* in metadata CSVs)\n"
    "4. Google BigQuery on ncbi-pathogen-detect dataset (scripts/ncbi_bigquery.py) — geographic priors\n\n"
    "Filters: target antibiotics (meropenem, ciprofloxacin, cefotaxime), Gram-negative pathogens "
    "(taxon IDs for E. coli, K. pneumoniae, A. baumannii, P. aeruginosa, S. enterica), "
    "S/I/R phenotype labels.\n\n"
    "Download dates: NCBI batch mid-2026 (pipeline header: Created 2026-07-22); "
    "BV-BRC batch September 2026.\n"
    "See: scripts/ncbi_bigquery.py, data/metadata_*.csv"
)
set_answer(9, q5_answer, 'Complete', 'scripts/ncbi_bigquery.py, metadata CSVs, pipeline header')

# =====================================================================
# Q6 - Isolate counts
# =====================================================================
q6_answer = (
    "Per antibiotic (NCBI batch, post-cleaning):\n"
    "| Drug | Downloaded | After cleaning | Resistant | Susceptible |\n"
    "|---|---|---|---|---|\n"
    f"| Meropenem | ~600 | {training_counts['meropenem']['total']} | {training_counts['meropenem']['resistant']} | {training_counts['meropenem']['susceptible']} |\n"
    f"| Ciprofloxacin | ~600 | {training_counts['ciprofloxacin']['total']} | {training_counts['ciprofloxacin']['resistant']} | {training_counts['ciprofloxacin']['susceptible']} |\n"
    f"| Cefotaxime (NCBI v3) | ~600 | {training_counts['cefotaxime_v3']['total']} | {training_counts['cefotaxime_v3']['resistant']} | {training_counts['cefotaxime_v3']['susceptible']} |\n"
    f"| Cefotaxime (BV-BRC) | 6,260 raw | 3,419 after cleaning | 384 | 3,035 |\n"
    f"| Cefotaxime (combined v4) | -- | {training_counts['cefotaxime_v4_combined']['total']} | {training_counts['cefotaxime_v4_combined']['resistant']} | {training_counts['cefotaxime_v4_combined']['susceptible']} |\n\n"
    f"Total unique isolates: ~1,800 NCBI + 3,419 BV-BRC = ~5,219 (with NCBI cefotaxime counted once).\n"
    f"The '1,800+' claim refers to the NCBI batch. With BV-BRC integration, total exceeds 5,200.\n"
    "See: data/training_summary_v3.csv, data/training_summary_v4.csv, BVBRC_INTEGRATION_AND_VALIDATION_REPORT.md"
)
set_answer(10, q6_answer, 'Complete', 'training_summary CSVs, BVBRC report')

# =====================================================================
# Q7 - Countries and African/Kenyan counts (UPDATED WITH ACTUAL DATA)
# =====================================================================
q7_answer = (
    f"Countries represented (from BigQuery cross-reference of training set): "
    f"USA, UK, Netherlands, Germany, Canada, Mexico, Tunisia, Nigeria, South Africa, "
    f"Zambia, Egypt, Israel, Pakistan, Brazil, Australia, Thailand, Hong Kong, Vietnam, "
    f"Norway, Ireland, Greece, Algeria, Nepal, Jordan, Taiwan, Dominican Republic, plus others.\n\n"
    f"=== AFRICAN ISOLATES IN TRAINING SET (exact counts from BigQuery cross-reference) ===\n"
    f"Total African isolates in training: 52 / 1,673 unique asm_acc (3.1%)\n"
    f"  - Kenya: 2 isolates (K. pneumoniae, Nairobi)\n"
    f"  - South Africa: 8 isolates (K. pneumoniae, E. coli, Enterobacter)\n"
    f"  - Tunisia: 32 isolates (K. pneumoniae, Sfax)\n"
    f"  - Nigeria: 9 isolates (K. pneumoniae, S. enterica)\n"
    f"  - Algeria: 1 isolate (E. coli, Batna)\n\n"
    f"=== PUBLICLY AVAILABLE KENYAN DATA (BigQuery, Oct 2026) ===\n"
    f"Kenya genomes with ANY AST in NCBI BigQuery: {kenya_total:,}\n"
    f"  - Strict 'Kenya': {top_countries.get('Kenya', 0):,} genomes\n"
    f"  - 'Kenya: Nairobi': {top_countries.get('Kenya: Nairobi', 0):,} genomes\n"
    f"  - Total Kenya (all locs): {kenya_total:,}\n\n"
    f"Kenya by target species (in BigQuery):\n"
    f"  - E. coli and Shigella: {kenya_species.get('E.coli and Shigella', 0):,}\n"
    f"  - Klebsiella pneumoniae: {kenya_species.get('Klebsiella pneumoniae', 0):,}\n"
    f"  - Salmonella enterica: {kenya_species.get('Salmonella enterica', 0):,}\n"
    f"  - Pseudomonas aeruginosa: {kenya_species.get('Pseudomonas aeruginosa', 0):,}\n"
    f"  - Acinetobacter baumannii: {kenya_species.get('Acinetobacter baumannii', 0):,}\n\n"
    f"Kenya AST for target antibiotics (BigQuery):\n"
    f"  - Meropenem: {kenya_ab['meropenem']['n_genomes']} genomes ({kenya_ab['meropenem']['n_res']}R/{kenya_ab['meropenem']['n_sus']}S)\n"
    f"  - Ciprofloxacin: {kenya_ab['ciprofloxacin']['n_genomes']} genomes ({kenya_ab['ciprofloxacin']['n_res']}R/{kenya_ab['ciprofloxacin']['n_sus']}S)\n"
    f"  - Cefotaxime: {kenya_ab['cefotaxime']['n_genomes']} genomes ({kenya_ab['cefotaxime']['n_res']}R/{kenya_ab['cefotaxime']['n_sus']}S)\n\n"
    f"East Africa total (Kenya+Uganda+Tanzania+Ethiopia+Rwanda): {ea_total:,} genomes\n"
    f"All Africa (13 countries): {af_total:,} genomes\n\n"
    f"NEW Kenyan isolates available for retraining: ~{kenya_total - 9:,} (our training has only 2)\n"
    f"See: scripts/lookup_kenya_training.py, scripts/kenya_audit_fast.py, data/kenya_audit_fast.json"
)
set_answer(11, q7_answer, 'Complete', 'scripts/lookup_kenya_training.py, kenya_audit_fast.json')

# =====================================================================
# Q8 - Input type and pipeline
# =====================================================================
q8_answer = (
    "Input: Pre-assembled genomes in FASTA format (.fna, .fasta, .fna.gz). "
    "Assemblies downloaded from NCBI GenBank (GCA_* accessions) and BV-BRC REST API. "
    "No raw read processing.\n\n"
    "Pipeline versions:\n"
    "- Python 3.12\n"
    "- Biopython (SeqIO for FASTA parsing)\n"
    "- scikit-learn CountVectorizer (k-mer tokenization, k=5)\n"
    "- scikit-learn SelectKBest (chi-squared, top 50,000 features)\n"
    "- XGBoost 2.1.3, Random Forest, LightGBM as classifiers\n"
    "- scikit-learn CalibratedClassifierCV (Platt sigmoid, 5-fold CV)\n"
    "- imbalanced-learn SMOTE for class rebalancing\n"
    "See: bactoai_pipeline.py, requirements-ml.txt, Dockerfile"
)
set_answer(12, q8_answer, 'Complete', 'bactoai_pipeline.py, requirements-ml.txt')

# =====================================================================
# Q9 - Non-NCBI data
# =====================================================================
q9_answer = (
    "Yes. BV-BRC (formerly PATRIC) was used as a second data source for cefotaxime:\n"
    "- File: data/BVBRC_genome_amr.csv (6,260 raw entries)\n"
    "- Organism: Escherichia coli (NCBI Taxon ID 562)\n"
    "- Downloaded via BV-BRC REST API (scripts/download_bvbrc_genomes.py)\n"
    "- 3,419 deduplicated records merged into combined cefotaxime training set (v4)\n"
    "- 3,419 full FASTA chromosomes saved to data/bvbrc_genomes/\n\n"
    "Potential but NOT yet used:\n"
    "- Liverpool E. coli WGS-AST dataset (762 isolates, 2025)\n"
    "- Moradigaravand et al. (2018) E. coli collection (~1,900 UK isolates)\n"
    "- Nguyen et al. (2018) K. pneumoniae MIC set (~1,600 isolates)\n"
    "- KEMRI partnerships (not yet established — requires MOU)\n"
    "See: BVBRC_INTEGRATION_AND_VALIDATION_REPORT.md, scripts/download_bvbrc_genomes.py"
)
set_answer(13, q9_answer, 'Complete', 'BVBRC report, download script')

# =====================================================================
# Q10 - AST methods
# =====================================================================
q10_answer = (
    "Two methods present:\n"
    "1. Broth microdilution (MIC): Used in NCBI batch (all three drugs, 600 isolates each)\n"
    "2. Disk diffusion (zone diameter in mm): Used in BV-BRC batch (cefotaxime only, 3,419 isolates)\n\n"
    "The cefotaxime v4 model is trained on mixed-modality data. "
    "Meropenem and ciprofloxacin models use only MIC-derived labels.\n"
    "See: data/BVBRC_genome_amr.csv (Laboratory Typing Method column), BVBRC report"
)
set_answer(14, q10_answer, 'Complete', 'BVBRC CSV columns, metadata CSVs')

# =====================================================================
# Q11 - Breakpoint standard
# =====================================================================
q11_answer = (
    "- BV-BRC (disk diffusion): EUCAST clinical breakpoints for Enterobacterales vs cefotaxime:\n"
    "  Resistant: zone diameter <= 17 mm\n"
    "  Intermediate: 18-25 mm (mapped to Resistant)\n"
    "  Susceptible: zone diameter >= 26 mm\n"
    "- NCBI data: Pre-classified S/I/R labels from NCBI Pathogen Detection AST Browser. "
    "The specific breakpoint standard and version used by original submitters varies by record "
    "and has NOT been re-harmonized to a single version.\n\n"
    "> WARNING: For formal validation, all labels should be re-interpreted using one standard "
    "and version (e.g., EUCAST v14.0 or CLSI M100 Ed34).\n"
    "See: bactoai_pipeline.py (parse_resistance function), validation guidance"
)
set_answer(15, q11_answer, 'Complete', 'bactoai_pipeline.py, metadata CSVs')

# =====================================================================
# Q12 - Intermediate/missing/conflicting
# =====================================================================
q12_answer = (
    "- Intermediate results: Mapped to Resistant (clinical default policy, "
    "documented in validation JSON as intermediate_policy: resistant)\n"
    "- Missing values: Rows with missing asm_acc or resistant fields are dropped "
    "(metadata_df.dropna(subset=['asm_acc', 'resistant']))\n"
    "- Duplicates: De-duplicated by assembly accession "
    "(metadata_df.drop_duplicates(subset='asm_acc'))\n"
    "- Conflicting records: Not explicitly handled. First occurrence retained after deduplication.\n"
    "See: bactoai_pipeline.py extract_features()"
)
set_answer(16, q12_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q13 - Genome QC
# =====================================================================
q13_answer = (
    "- The pipeline checks whether a genome file exists and is readable "
    "(read_fasta() returns empty string on failure)\n"
    "- Genomes that cannot be parsed or are empty are skipped\n"
    "- No explicit thresholds for contamination, completeness, contig count or genome size\n\n"
    "> GAP: Formal genome QC (e.g., CheckM for completeness/contamination, species confirmation) "
    "is not currently implemented. Should be added before formal validation.\n"
    "See: bactoai_pipeline.py read_fasta(), validate_genome_file()"
)
set_answer(17, q13_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q14 - Input features
# =====================================================================
q14_answer = (
    "Two feature types:\n"
    "1. K-mer frequencies (k=5): Each genome decomposed into all 5-character substrings. "
    "CountVectorizer tokenizes, then SelectKBest(chi2) selects top 50,000 most informative k-mers. "
    "For v4 cefotaxime model, 1,321 unique 5-mers passed chi-squared test.\n"
    "2. AMR gene signature features (18 binary features): Presence/absence of known resistance "
    "gene k-mer markers covering:\n"
    "  - Carbapenemases: blaKPC, blaNDM, blaVIM, blaIMP, blaOXA-48\n"
    "  - Penicillinases: blaTEM, blaSHV\n"
    "  - Cephalosporinases: blaCTX-M, blaPER, blaACC\n"
    "  - Fluoroquinolone: gyrA mutations, parC mutations\n"
    "  - Efflux pumps: acrAB, ramA\n"
    "  - MLS: ermB, mphA\n"
    "  - Aminoglycoside: aac(6')-I, aph(3')\n"
    "Combined: k-mer counts + gene signatures via scipy.sparse.hstack\n"
    "See: bactoai_pipeline.py build_kmers(), extract_gene_signatures()"
)
set_answer(18, q14_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q15 - Algorithm
# =====================================================================
q15_answer = (
    "Soft-voting ensemble of three classifiers:\n"
    "1. XGBoost (300 estimators, max depth 6, learning rate 0.05)\n"
    "2. Random Forest (200 estimators, max depth 10, balanced class weights)\n"
    "3. LightGBM (300 estimators, max depth 6, learning rate 0.05)\n\n"
    "Each wrapped in CalibratedClassifierCV(method='sigmoid', cv=5) for Platt scaling. "
    "Deep ensemble of 5 such calibrated models (seeds: 42, 123, 456, 789, 1024) provides "
    "uncertainty estimation through prediction variance.\n"
    "See: bactoai_pipeline.py train_deep_ensemble()"
)
set_answer(19, q15_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q16 - Class imbalance
# =====================================================================
q16_answer = (
    "- SMOTE (Synthetic Minority Over-sampling): Applied when minority class < 60% of majority, "
    "using imblearn.over_sampling.SMOTE(k_neighbors=min(5, n_pos-1))\n"
    "- Scale weighting: XGBoost uses scale_pos_weight = n_neg/n_pos; "
    "Random Forest uses class_weight='balanced'; LightGBM uses scale_pos_weight\n"
    "- Balanced training data: NCBI batch curated at 300 R / 300 S per drug (perfectly balanced). "
    "SMOTE applied for combined cefotaxime set (684 R vs 3,335 S).\n"
    "See: bactoai_pipeline.py"
)
set_answer(20, q16_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q17 - Hyperparameter tuning
# =====================================================================
q17_answer = (
    "Hyperparameters are currently FIXED (not tuned via grid search or Bayesian optimization):\n"
    "- XGBoost: n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8, "
    "colsample_bytree=0.8\n"
    "- Random Forest: n_estimators=200, max_depth=10\n"
    "- LightGBM: n_estimators=300, max_depth=6, learning_rate=0.05\n"
    "- Feature selection: SelectKBest(chi2, k=50,000+18)\n\n"
    "5-fold CV in CalibratedClassifierCV applied within training partition only. "
    "25% test holdout not used during hyperparameter selection or calibration.\n"
    "See: bactoai_pipeline.py train_deep_ensemble()"
)
set_answer(21, q17_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q18 - Test set sizes
# =====================================================================
q18_answer = (
    "| Drug | Total | Train | Test | Test proportion |\n"
    "|---|---|---|---|---|\n"
    f"| Meropenem (v3) | ~{training_counts['meropenem']['total']} | ~373 | 125 (69R, 56S) | 25% |\n"
    f"| Ciprofloxacin (v3) | ~{training_counts['ciprofloxacin']['total']} | ~430 | 140 (68R, 72S) | 25% |\n"
    f"| Cefotaxime (v3, NCBI only) | ~{training_counts['cefotaxime_v3']['total']} | ~435 | 145 (71R, 74S) | 25% |\n"
    f"| Cefotaxime (v4, combined) | {training_counts['cefotaxime_v4_combined']['total']} | 2,997 | 1,000 (167R, 833S) | 25% |\n"
    "See: data/training_summary_v3.csv, data/training_summary_v4.csv, validation_results/threshold_audit_*.json"
)
set_answer(22, q18_answer, 'Complete', 'training_summary CSVs, threshold audit JSONs')

# =====================================================================
# Q19 - Split method
# =====================================================================
q19_answer = (
    "The split is RANDOM, using train_test_split(test_size=0.25, random_state=42, stratify=y). "
    "Stratification preserves the S/R class ratio in both sets.\n\n"
    "Related isolates (same SNP cluster, sequence type or clade) are NOT kept together. "
    "The pipeline does not use phylogenetic or SNP-cluster-aware splitting.\n\n"
    "> GAP: A relatedness-aware split has not been performed. Random splits can inflate AUC "
    "when near-clonal isolates appear in both training and test sets. Re-computing AUC under "
    "a phylogeny-aware or sequence-type-aware split is required before formal validation.\n"
    "See: bactoai_pipeline.py train_deep_ensemble()"
)
set_answer(23, q19_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q20 - No overlap confirmation
# =====================================================================
q20_answer = (
    "De-duplication by assembly accession (drop_duplicates(subset='asm_acc')) occurs before splitting. "
    "train_test_split partitions the de-duplicated list, so no accession appears in both sets "
    "within a single drug model.\n\n"
    "Cross-dataset overlap between NCBI and BV-BRC was checked by accession format: NCBI uses "
    "GCA_* prefixes while BV-BRC uses 562.* genome IDs, so namespaces do not collide. "
    "However, BioSample-level de-duplication (checking whether the same physical isolate was "
    "deposited in both databases) has NOT yet been done.\n"
    "See: bactoai_pipeline.py extract_features()"
)
set_answer(24, q20_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q21 - Preprocessing fitted on full dataset
# =====================================================================
q21_answer = (
    "No. In extract_features(), CountVectorizer.fit_transform() and SelectKBest.fit_transform() "
    "are called on the training partition only. The test set is transformed with the fitted "
    "vectorizer and selector (.transform(), not .fit_transform()).\n\n"
    "The split happens via train_test_split() in train_deep_ensemble(), and feature extraction "
    "parameters are fitted on X_tr only.\n"
    "See: bactoai_pipeline.py"
)
set_answer(25, q21_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q22 - Test set used once
# =====================================================================
q22_answer = (
    "The internal test holdout is evaluated at the end of training for each of the 5 ensemble members. "
    "All model architecture and hyperparameter choices are fixed before training begins (no iterative "
    "tuning on the test set). However, the same holdout data was used for:\n"
    "- Per-model AUC reporting\n"
    "- Overall ensemble AUC reporting\n"
    "- Calibration score computation for conformal prediction\n\n"
    "The test set was not used to select hyperparameters or features.\n"
    "See: bactoai_pipeline.py train_deep_ensemble()"
)
set_answer(26, q22_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q23 - Cipro vs Cefo AUC confirmation
# =====================================================================
q23_answer = (
    "From data/training_summary_v3.csv:\n"
    "| Drug | ROC-AUC |\n"
    "|---|---|\n"
    "| Meropenem | 0.9415 |\n"
    "| Ciprofloxacin | 0.8791 |\n"
    "| Cefotaxime | 0.8721 |\n\n"
    "The two values are NOT identical: ciprofloxacin = 0.8791, cefotaxime = 0.8721. "
    "They were rounded to 0.87 in the draft letter, producing the appearance of identical figures.\n\n"
    "For cefotaxime v4 (retrained on 4,019 genomes): internal AUC = 0.7793, "
    "external BV-BRC validation AUC = 0.9333.\n"
    "See: data/training_summary_v3.csv, validation_results/bvbrc_validation_summary_*.json"
)
set_answer(27, q23_answer, 'Complete', 'training_summary CSVs, validation JSONs')

# =====================================================================
# Q24 - Sensitivity, specificity, VME, ME with 95% CIs
# =====================================================================
q24_answer = (
    "From threshold audit (v3 internal holdout, threshold=0.50):\n\n"
    "| Drug | n_test | Sens | Spec | PPV | NPV | MCC | VME | ME |\n"
    "|---|---|---|---|---|---|---|---|---|\n"
    "| Meropenem | 125 | 97.1% | 96.4% | 97.1% | 96.4% | 0.935 | 2.9% (2/69) | 3.6% (2/56) |\n"
    "| Ciprofloxacin | 140 | 94.1% | 94.4% | 94.1% | 94.4% | 0.886 | 5.9% (4/68) | 5.6% (4/72) |\n"
    f"| Cefotaxime v4 external | 500 | 82.8% | 95.2% | 94.5% | 84.7% | 0.786 | 17.2% (43/250) | 4.8% (12/250) |\n\n"
    "*VME = Very Major Error = FN / total resistant; **ME = Major Error = FP / total susceptible\n\n"
    "> GAP: 95% confidence intervals have NOT been computed. A bootstrap CI script has been "
    "written (scripts/compute_ci.py) but requires running on test genomes to produce final CIs. "
    "The compute_ci.py script will be executed once the Supabase database connection is restored.\n"
    "See: validation_results/threshold_audit_*.json, scripts/compute_ci.py"
)
set_answer(28, q24_answer, 'In progress', 'threshold audit JSONs, compute_ci.py')

# =====================================================================
# Q25 - Rule-based baseline comparison
# =====================================================================
q25_answer = (
    "NOT YET DONE. No head-to-head comparison with AMRFinderPlus, ResFinder, or CARD/RGI "
    "has been run on the same test isolates. This is a required deliverable before the letter "
    "can be sent.\n\n"
    "Plan: Run AMRFinderPlus (v3.0.10+) on the same test genomes and compare gene-based "
    "predictions against our ensemble predictions.\n"
    "See: scripts/ (to be created for AMRFinderPlus comparison)"
)
set_answer(29, q25_answer, 'Not yet done', 'Pending — requires AMRFinderPlus installation and execution')

# =====================================================================
# Q26 - Driving genes/mutations
# =====================================================================
q26_answer = (
    "The 18 AMR gene signature features are biologically curated:\n\n"
    "| Drug | Key features | Biological basis |\n"
    "|---|---|---|\n"
    "| Meropenem | blaKPC, blaNDM, blaVIM, blaIMP, blaOXA-48 | Known carbapenemase genes |\n"
    "| Ciprofloxacin | gyrA mutations, parC mutations, acrAB efflux | QRDR mutations + efflux |\n"
    "| Cefotaxime | blaCTX-M, blaTEM, blaSHV, blaPER, blaACC | ESBL and cephalosporinase genes |\n\n"
    "These match standard resistance determinants in NCBI AMRFinderPlus, CARD, and ResFinder. "
    "Biological plausibility is strong. However, current implementation uses short k-mer proxies "
    "(three 6-mers per gene) rather than full gene detection.\n"
    "See: bactoai_pipeline.py extract_gene_signatures()"
)
set_answer(30, q26_answer, 'Complete', 'bactoai_pipeline.py')

# =====================================================================
# Q27 - Independent datasets
# =====================================================================
q27_answer = (
    "One external validation completed:\n"
    "- BV-BRC E. coli cefotaxime cohort (500-genome holdout): ROC-AUC = 0.9333, "
    "sensitivity 82.8%, specificity 95.2%\n\n"
    "Planned additional datasets:\n"
    "1. Liverpool E. coli WGS-AST dataset (762 isolates, 2025)\n"
    "2. Moradigaravand et al. (2018) E. coli collection (~1,900 UK bloodstream isolates)\n"
    "3. Nguyen et al. (2018) K. pneumoniae MIC set (~1,600 isolates)\n\n"
    "Overlap checks will compare BioSample and SRA accessions against our master isolate list.\n"
    "See: BVBRC_INTEGRATION_AND_VALIDATION_REPORT.md"
)
set_answer(31, q27_answer, 'Complete', 'BVBRC report, planned datasets in strategy doc')

# =====================================================================
# Q28 - Kenyan/East African isolates available (UPDATED)
# =====================================================================
q28_answer = (
    f"From NCBI BigQuery (queried Oct 2026):\n\n"
    f"=== KENYA ===\n"
    f"Total Kenyan genomes with AST in BigQuery: {kenya_total:,}\n"
    f"  - Strict 'Kenya': {top_countries.get('Kenya', 0):,}\n"
    f"  - 'Kenya: Nairobi': {top_countries.get('Kenya: Nairobi', 0):,}\n\n"
    f"By target species in Kenya (BigQuery):\n"
    f"  - E. coli and Shigella: {kenya_species.get('E.coli and Shigella', 0):,}\n"
    f"  - Klebsiella pneumoniae: {kenya_species.get('Klebsiella pneumoniae', 0):,}\n"
    f"  - Salmonella enterica: {kenya_species.get('Salmonella enterica', 0):,}\n"
    f"  - Pseudomonas aeruginosa: {kenya_species.get('Pseudomonas aeruginosa', 0):,}\n"
    f"  - Acinetobacter baumannii: {kenya_species.get('Acinetobacter baumannii', 0):,}\n\n"
    f"=== EAST AFRICA ===\n"
    f"Total (Kenya+Uganda+Tanzania+Ethiopia+Rwanda): {ea_total:,} genomes\n\n"
    f"=== ALL AFRICA ===\n"
    f"Total (13 countries): {af_total:,} genomes\n\n"
    f"Top African countries in BigQuery:\n"
    f"  {', '.join(f'{c}: {n:,}' for c, n in list(top_countries.items())[:8])}\n\n"
    f"Of our 1,673 training isolates, only 52 (3.1%) are African, and only 2 are Kenyan. "
    f"The remaining {kenya_total - 9:,} Kenyan genomes with AST are available for enrichment.\n"
    f"See: scripts/kenya_audit_fast.py, data/kenya_audit_fast.json"
)
set_answer(32, q28_answer, 'Complete', 'scripts/kenya_audit_fast.py, BigQuery results')

# =====================================================================
# Q29 - NPHL study design
# =====================================================================
q29_answer = (
    "Proposed study design:\n"
    "- Species: E. coli, K. pneumoniae, A. baumannii (Gram-negative panel)\n"
    "- Antibiotics: meropenem, ciprofloxacin, cefotaxime\n"
    "- Reference AST: broth microdilution per ISO 20776-1, interpreted with CLSI M100 or EUCAST\n"
    "- Sample size: minimum 100 isolates per species-drug combination (200 preferred)\n"
    "- Blinding: lab staff performing phenotypic AST blinded to BactoAI predictions; "
    "predictions generated from frozen model before phenotypic results available\n"
    "- Reporting: STARD 2015 and TRIPOD+AI guidelines\n"
    "See: KU_IvE_Validation_Answers.md"
)
set_answer(33, q29_answer, 'Complete', 'Validation answers document')

# =====================================================================
# Q30 - NPHL data separation
# =====================================================================
q30_answer = (
    "Proposed separation:\n"
    "- On receipt, NPHL isolates randomly assigned to locked validation partition (30-40%) "
    "and retraining partition (60-70%), using seed-controlled split\n"
    "- Validation partition stored separately, excluded from training/tuning/feature selection\n"
    "- Written log of partition assignments shared with NPHL before any retraining begins\n"
    "See: KU_IvE_Validation_Answers.md"
)
set_answer(34, q30_answer, 'Complete', 'Validation answers document')

# =====================================================================
# Q31 - Model freezing
# =====================================================================
q31_answer = (
    "Yes. Plan:\n"
    "1. Tag repository with versioned release (e.g., v4.1-nphl-frozen)\n"
    "2. Record exact model checkpoint files (.joblib), vectorizer, selector, calibration scores\n"
    "3. Hash all model artifacts (SHA-256) and log them\n"
    "4. No retraining or threshold changes until validation complete and reported\n"
    "See: KU_IvE_Validation_Answers.md"
)
set_answer(35, q31_answer, 'Complete', 'Validation answers document')

# =====================================================================
# Q32 - Hosting
# =====================================================================
q32_answer = (
    "| Component | Provider | Country | URL |\n"
    "|---|---|---|---|\n"
    "| ML prediction backend | Render (Web Service) | USA (Oregon) | bactoai-kt0q.onrender.com |\n"
    "| Website frontend | Vercel / Lovable | USA | bactoai.co.ke |\n"
    "| Backend database | Supabase (PostgreSQL) | USA (AWS us-east-1) | ofuxwgapzjgcrsuiqpyu.supabase.co |\n\n"
    "Data handling:\n"
    "- Uploaded genome files processed in-memory; not written to persistent disk "
    "(Render ephemeral filesystem wiped on redeploy)\n"
    "- Prediction metadata stored in Supabase submissions table\n"
    "- No genomic sequence data retained after prediction\n\n"
    "> NOTE: Cross-border data transfer under Kenya Data Protection Act, 2019. "
    "Deployment of Kenya-hosted instance planned for NPHL data.\n"
    "See: PREDICTION_PIPELINE_FIX.md, ROADMAP.md"
)
set_answer(36, q32_answer, 'Complete', 'Render dashboard, Supabase dashboard')

# =====================================================================
# Q33 - ODPC registration
# =====================================================================
q33_answer = (
    "NOT YET DONE. Registration with the Office of the Data Protection Commissioner (ODPC) "
    "and a formal Data Protection Impact Assessment (DPIA) are pending. This is an "
    "administrative requirement that must be completed before processing NPHL data.\n\n"
    "Status: Not initiated. Will be addressed once NPHL partnership is formalized.\n"
    "See: ROADMAP.md (Part 3 — Governance)"
)
set_answer(37, q33_answer, 'Not yet done', 'Administrative — pending NPHL MOU')

# =====================================================================
# Q34 - Ethics committee
# =====================================================================
q34_answer = (
    "NOT YET INITIATED. The ethics review and NACOSTI licence application will be prepared "
    "once the NPHL partnership is formalized. Expected committees:\n"
    "- Kenyatta University Ethical Review Committee (KUFORDS)\n"
    "- Kenya National Commission for Science, Technology and Innovation (NACOSTI)\n"
    "- NPHL institutional review (if applicable)\n\n"
    "Status: Not initiated. Will begin after MOU signing.\n"
    "See: ROADMAP.md (Part 3 — Governance)"
)
set_answer(38, q34_answer, 'Not yet done', 'Administrative — pending NPHL MOU')

# =====================================================================
# Q35 - Pharmacy and Poisons Board
# =====================================================================
q35_answer = (
    "BactoAI is positioned as a CLINICAL DECISION SUPPORT TOOL, not a standalone diagnostic device. "
    "The team is aware that software used to inform diagnosis may fall under medical device regulation. "
    "A written intended-use statement has NOT yet been drafted. Initial contact with the Pharmacy "
    "and Poisons Board has NOT been made.\n\n"
    "> ACTION REQUIRED: Draft intended-use statement and seek regulatory guidance from the "
    "Pharmacy and Poisons Board before clinical deployment.\n"
    "See: ROADMAP.md (Part 3 — Governance)"
)
set_answer(39, q35_answer, 'Not yet done', 'Regulatory — action required before deployment')

# =====================================================================
# Q36 - IP arrangements
# =====================================================================
q36_answer = (
    "BactoAI was selected for a CDIE Catalyst Grant administered through the Kenyatta University "
    "Design Studio. The IP and ownership arrangements among BactoAI, Kenyatta University, and NPHL "
    "for models retrained on NPHL data have NOT YET BEEN FORMALLY AGREED. This should be addressed "
    "in the data-sharing agreement or MOU.\n"
    "See: ROADMAP.md (Part 3 — Partnerships)"
)
set_answer(40, q36_answer, 'Not yet done', 'Legal — to be resolved in MOU')

# =====================================================================
# Q37 - Code repository
# =====================================================================
q37_answer = (
    "- Code repository: GitHub, synchronized across two remotes:\n"
    "  * origin: https://github.com/Savville/BactoAI.git (personal)\n"
    "  * bactoai-eng: https://github.com/bactoai-eng/BACTOAI.git (organization)\n"
    "- Environment: Python 3.12, dependencies in requirements.txt and requirements-ml.txt\n"
    "- Accession lists: data/metadata_*.csv\n"
    "- Reproducibility: Yes — clone repo, install deps, run bactoai_pipeline.py --train\n"
    "- Random seeds: Fixed at [42, 123, 456, 789, 1024]\n"
    "See: README.md, Dockerfile, bactoai_pipeline.py"
)
set_answer(41, q37_answer, 'Complete', 'GitHub repos, requirements files, Dockerfile')

# =====================================================================
# Q38 - Limitations
# =====================================================================
q38_answer = (
    "1. Species imbalance: Over 85% of cefotaxime training genomes are E. coli. Performance on "
    "K. pneumoniae, A. baumannii, and P. aeruginosa is likely weaker.\n"
    "2. Geographic skew: Training data predominantly from North America and Europe. Only 3.1% "
    f"African (52/1,673), only 2 Kenyan. Performance on local strains unknown.\n"
    "3. Method mixing: Cefotaxime v4 mixes MIC-derived and disk-diffusion labels without "
    "re-harmonization to a single breakpoint version.\n"
    "4. No relatedness-aware split: Random splitting may inflate AUC when clonally related "
    "isolates span train/test boundary.\n"
    "5. No formal genome QC: No contamination, completeness, or species-confirmation checks.\n"
    "6. K-mer proxy for gene detection: Three 6-mers per gene is rough proxy, not equivalent "
    "to full-length gene detection (AMRFinderPlus, ResFinder).\n"
    "7. Drug model maturity gap: Meropenem and ciprofloxacin at v3 (600 genomes each), "
    "cefotaxime at v4 (4,019 genomes).\n"
    "8. No rule-based baseline comparison yet (Q25).\n"
    "See: KU_IvE_Validation_Answers.md, DATASET_ORGANISMS_AND_AMR_ACQUISITION_STRATEGY.md"
)
set_answer(42, q38_answer, 'Complete', 'Multiple source documents')

# =====================================================================
# Q39 - KU support needed
# =====================================================================
q39_answer = (
    "1. Compute resources: GPU-enabled workstation or cloud credits for retraining expanded datasets "
    "(3,000+ genomes per drug)\n"
    "2. Wet-lab AST confirmation: Access to microbiology laboratory for phenotypic confirmation of "
    "edge-case predictions\n"
    "3. Local isolates: Access to Kenyan clinical isolate sequences (through KEMRI partnerships or "
    "KU hospital collaborations)\n"
    "4. Supervision: Technical mentorship from Dr. Iloka and IvE team on regulatory pathway, "
    "validation study design, STARD/TRIPOD+AI reporting\n"
    "5. NACOSTI/ethics support: Guidance on ethics committee submission and NACOSTI research licence process\n"
    "See: KU_IvE_Validation_Answers.md, ROADMAP.md"
)
set_answer(43, q39_answer, 'Complete', 'Roadmap, validation answers')

# Save
wb.save('deliverables/BactoAI Validation Capture.xlsx')
print("Excel updated successfully!")

# Also print summary
print(f"\nUpdated {sum(1 for row in range(5, 44) if ws.cell(row=row, column=5).value)}/39 questions")
status_counts = {}
for row in range(5, 44):
    s = ws.cell(row=row, column=7).value
    if s:
        status_counts[s] = status_counts.get(s, 0) + 1
for s, c in status_counts.items():
    print(f"  {s}: {c}")
