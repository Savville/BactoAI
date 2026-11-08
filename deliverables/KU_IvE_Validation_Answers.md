# BactoAI: Responses to KU IvE Validation Guidance Questions

**Date:** 8 November 2026
**Reference document:** *BactoAI: Validating a Genomic AMR Prediction Model* (Dr Kenneth Malongo Iloka, 26 October 2026)

---

## A. The Product and the Claims in the Letter

### Q1. Which bacterial species do the meropenem, ciprofloxacin and cefotaxime models cover? Is there one model per drug across species, or one per species-drug pair?

There is **one model per antibiotic**, trained across multiple Gram-negative species. The species included per drug are:

| Drug | Species in training set | Count |
|:---|:---|:---:|
| **Meropenem** | *A. baumannii* (98), *K. pneumoniae* (152), *E. coli/Shigella* (198), *P. aeruginosa* (63), *S. enterica* (87), *E. cloacae* (2) | 600 |
| **Ciprofloxacin** | *E. coli/Shigella* (287), *S. enterica* (133), *A. baumannii* (86), *K. pneumoniae* (54), *P. aeruginosa* (39), *E. cloacae* (1) | 600 |
| **Cefotaxime** | *E. coli/Shigella* (222 NCBI + 3,419 BV-BRC), *K. pneumoniae* (219), *A. baumannii* (114), *S. enterica* (43), *P. aeruginosa* (1), *E. cloacae* (1) | 600 NCBI; 4,019 combined |

Each model is a cross-species model. It is not separated by species-drug pair.

### Q2. What does the "under ten minutes" start from and what does it include? What is the realistic total time from patient sample to result?

The "under ten minutes" refers to **computational prediction time from an assembled genome (FASTA file) to a resistance call**. Specifically:
- **Input:** An assembled genome in `.fna` or `.fasta` format.
- **Process:** k-mer extraction, feature vectorization, and inference through a 5-model deep ensemble with uncertainty estimation.
- **Observed time:** 8-thread parallel inference on 500 genomes completed in 45 seconds total (about 0.09 seconds per genome). A single genome prediction runs in under 1 second.

The realistic total turnaround from a patient sample involves:
1. Culture and isolation: 1-2 days
2. DNA extraction: 2-4 hours
3. Whole-genome sequencing (Illumina): 12-36 hours; (Nanopore MinION): 2-8 hours
4. Assembly (SPAdes / Flye): 30 minutes to 2 hours
5. **BactoAI prediction: under 1 minute**

Total sample-to-result: approximately 2-4 days, depending on the sequencing platform. The advantage over conventional phenotypic AST is that BactoAI provides simultaneous resistance predictions across three antibiotic classes as soon as a genome assembly exists, whereas disk diffusion or broth microdilution requires a separate 16-20 hour incubation step *after* isolation.

### Q3. What sequencing platform and file types does the tool accept? Does this match what NPHL produces?

The tool accepts:
- **File formats:** FASTA (`.fna`, `.fasta`), including gzip-compressed (`.fna.gz`).
- **Input type:** Assembled contigs (not raw reads). The `read_fasta()` function in `bactoai_pipeline.py` concatenates all contigs in a multi-FASTA into a single sequence string.
- **Sequencing platform:** Platform-agnostic. Training data includes assemblies from both Illumina short-read and Nanopore long-read sequencing.

NPHL operates Illumina MiSeq and NextSeq instruments and produces assembled genomes in FASTA format, so the input formats are compatible.

### Q4. Are there models for other antibiotics? Why were these three highlighted?

Currently, only three models are deployed: **meropenem, ciprofloxacin, cefotaxime**. These were selected because they represent three clinically high-priority antibiotic classes for Gram-negative infections in Kenya and East Africa:

- **Meropenem (carbapenem):** Last-line therapy for multidrug-resistant infections; carbapenem resistance is a WHO Priority 1 Critical threat.
- **Ciprofloxacin (fluoroquinolone):** First-line for many Gram-negative infections; resistance exceeds 60% in many LMIC hospital settings.
- **Cefotaxime (3rd-gen cephalosporin):** Widely used empiric therapy; ESBL-mediated resistance is expanding rapidly.

The data acquisition roadmap includes expansion to additional antibiotics (ceftriaxone, ceftazidime, gentamicin, amikacin, colistin) through future BV-BRC and NCBI downloads.

---

## B. Training Data (the 1,800+ Clinical Isolates)

### Q5. Which NCBI resources did you use? Give search terms, filters and download date.

**Sources used:**
1. **NCBI Pathogen Detection AST Browser** (`ncbi.nlm.nih.gov/pathogens/ast`) -- primary source for the 600-isolate-per-drug NCBI batch.
2. **NCBI Isolates Browser** (`ncbi.nlm.nih.gov/pathogens/isolates`) -- isolate metadata, SNP cluster IDs, country information.
3. **NCBI SRA and GenBank** -- genome assemblies downloaded via accession (column `asm_acc` in metadata CSVs, e.g. `GCA_016535115.2`).
4. **Google BigQuery** on `ncbi-pathogen-detect` dataset (via `scripts/ncbi_bigquery.py`) -- geographic resistance prevalence priors.

**Filters applied (documented in `scripts/ncbi_bigquery.py`):**
- Target antibiotics: meropenem, ciprofloxacin, cefotaxime (plus related drugs for enrichment).
- Target organisms: Gram-negative pathogens (taxon IDs for *E. coli*, *K. pneumoniae*, *A. baumannii*, *P. aeruginosa*, *S. enterica*).
- Phenotype: records with S/I/R labels or quantitative MIC values.

**Download date:** Initial NCBI batch downloaded mid-2026 (pipeline file header: "Created: 2026-07-22"). BV-BRC batch downloaded September 2026.

### Q6. How many isolates were downloaded, and how many remained after cleaning?

| Drug | Downloaded | After cleaning | Resistant | Susceptible |
|:---|:---:|:---:|:---:|:---:|
| Meropenem (NCBI) | ~600 | 600 | 300 | 300 |
| Ciprofloxacin (NCBI) | ~600 | 600 | 300 | 300 |
| Cefotaxime (NCBI) | ~600 | 600 | 300 | 300 |
| Cefotaxime (BV-BRC) | 6,260 raw entries | 3,419 after cleaning | 384 | 3,035 |
| **Cefotaxime (combined v4)** | -- | **4,019** | **684** | **3,335** |

Total unique isolates across all three drugs: approximately **1,800 NCBI** plus **3,419 BV-BRC** = **5,219** (with the 600 NCBI cefotaxime isolates counted once).

The "1,800+" claim in the letter refers to the NCBI batch (600 per drug x 3 drugs; 1,673 unique isolates after de-duplication). The combined research corpus, including BV-BRC, exceeds 5,200 isolates, but BV-BRC was used only for the non-deployed combined cefotaxime model and benchmark.

### Q7. Which countries, years and settings are represented? How many are African, how many Kenyan?

**Exact counts from BigQuery cross-reference (October 2026):**

The NCBI metadata files contain a `target_acc` (PDT accession) and `taxgroup_name` but no explicit country columns. We queried NCBI BigQuery (`ncbi-pathogen-detect.pdbrowser.isolates`) to cross-reference our 1,673 training set accessions against geographic data.

**African isolates in the current training set (52 / 1,673 = 3.1%):**

| Country | Isolates in Training | Species | Drugs |
|---------|---------------------|---------|-------|
| **Kenya** | **2** | K. pneumoniae | cefotaxime, meropenem |
| South Africa | 8 | K. pneumoniae, E. coli, Enterobacter | all 3 |
| Tunisia | 32 | K. pneumoniae | all 3 |
| Nigeria | 9 | K. pneumoniae, S. enterica | all 3 |
| Algeria | 1 | E. coli | cefotaxime |
| **Total Africa** | **52 / 1,673 (3.1%)** | | |

**Publicly available Kenyan data (BigQuery, Oct 2026):**

| Metric | Count |
|--------|------:|
| Kenya genomes with ANY AST | **8,462** |
|, Strict "Kenya" | 6,539 |
|, "Kenya: Nairobi" | 821 |
| East Africa (Keny+Uga+Tan+Eth+Rwa) | **17,173** |
| All Africa (13 countries) | **33,483** |

**Kenya by target species (BigQuery):**

| Species | Genomes |
|---------|--------:|
| E. coli and Shigella | 4,246 |
| Klebsiella pneumoniae | 1,359 |
| Salmonella enterica | 561 |
| Pseudomonas aeruginosa | 76 |
| Acinetobacter baumannii | 43 |

**Kenya AST for target antibiotics (BigQuery):**

| Antibiotic | Genomes | Records | Resistant | Susceptible |
|------------|--------:|--------:|----------:|------------:|
| Meropenem | 9 | 9 | 6 | 3 |
| Ciprofloxacin | 13 | 13 | 8 | 5 |
| Cefotaxime | 7 | 7 | 6 | 1 |

**New Kenyan isolates available for retraining:** ~8,453 (our training has only 2)

The figure of two is the number of unique Kenyan accessions in the three current NCBI drug metadata files, not the total number of public Kenyan isolates. A separate enrichment CSV contains seven Kenyan *K. pneumoniae* meropenem records; the PRJNA717739 attribution is from the supplied review message, not a field in that CSV. Only two accessions, GCA_019927625.1 and GCA_020407015.1, occur in the current drug metadata; both are assigned to training, and neither is in a reconstructed holdout. The seven-record enrichment set was not added to deployed model data.

> [!IMPORTANT]
> **Action completed:** BigQuery geographic enrichment query executed 2026-10-30.
> See: `scripts/kenya_audit_fast.py`, `data/kenya_audit_fast.json`

---

### Q28. How many Kenyan or East African isolates with AST data are available in public databases?

**From NCBI BigQuery (queried 2026-10-30):**

- **Kenyan genomes with AST:** 8,462 (6,539 strict Kenya + 821 Nairobi)
- **East African genomes (5 countries):** 17,173
- **All African genomes (13 countries):** 33,483

**Top African countries in BigQuery:**
South Africa (9,401), Kenya (6,539), Tanzania (3,019), Nigeria (2,415), Uganda (1,329), Ghana (1,235), Tunisia (1,129), Ethiopia (981)

**BV-BRC data:** 0 Kenyan isolates. The BV-BRC dataset (PMIDs: 29112974, 30092762, 32422315, 33846529, 36363724, 38219757) is predominantly European clinical E. coli isolates. No African geographic references found in evidence columns.

**Other sources checked:**
- PathogenWatch: API reachable but no Kenyan/East African outbreak data for target species
- PubMLST: Endpoints returned 404 (API may have changed)
- KEMRI: No public genomic API, requires formal partnership/MOU

> [!NOTE]
> The 8,462 Kenyan genomes represent an enrichment opportunity. A realistic retraining target would be 500-1,000 new Kenyan isolates per antibiotic after deduplication.

### Q8. Did you use raw reads, assemblies or pre-computed gene calls? Which pipeline and tool versions?

- **Input type:** Pre-assembled genomes (FASTA format). Assemblies were downloaded from NCBI GenBank (`GCA_*` accessions) and BV-BRC REST API.
- **No raw read processing is done.** The pipeline starts from assembled genomes.
- **Assembly versions used:** The exact GCA version suffix and FASTA filename for each required assembly are recorded in `validation_results/all_metadata_genome_manifest.csv`, alongside file size and SHA-256. The cited GCA_019927405.1 is not in the required manifest or local `data/genomes/`, so it was not used for these results. Genome files are not tracked in Git.
- **Feature extraction pipeline versions:**
  - Python 3.12
  - Biopython (SeqIO for FASTA parsing)
  - scikit-learn CountVectorizer for k-mer tokenization
  - scikit-learn SelectKBest (chi-squared) for feature selection
  - XGBoost, Random Forest, LightGBM as classifiers
  - scikit-learn CalibratedClassifierCV (Platt sigmoid scaling)
- **Library versions:** `requirements-ml.txt` declares scikit-learn 1.7.2 and XGBoost 3.2.0. The serialized estimator confirms scikit-learn 1.7.2, but the exact XGBoost training version is not established; the serialized model emits a version-compatibility warning when loaded. Local verification used scikit-learn 1.8.0 and XGBoost 3.2.0; these are verification-runtime versions.
  - imbalanced-learn SMOTE for class rebalancing

### Q9. Did you use any data outside NCBI?

Yes. **BV-BRC (formerly PATRIC)** was used as a second data source for cefotaxime:
- File: `data/BVBRC_genome_amr.csv` (6,260 raw entries)
- Organism: *Escherichia coli* (NCBI Taxon ID 562)
- Downloaded via the BV-BRC REST API (`scripts/download_bvbrc_genomes.py`)
- 6,090 full FASTA chromosomes saved to `data/bvbrc_genomes/`
- After cleaning: 3,419 deduplicated records merged into the combined cefotaxime training set

No other external datasets have been used for training so far. The Liverpool *E. coli* WGS-AST dataset, Moradigaravand et al. (2018), and Nguyen et al. (2018) are identified as potential independent test sets but have not been downloaded.

---

## C. Phenotype Labels and Quality Control

### Q10. Which AST methods are in your data? Did you mix methods?

Yes, two sources/types are represented:
1. **Each deployed `metadata_{drug}.csv`:** 600 NCBI Pathogen Detection labels and 0 BV-BRC labels, for meropenem, ciprofloxacin and cefotaxime. Calls are pre-classified S/I/R and recorded as `MIC_or_mixed`; exact per-record laboratory method and breakpoint edition are not consistently available.
2. **Disk diffusion (zone diameter in mm):** Used in the BV-BRC batch (cefotaxime only, 3,419 isolates).

All three deployed models use the 600-row-per-drug NCBI metadata. BV-BRC cefotaxime disk-diffusion labels are used only in a separate research benchmark, not by the deployed models.

### Q11. Which breakpoint standard and version did you use to convert MICs to S/I/R?

- **BV-BRC (disk diffusion):** EUCAST v14.0 clinical breakpoints for *Enterobacterales* vs cefotaxime (5 µg disc):
  - Resistant: zone diameter <= 17 mm
  - Intermediate / Area of Technical Uncertainty: 17-19 mm (mapped to Resistant under the clinical default)
  - Susceptible: zone diameter >= 20 mm
- **NCBI data (all deployed models):** The NCBI Pathogen Detection AST Browser provides pre-classified S/I/R labels recorded as `MIC_or_mixed`. The specific breakpoint standard and version used by the original submitters varies by record and has **not been re-harmonised to a single version**.

> [!WARNING]
> **Gap:** The deployed models use NCBI labels only; they were not re-interpreted with a single breakpoint version. The BV-BRC labels were standardised to EUCAST v14.0 but are used only by the non-deployed combined cefotaxime model and the BV-BRC benchmark. For the NPHL validation, all labels should be re-interpreted using one standard and version (e.g., EUCAST v14.0 or CLSI M100 Ed34).

### Q12. How did you treat intermediate results, missing values and conflicting records?

- **Intermediate results:** One intermediate row each is present in meropenem and ciprofloxacin metadata, both encoded as `resistant = 1`; cefotaxime has none. The original sampling/mapping rationale and the handling of other intermediate records cannot be reconstructed from available source inputs.
- **ND/DD/NS:** No such rows are present in the shipped metadata. The original pre-filter counts and exclusion process are unavailable.
- **Missing values:** Rows with missing `asm_acc` or `resistant` fields are dropped in `extract_features()` via `metadata_df.dropna(subset=["asm_acc", "resistant"])`.
- **Duplicates:** De-duplicated by assembly accession using `metadata_df.drop_duplicates(subset="asm_acc")`.
- **Conflicting records:** Not explicitly handled. If the same isolate has conflicting S/R labels across sources, only the first occurrence (after de-duplication) is retained.

### Q13. What genome quality-control thresholds did you apply, and how many genomes failed?

- The pipeline checks whether a genome file exists and is readable (`read_fasta()` returns an empty string on failure).
- Genomes that cannot be parsed or are empty are skipped (counted as `missing` in `extract_features()`).
- **No explicit thresholds for contamination, completeness, contig count or genome size are applied.**

> [!WARNING]
> **Gap:** Formal genome QC (e.g., CheckM for completeness/contamination, species confirmation) is not currently implemented. This should be added before formal validation.

---

## D. Features and Model

### Q14. What input features does the model use? How are they generated?

The model uses two feature types:

1. **K-mer frequencies (k=5):** Each genome is decomposed into all 5-character substrings. The `CountVectorizer` tokenizes these, then `SelectKBest(chi2)` selects the top 50,000 most informative k-mers. For the v4 cefotaxime model, 1,321 unique 5-mers passed the chi-squared test.

2. **AMR gene signature features (18 binary features):** Presence/absence of known resistance gene k-mer markers. These cover:
   - Carbapenemases: *blaKPC*, *blaNDM*, *blaVIM*, *blaIMP*, *blaOXA-48*
   - Penicillinases: *blaTEM*, *blaSHV*
   - Cephalosporinases: *blaCTX-M*, *blaPER*, *blaACC*
   - Fluoroquinolone resistance: *gyrA* mutations, *parC* mutations
   - Efflux pumps: *acrAB*, *ramA*
   - MLS resistance: *ermB*, *mphA*
   - Aminoglycoside resistance: *aac(6')-I*, *aph(3')*

Combined feature matrix: k-mer counts + gene signatures concatenated via `scipy.sparse.hstack`.

### Q15. Which algorithm(s) did you train, and why?

A loaded model object is `CalibratedClassifierCV`, wrapping a soft-voting `VotingClassifier` of three base learners:
1. **XGBoost** (300 estimators, max depth 6, learning rate 0.05) -- gradient-boosted trees perform well on tabular/sparse feature matrices.
2. **Random Forest** (200 estimators, max depth 10, balanced class weights) -- provides diversity and is strong to overfitting.
3. **LightGBM** (300 estimators, max depth 6, learning rate 0.05) -- fast gradient boosting with leaf-wise growth.

Five such calibrated model objects are saved per drug (seeds: 42, 123, 456, 789, 1024). Their mean probability is the prediction; their standard deviation is the uncertainty. The deployment is not a single 15-model ensemble.

### Q16. How did you handle class imbalance?

- **SMOTE (Synthetic Minority Over-sampling Technique):** Applied when the minority class (resistant) is less than 60% of the majority class, using `imblearn.over_sampling.SMOTE(k_neighbors=min(5, n_pos-1))`.
- **Scale weighting:** XGBoost uses `scale_pos_weight = n_neg / n_pos`. Random Forest uses `class_weight="balanced"`. LightGBM uses `scale_pos_weight`.
- **Balanced training data:** The NCBI batch was curated at 300 R / 300 S per drug (perfectly balanced). SMOTE was applied for the combined cefotaxime set (684 R vs 3,335 S).

### Q17. How were hyperparameters tuned, and on which data partition?

Hyperparameters are currently **fixed** (not tuned via grid search or Bayesian optimization):
- XGBoost: `n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8`
- Random Forest: `n_estimators=200, max_depth=10`
- LightGBM: `n_estimators=300, max_depth=6, learning_rate=0.05`
- Feature selection: `SelectKBest(chi2, k=50,000+18)`

The 5-fold `CalibratedClassifierCV(method="sigmoid")` is fitted on the training partition. The holdout is not used to fit the Platt calibrator, but it is used for reported evaluation and for the saved conformal nonconformity scores. The available record does not establish whether the original adaptive-threshold constants were selected using test results.

---

## E. How the ROC-AUC Figures Were Obtained

### Q18. For each drug, how many isolates were in the test set, and what proportion?

| Drug | Metadata rows | Usable (FASTA present) | Train | Test | Test proportion |
|:---|:---:|:---:|:---:|:---:|:---:|
| Meropenem (deployed v4) | 600 | 493 | 369 | **124 (70R, 54S)** | 25% |
| Ciprofloxacin (deployed v4) | 600 | 572 | 429 | **143 (70R, 73S)** | 25% |
| Cefotaxime (deployed v4, NCBI only) | 600 | 578 | 433 | **145 (71R, 74S)** | 25% |

The split is reconstructed by dropping missing labels and duplicate accessions, shuffling with seed 42, removing missing or unreadable FASTAs, and applying a stratified 25% split. The old `threshold_audit` counts (125/140/147) came from a different, non-equivalent split. The earlier cefotaxime accuracy 79.31% (115/145) is superseded by 78.62% (114/145); old row-level predictions are unavailable to explain the one-call difference. The per-accession assignment is in `validation_results/test_split_*.csv`.

### Q19. Was the split random, or were related isolates kept together?

The split is **random**, using `train_test_split(test_size=0.25, random_state=42, stratify=y)`. Stratification preserves the S/R class ratio in both sets.

**Related isolates (same SNP cluster, sequence type or clade) are NOT kept together.** The pipeline does not use phylogenetic or SNP-cluster-aware splitting.

> [!WARNING]
> **Gap:** No ANI, SNP-cluster or phylogeny-based train/test comparison has been run. Relatedness across the random split is unknown; possible leakage remains an unmeasured limitation.

### Q20. How did you confirm that no isolate appears in both training and testing?

De-duplication by assembly accession (`drop_duplicates(subset="asm_acc")`) occurs before splitting. The `train_test_split` function partitions the de-duplicated list, so no accession appears in both sets within a single drug model.

Cross-dataset overlap between NCBI and BV-BRC was checked by accession format: NCBI uses `GCA_*` prefixes while BV-BRC uses `562.*` genome IDs, so the namespaces do not collide. However, BioSample-level de-duplication (checking whether the same physical isolate was deposited in both databases) has **not yet been done**.

### Q21. Was any preprocessing fitted on the full dataset before splitting?

No. In `extract_features()`, `CountVectorizer.fit_transform()` and `SelectKBest.fit_transform()` are called on the training partition only. The test set is transformed with the fitted vectorizer and selector (`.transform()`, not `.fit_transform()`).

The split happens via `train_test_split()` in `train_deep_ensemble()`, and feature extraction parameters are fitted on `X_tr` only.

### Q22. Was the test set used once, after all model choices were fixed?

The internal holdout is evaluated at the end of training for each of the five saved models. Available code shows no iterative hyperparameter tuning on the holdout. The holdout is used for:
- Per-model AUC reporting
- Overall ensemble AUC reporting
- Saved nonconformity scores for conformal prediction

The Platt calibrator is fitted only within the training partition. No record explains who selected the adaptive-threshold or confidence constants, why those values were chosen, or whether test performance informed the original choices.

### Q23. Please confirm the ciprofloxacin and cefotaxime results separately. Are both exactly 0.872?

The current deployed artifact is under `data/models_v4/`; no `models_v3/` artifact is available. `joblib.load()` returns `CalibratedClassifierCV` wrapping a soft-voting `VotingClassifier` with XGBoost, Random Forest and LightGBM. Five such top-level models are used per drug.

| Drug | Current v4 holdout AUC | Historical summary |
|:--|--:|:--|
| Meropenem | **0.942063** | — |
| Ciprofloxacin | **0.877299** | — |
| Cefotaxime | **0.872288** | `training_summary_v3.csv` records 0.872097 and 79.31% accuracy |

The current cefotaxime v4 prediction CSV and `summary_cefotaxime.json` agree at AUC 0.872288 and 78.62% accuracy. The v3 summary has no corresponding model or row-level predictions, so it cannot be confirmed as the same model or reconciled with v4; its 79.31% accuracy is withdrawn.

The old 0.9871 and 0.9559 figures are from the non-equivalent `threshold_audit` split and are withdrawn. The BV-BRC benchmark AUC of 0.9333 can be recomputed from its 500-row CSV, but is in-corpus, not independent validation. The 0.7793 combined-model AUC is only in a training summary; without its 1,000-row prediction output it is withdrawn from reported results.

### Q24. For each drug, give sensitivity, specificity, VME rate and ME rate at the decision threshold, with 95% CIs.

**Current deployed holdout results.** The live rule gave the same calls as fixed 0.50 in the test CSVs, so both columns below are identical. Wilson 95% intervals are shown for sensitivity and specificity.

| Drug | n | Sensitivity | Spec. | VME | ME | Low confidence | AUC (95% CI) |
|:---|--:|--:|--:|--:|--:|--:|:--|
| Meropenem | 124 | 91.4% [82.5, 96.0] | 87.0% [75.6, 93.6] | 8.6% (6/70) | 13.0% (7/54) | 0/124 | 0.9421 [0.9009, 0.9832] |
| Ciprofloxacin | 143 | 80.0% [69.2, 87.7] | 83.6% [73.4, 90.3] | 20.0% (14/70) | 16.4% (12/73) | 0/143 | 0.8773 [0.8189, 0.9357] |
| Cefotaxime | 145 | 83.1% [72.7, 90.1] | 74.3% [63.4, 82.9] | 16.9% (12/71) | 25.7% (19/74) | 0/145 | 0.8723 [0.8132, 0.9314] |

*VME = Very Major Error = resistant isolates called susceptible = FN / total resistant.
**ME = Major Error = susceptible isolates called resistant = FP / total susceptible.

**Method:** Wilson score intervals for proportions; AUC CIs via the Hanley & McNeil (1982) delta-method approximation.

The code hard-codes an adaptive threshold of `0.50 + min(0.5 × uncertainty, 0.15)` and confidence cutoffs of 0.05/0.15. The repository does not document who selected these values or whether test performance was used. The code comment says the threshold increase is intended to reduce false positives; it can also increase false-susceptible calls, and has not been validated as a safety feature. All 412 holdout rows are HIGH under these heuristic cutoffs; no test call changes under the live rule.

The BV-BRC benchmark's stored operating point at 0.20 has TP=207, TN=238, FP=12, FN=43. Its AUC is recomputable from the CSV; the threshold's selection rationale is not documented, and this result is not independent validation.

> **Verification:** values recomputed from `validation_results/test_predictions_*.csv`.
> CIs in `validation_results/regenerated_metrics_ci.md` and `.json`.
> The earlier `q24_ci_*` files were computed from the leaky `threshold_audit` split and are superseded.

### Q25. How did the model compare with a rule-based tool?

No head-to-head comparison against AMRFinderPlus or ResFinder has been run. Neither tool is installed in this environment. A comparison script exists at `scripts/amrfinder_baseline.py`, but it has not been run.

The model uses 18 AMR gene-signature features as direct inputs (see Q26). They are k-mer proxies for known resistance markers; using them as a simple rule-based baseline would not be equivalent to full gene detection.

| Drug | Gene markers used | Rule-based logic |
|------|------------------|-----------------|
| Meropenem | blaKPC, blaNDM, blaVIM, blaIMP, blaOXA-48 | Any carbapenemase marker -> resistant |
| Ciprofloxacin | gyrA mutations, parC mutations, acrAB | QRDR marker or efflux marker -> resistant |
| Cefotaxime | blaCTX-M, blaTEM, blaSHV, blaPER, blaACC | Any ESBL/cephalosporinase marker -> resistant |

### Q26. Which genes or mutations drive predictions? Are they biologically plausible?

The 18 AMR gene-signature features are biologically motivated:

| Drug | Key driving features | Biological basis |
|:---|:---|:---|
| Meropenem | *blaKPC*, *blaNDM*, *blaVIM*, *blaIMP*, *blaOXA-48* | Known carbapenemase genes |
| Ciprofloxacin | *gyrA* mutations, *parC* mutations, *acrAB* efflux | QRDR mutations and efflux-mediated fluoroquinolone resistance |
| Cefotaxime | *blaCTX-M*, *blaTEM*, *blaSHV*, *blaPER*, *blaACC* | ESBL and cephalosporinase genes |

These are the standard resistance determinants recognized by NCBI AMRFinderPlus, CARD, and ResFinder. The biological plausibility is strong. However, the current implementation uses short k-mer proxies (three 6-mers per gene) rather than full gene detection, which is a known limitation.

---

## F. External Validation Plan

### Q27. Which independent dataset(s) will you test on before the letter is sent?

No independent external validation has been completed. The BV-BRC 500-row benchmark CSV reproduces AUC 0.9333 and the stored 0.20 operating point (TP=207, TN=238, FP=12, FN=43). It is an in-corpus result, not independent validation; the rationale for choosing 0.20 is undocumented. The 0.7793 combined-model AUC is withdrawn because its 1,000-row prediction output is unavailable for independent recomputation.

For the remaining drugs and for a truly independent test, the following datasets from Section 3.2 are planned:
1. Liverpool *E. coli* WGS-AST dataset (762 isolates, 2025)
2. Moradigaravand et al. (2018) *E. coli* collection (~1,900 UK bloodstream isolates)
3. Nguyen et al. (2018) *K. pneumoniae* MIC set (~1,600 isolates)

Overlap checks will compare BioSample and SRA accessions against our master isolate list.

### Q28. How many Kenyan or East African isolates with AST data are available in public databases?

See Q7 for the BigQuery counts. As of October 2026:

- Kenyan genomes with AST in NCBI BigQuery: **8,462**
- East African genomes (5 countries): **17,173**
- All African genomes (13 countries): **33,483**
- BV-BRC: **0** Kenyan isolates (European-only dataset)

> [!NOTE]
> The `scripts/ncbi_bigquery.py` script includes filters for `geo_loc_name = Kenya` and neighboring countries. Query results compiled in `data/kenya_audit_fast.json` (2026-10-30).

### Q29. For the NPHL study, what sample size, species, reference AST method and blinding arrangements do you propose?

**Proposed study design:**
- Species: *E. coli*, *K. pneumoniae*, *A. baumannii* (Gram-negative panel)
- Antibiotics: meropenem, ciprofloxacin, cefotaxime
- Reference AST method: broth microdilution per ISO 20776-1, interpreted with CLSI M100 or EUCAST (to be agreed with NPHL)
- Sample size: minimum 100 isolates per species-drug combination (200 preferred for adequate power)
- Blinding: laboratory staff performing phenotypic AST will be blinded to BactoAI predictions; predictions will be generated from a frozen model version before phenotypic results are available
- Reporting: following STARD 2015 and TRIPOD+AI guidelines

### Q30. How will NPHL retraining data be kept separate from validation data?

**Proposed separation:**
- On receipt, NPHL isolates will be randomly assigned to a locked validation partition (30-40%) and a retraining partition (60-70%), using a seed-controlled split.
- The validation partition will be stored in a separate directory and excluded from any training, tuning, or feature selection.
- A written log of the partition assignments will be shared with NPHL before any model retraining begins.

### Q31. Will the model version be frozen before NPHL validation begins?

Yes. The plan is to:
1. Tag the code repository with a versioned release (e.g., `v4.1-nphl-frozen`)
2. Record the exact model checkpoint files (`.joblib`), vectorizer, selector, and calibration scores
3. Hash all model artifacts (SHA-256) and log them
4. No retraining or threshold changes will occur until the validation is complete and reported

---

## G. Governance, Data Protection and Regulation

### Q32. Where are the web platform and model backend hosted? How are uploaded genomes secured, retained and deleted?

| Component | Provider | Country | URL |
|:---|:---|:---|:---|
| ML prediction backend | Render (Web Service) | USA (Oregon) | `bactoai-kt0q.onrender.com` |
| Website frontend | Vercel / Lovable | USA | `bactoai.co.ke` |
| Backend database | Supabase (PostgreSQL) | Previously documented as AWS `us-east-1`; not independently verified | `ofuxwgapzjgcrsuiqpyu.supabase.co` |
| Website database | Supabase (PostgreSQL) | Region not verified | `ojnecaomcicsayeweoab.supabase.co` |

**Data handling:**
- Uploaded genome files are processed in-memory on the Render backend. They are not written to persistent disk (Render uses an ephemeral filesystem that is wiped on every redeploy).
- Prediction metadata (drug probabilities, confidence scores, timestamps) is stored in the Supabase `submissions` table.
- No genomic sequence data is retained after prediction completes.
- Automated retention for prediction records, feedback and IP audit entries is not implemented; these records may persist indefinitely.
- Live backend RLS and the Render key role have not been independently verified. The local backend migration names the website project as its target, while backend configuration names a different project.

> [!WARNING]
> **Gap for NPHL:** If NPHL genomic data is uploaded, hosting in USA servers constitutes cross-border data transfer under the Data Protection Act, 2019. Before processing NPHL data, either (a) deploy a Kenya-hosted instance, or (b) obtain explicit written consent and a data protection impact assessment for cross-border transfer.

### Q33. Is BactoAI registered with the Office of the Data Protection Commissioner?

**Not yet done.** Registration with the ODPC and a formal Data Protection Impact Assessment (DPIA) are pending.

### Q34. Which ethics committee will review the NPHL study? What is the NACOSTI research licence status?

**Not yet initiated.** The ethics review and NACOSTI licence application will be prepared once the NPHL partnership is formalized.

### Q35. Have you identified the Pharmacy and Poisons Board requirements?

BactoAI is positioned as a **clinical decision support tool**, not a standalone diagnostic device. The team is aware that software used to inform diagnosis may fall under medical device regulation. A written intended-use statement has not yet been drafted. Initial contact with the Pharmacy and Poisons Board has not been made.

> [!IMPORTANT]
> **Action required:** Draft an intended-use statement and seek regulatory guidance from the Pharmacy and Poisons Board before clinical deployment.

### Q36. What are the agreed IP and ownership arrangements?

BactoAI was selected for a **CDIE Catalyst Grant** administered through the Kenyatta University Design Studio. The IP and ownership arrangements between BactoAI (the venture), Kenyatta University, and NPHL for models retrained on NPHL data have **not yet been formally agreed**. This should be addressed in the data-sharing agreement or MOU.

---

## H. Reproducibility and Support

### Q37. Where are the code, environment details and accession lists stored? Can another person rerun the pipeline?

- **Code repository:** GitHub, synchronized across two remotes:
  - `origin`: `https://github.com/Savville/BactoAI.git` (personal)
  - `bactoai-eng`: `https://github.com/bactoai-eng/BACTOAI.git` (organization)
- **Environment:** dependencies are listed in `requirements.txt` and `requirements-ml.txt`. The `.venv/` directory is excluded from the updated branch.
- **Accession lists:** Assembly accessions are in the metadata CSV files (`data/metadata_*.csv`)
- **Metric verification:** `python scripts/verify_regenerated_predictions.py` recomputes metrics from the included prediction CSVs and compares them with saved summaries and calibration scores.
- **Prediction regeneration:** `python scripts/regenerate_test_predictions.py --workers 8` requires the genome FASTAs in `data/genomes/`. These files (about 8.76 GB) are not tracked in Git. Accession, size and SHA-256 values are in `validation_results/all_metadata_genome_manifest.csv`; full regeneration requires obtaining the matching FASTAs.
- **Training:** The pipeline can be retrained from the metadata and genome FASTAs, but that is distinct from reproducing the deployed artifacts.
- **Random seeds:** Fixed at `[42, 123, 456, 789, 1024]` for reproducibility.

### Q38. What are the main limitations of the current models and data?

1. **Species imbalance:** Over 85% of cefotaxime training genomes are *E. coli*. Performance on *K. pneumoniae*, *A. baumannii*, and *P. aeruginosa* is likely weaker.
2. **Geographic skew:** Training data is predominantly from North America and Europe. Two unique Kenyan isolates occur in deployed metadata; both are in training and none in the test split. Performance on local strains is unknown.
3. **Label provenance and breakpoint drift:** The deployed models use NCBI pre-classified S/I/R calls recorded as `MIC_or_mixed`; the breakpoint standard and edition vary by submitting laboratory and have not been re-harmonised. The BV-BRC disk-diffusion labels (EUCAST v14.0) apply only to the non-deployed combined cefotaxime model and the BV-BRC benchmark.
4. **No relatedness-aware split:** Random splitting may inflate AUC when clonally related isolates span the train/test boundary.
5. **No formal genome QC:** No contamination, completeness, or species-confirmation checks.
6. **K-mer proxy for gene detection:** Using three 6-mers per gene is a rough proxy, not equivalent to full-length gene detection (AMRFinderPlus, ResFinder).
7. **Deployment scope:** All three deployed models were trained on the 600-row NCBI metadata (369, 429 and 433 usable training isolates for meropenem, ciprofloxacin and cefotaxime). The 0.7793 combined-model figure is withdrawn pending prediction-level evidence.
8. **No rule-based baseline comparison** yet.

### Q39. What support do you need from KU?

1. **Compute resources:** Access to a GPU-enabled workstation or cloud credits for retraining expanded datasets (3,000+ genomes per drug).
2. **Wet-lab AST confirmation:** Access to a microbiology laboratory for phenotypic confirmation of edge-case predictions (especially borderline MICs near breakpoints).
3. **Local isolates:** Access to Kenyan clinical isolate sequences (through KEMRI partnerships or KU hospital collaborations) to test model performance against regional genomic variation.
4. **Supervision:** Technical mentorship from Dr. Iloka and the IvE team on regulatory pathway, validation study design, and STARD/TRIPOD+AI reporting.
5. **NACOSTI/ethics support:** Guidance on the ethics committee submission and NACOSTI research licence process.

---

## Section 6 Deliverables Checklist

| Deliverable | Status |
|:---|:---|
| This document with response column completed | **Done** (this file) |
| Master isolate table (CSV) with accessions, source, metadata, and partition assignments | **Partially done** -- metadata CSVs exist per drug but lack country, partition assignment, and BioSample columns. Needs consolidation. |
| Results table per drug (model + rule-based baseline, original + relatedness-aware split, external test) | **Partially done** -- model results exist; rule-based baseline and relatedness-aware split are missing. |
| Two-page technical summary for NPHL | **Done** -- `deliverables/NPHL_Technical_Summary.md`. |
| Revised letter (Annex A) with all placeholders completed | **Partially completable** -- many placeholders can now be filled from these answers. |
| Link to code repository with software versions and random seeds | **Done** -- `https://github.com/bactoai-eng/BACTOAI.git`, seeds `[42, 123, 456, 789, 1024]`, Python 3.12. |
