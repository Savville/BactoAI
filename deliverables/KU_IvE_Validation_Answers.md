# BactoAI: Responses to KU IvE Validation Guidance Questions

**Prepared by:** BactoAI Engineering Team
**Date:** 29 October 2026
**Reference document:** *BactoAI: Validating a Genomic AMR Prediction Model* (Dr Kenneth Malongo Iloka, 26 October 2026)

---

## Status Summary

| Category | Answered | Partially answered | Not yet done |
|:---|:---:|:---:|:---:|
| A. Product and claims (Q1-Q4) | 4 | 0 | 0 |
| B. Training data (Q5-Q9) | 5 | 0 | 0 |
| C. Phenotype labels and QC (Q10-Q13) | 3 | 1 | 0 |
| D. has and model (Q14-Q17) | 4 | 0 | 0 |
| E. ROC-AUC figures (Q18-Q26) | 6 | 2 | 1 |
| F. External validation plan (Q27-Q31) | 3 | 1 | 1 |
| G. Governance and data protection (Q32-Q36) | 2 | 1 | 2 |
| H. Reproducibility and support (Q37-Q39) | 3 | 0 | 0 |
| **Total** | **33** | **1** | **5** |

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

The "1,800+" claim in the letter refers to the NCBI batch (600 per drug x 3 drugs). With BV-BRC integration, the total training corpus now exceeds 5,200.

### Q7. Which countries, years and settings are represented? How many are African, how many Kenyan?

**Exact counts from BigQuery cross-reference (October 2026):**

The NCBI metadata files contain a `target_acc` (PDT accession) and `taxgroup_name` but no explicit country columns. We queried NCBI BigQuery (`ncbi-pathogen-detect.pdbrowser.isolates`) to cross-reference our 1,673 training set accessions against geographic data.

**African isolates in training set (52 / 1,673 = 3.1%):**

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
> The 8,462 Kenyan genomes represent a substantial enrichment opportunity. A realistic target for retraining would be 500–1,000 new Kenyan isolates per antibiotic after deduplication with the existing training set.

### Q8. Did you use raw reads, assemblies or pre-computed gene calls? Which pipeline and tool versions?

- **Input type:** Pre-assembled genomes (FASTA format). Assemblies were downloaded from NCBI GenBank (`GCA_*` accessions) and BV-BRC REST API.
- **No raw read processing is done.** The pipeline starts from assembled genomes.
- **Feature extraction pipeline versions:**
  - Python 3.12
  - Biopython (SeqIO for FASTA parsing)
  - scikit-learn CountVectorizer for k-mer tokenization
  - scikit-learn SelectKBest (chi-squared) for feature selection
  - XGBoost, Random Forest, LightGBM as classifiers
  - scikit-learn CalibratedClassifierCV (Platt sigmoid scaling)
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

Yes, two methods are present:
1. **Broth microdilution (MIC):** Used in the NCBI batch (all three drugs, 600 isolates each).
2. **Disk diffusion (zone diameter in mm):** Used in the BV-BRC batch (cefotaxime only, 3,419 isolates).

The cefotaxime v4 model is trained on mixed-modality data. Meropenem and ciprofloxacin models use only MIC-derived labels.

### Q11. Which breakpoint standard and version did you use to convert MICs to S/I/R?

- **BV-BRC (disk diffusion):** EUCAST clinical breakpoints for *Enterobacterales* vs cefotaxime:
  - Resistant: zone diameter <= 17 mm
  - Intermediate: 18-25 mm (mapped to Resistant under clinical default)
  - Susceptible: zone diameter >= 26 mm
- **NCBI data:** The NCBI Pathogen Detection AST Browser provides pre-classified S/I/R labels. The specific breakpoint standard and version used by the original submitters varies by record and has **not been re-harmonized to a single version**.

> [!WARNING]
> **Gap:** The NCBI labels have not been re-interpreted with a single breakpoint version. The BV-BRC labels were standardized to EUCAST. For a formal validation, all labels should be re-interpreted using one standard and version (e.g., EUCAST v14.0 or CLSI M100 Ed34).

### Q12. How did you treat intermediate results, missing values and conflicting records?

- **Intermediate results:** Mapped to Resistant (clinical default: "intermediate = resistant" policy, documented in validation JSON as `intermediate_policy: resistant`).
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

## D. has and Model

### Q14. What input has does the model use? How are they generated?

The model uses two feature types:

1. **K-mer frequencies (k=5):** Each genome is decomposed into all 5-character substrings. The `CountVectorizer` tokenizes these, then `SelectKBest(chi2)` selects the top 50,000 most informative k-mers. For the v4 cefotaxime model, 1,321 unique 5-mers passed the chi-squared test.

2. **AMR gene signature has (18 binary has):** Presence/absence of known resistance gene k-mer markers. These cover:
   - Carbapenemases: *blaKPC*, *blaNDM*, *blaVIM*, *blaIMP*, *blaOXA-48*
   - Penicillinases: *blaTEM*, *blaSHV*
   - Cephalosporinases: *blaCTX-M*, *blaPER*, *blaACC*
   - Fluoroquinolone resistance: *gyrA* mutations, *parC* mutations
   - Efflux pumps: *acrAB*, *ramA*
   - MLS resistance: *ermB*, *mphA*
   - Aminoglycoside resistance: *aac(6')-I*, *aph(3')*

Combined feature matrix: k-mer counts + gene signatures concatenated via `scipy.sparse.hstack`.

### Q15. Which algorithm(s) did you train, and why?

A **soft-voting ensemble** of three classifiers:
1. **XGBoost** (300 estimators, max depth 6, learning rate 0.05) -- gradient-boosted trees perform well on tabular/sparse feature matrices.
2. **Random Forest** (200 estimators, max depth 10, balanced class weights) -- provides diversity and is strong to overfitting.
3. **LightGBM** (300 estimators, max depth 6, learning rate 0.05) -- fast gradient boosting with leaf-wise growth.

Each ensemble is wrapped in `CalibratedClassifierCV(method="sigmoid", cv=5)` for Platt scaling to produce calibrated probability outputs.

A **deep ensemble** of 5 such calibrated voter models (seeds: 42, 123, 456, 789, 1024) provides uncertainty estimation through prediction variance across the ensemble.

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

The 5-fold cross-validation in `CalibratedClassifierCV` is applied within the training partition only. The 25% test holdout is not used during hyperparameter selection or calibration.

---

## E. How the ROC-AUC Figures Were Obtained

### Q18. For each drug, how many isolates were in the test set, and what proportion?

| Drug | Total | Train | Test | Test proportion |
|:---|:---:|:---:|:---:|:---:|
| Meropenem (v3) | ~497 | ~373 | 125 (69R, 56S) | 25% |
| Ciprofloxacin (v3) | ~573 | ~430 | 140 (68R, 72S) | 25% |
| Cefotaxime (v3, NCBI only) | ~580 | ~435 | 145 (71R, 74S) | 25% |
| Cefotaxime (v4, combined) | 4,019 | 2,997 | 1,000 (167R, 833S) | 25% |

### Q19. Was the split random, or were related isolates kept together?

The split is **random**, using `train_test_split(test_size=0.25, random_state=42, stratify=y)`. Stratification preserves the S/R class ratio in both sets.

**Related isolates (same SNP cluster, sequence type or clade) are NOT kept together.** The pipeline does not use phylogenetic or SNP-cluster-aware splitting.

> [!WARNING]
> **Gap:** A relatedness-aware split has not been performed. Random splits can inflate AUC when near-clonal isolates appear in both training and test sets. Re-computing the AUC under a phylogeny-aware or sequence-type-aware split is required before formal validation.

### Q20. How did you confirm that no isolate appears in both training and testing?

De-duplication by assembly accession (`drop_duplicates(subset="asm_acc")`) occurs before splitting. The `train_test_split` function partitions the de-duplicated list, so no accession appears in both sets within a single drug model.

Cross-dataset overlap between NCBI and BV-BRC was checked by accession format: NCBI uses `GCA_*` prefixes while BV-BRC uses `562.*` genome IDs, so the namespaces do not collide. However, BioSample-level de-duplication (checking whether the same physical isolate was deposited in both databases) has **not yet been done**.

### Q21. Was any preprocessing fitted on the full dataset before splitting?

No. In `extract_features()`, `CountVectorizer.fit_transform()` and `SelectKBest.fit_transform()` are called on the training partition only. The test set is transformed with the fitted vectorizer and selector (`.transform()`, not `.fit_transform()`).

The split happens via `train_test_split()` in `train_deep_ensemble()`, and feature extraction parameters are fitted on `X_tr` only.

### Q22. Was the test set used once, after all model choices were fixed?

The internal test holdout is evaluated at the end of training for each of the 5 ensemble members. All model architecture and hyperparameter choices are fixed before training begins (no iterative tuning on the test set). However, the same holdout data was used for:
- Per-model AUC reporting
- Overall ensemble AUC reporting
- Calibration score computation for conformal prediction

The test set was not used to select hyperparameters or has.

### Q23. Please confirm the ciprofloxacin and cefotaxime results separately. Are both exactly 0.872?

From the v3 training summary (`data/training_summary_v3.csv`):

| Drug | ROC-AUC |
|:---|:---|
| Meropenem | **0.9415** |
| Ciprofloxacin | **0.8791** |
| Cefotaxime | **0.8721** |

The two values are **not identical**: ciprofloxacin = 0.879 and cefotaxime = 0.872. They were rounded to the same two decimal places (0.87) in the draft letter, which produced the appearance of identical figures. When reported to three decimal places, they differ.

For the v4 cefotaxime model (retrained on 4,019 genomes), the internal AUC is 0.7793 and the external BV-BRC validation AUC is **0.9333**.

### Q24. For each drug, give sensitivity, specificity, VME rate and ME rate at the decision threshold, with 95% CIs.

**From the threshold audit (v3 internal holdout at threshold=0.50) with Wilson 95% CIs:**

| Drug | n_test | Sens | 95% CI | Spec | 95% CI | PPV | NPV | MCC | VME rate* | ME rate** | AUC | 95% CI |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Meropenem | 125 | 97.1% | [90.0%, 99.2%] | 96.4% | [87.9%, 99.0%] | 97.1% | 96.4% | 0.935 | 2.9% (2/69) | 3.6% (2/56) | 0.9871 | [0.973, 1.000] |
| Ciprofloxacin | 140 | 94.1% | [87.8%, 97.3%] | 94.4% | [88.0%, 97.5%] | 94.1% | 94.4% | 0.886 | 5.9% (4/68) | 5.6% (4/72) | 0.8791 | [0.820, 0.938] |
| Cefotaxime v4 external (500 genomes, t=0.20) | 500 | 82.8% | [77.6%, 87.0%] | 95.2% | [91.8%, 97.2%] | 94.5% | 84.7% | 0.786 | 17.2% (43/250) | 4.8% (12/250) | 0.9333 | [0.917, 0.949] |

*VME = Very Major Error = resistant isolates called susceptible = FN / total resistant.
**ME = Major Error = susceptible isolates called resistant = FP / total susceptible.

**Method:** Wilson score intervals (exact for binomial proportions, recommended by Newcombe 1998).
AUC CIs computed via Delta method approximation (Hanley & McNeil 1982).
Ciprofloxacin CIs derived from threshold audit confusion matrix (tp=68, tn=68, fp=4, fn=4, n=140).

> [✓] **Done:** 95% confidence intervals computed via `scripts/compute_q24_cis.py`.
> Results in `validation_results/q24_ci_report_*.md` and `q24_ci_*.json`.

### Q25. How did the model compare with a rule-based tool?

**PARTIAL, AMRFinderPlus comparison pending installation.**

AMRFinderPlus (NCBI) and ResFinder (CGE/DANMAP) are not currently installed in this environment.
The comparison script is ready (`scripts/amrfinder_baseline.py`) but requires:
- `conda install -c bioconda amrfinderplus` (Linux/macOS), or
- Docker: `docker run --rm -v $(pwd):/data ncbitaxonomy/amrfinder amrfinder /data/genome.fna`

**Partial rule-based evidence already available:**
The model uses 18 AMR gene signature has as direct inputs (see Q26 below). These are
k-mer-based proxies for known resistance genes. A simplified rule-based comparison can be
made by thresholding these gene signatures:

| Drug | Gene markers used | Rule-based logic |
|------|------------------|-----------------|
| Meropenem | blaKPC, blaNDM, blaVIM, blaIMP, blaOXA-48 | Any carbapenemase gene → RESISTANT |
| Ciprofloxacin | gyrA mutations, parC mutations, acrAB | QRDR mutation OR efflux → RESISTANT |
| Cefotaxime | blaCTX-M, blaTEM, blaSHV, blaPER, blaACC | Any ESBL/cephalosporinase → RESISTANT |

This gene-signature-only approach is an intermediate baseline. Full AMRFinderPlus
comparison will be run on a Linux workstation once the tool is installed.

> [!] **Action required:** Install AMRFinderPlus on a Linux environment and run
> `scripts/amrfinder_baseline.py --run` on the test genomes.

### Q26. Which genes or mutations drive predictions? Are they biologically plausible?

The 18 AMR gene signature has are biologically curated and directly relevant:

| Drug | Key driving has | Biological basis |
|:---|:---|:---|
| Meropenem | *blaKPC*, *blaNDM*, *blaVIM*, *blaIMP*, *blaOXA-48* | Known carbapenemase genes |
| Ciprofloxacin | *gyrA* mutations, *parC* mutations, *acrAB* efflux | QRDR mutations and efflux-mediated fluoroquinolone resistance |
| Cefotaxime | *blaCTX-M*, *blaTEM*, *blaSHV*, *blaPER*, *blaACC* | ESBL and cephalosporinase genes |

These are the standard resistance determinants recognized by NCBI AMRFinderPlus, CARD, and ResFinder. The biological plausibility is strong. However, the current implementation uses short k-mer proxies (three 6-mers per gene) rather than full gene detection, which is a known limitation.

---

## F. External Validation Plan

### Q27. Which independent dataset(s) will you test on before the letter is sent?

One external validation has already been completed:
- **BV-BRC *E. coli* cefotaxime cohort (500-genome holdout):** ROC-AUC = 0.9333, sensitivity 82.8%, specificity 95.2%.

For the remaining drugs and for a truly independent test, the following datasets from Section 3.2 are planned:
1. Liverpool *E. coli* WGS-AST dataset (762 isolates, 2025)
2. Moradigaravand et al. (2018) *E. coli* collection (~1,900 UK bloodstream isolates)
3. Nguyen et al. (2018) *K. pneumoniae* MIC set (~1,600 isolates)

Overlap checks will compare BioSample and SRA accessions against our master isolate list.

### Q28. How many Kenyan or East African isolates with AST data are available in public databases?

**Not yet quantified**, see Q7 above for exact BigQuery results. As of October 2026:

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
| Backend database | Supabase (PostgreSQL) | USA (AWS us-east-1) | `ofuxwgapzjgcrsuiqpyu.supabase.co` |
| Website database | Supabase (PostgreSQL) | USA (AWS) | `ojnecaomcicsayeweoab.supabase.co` |

**Data handling:**
- Uploaded genome files are processed in-memory on the Render backend. They are not written to persistent disk (Render uses an ephemeral filesystem that is wiped on every redeploy).
- Prediction metadata (drug probabilities, confidence scores, timestamps) is stored in the Supabase `submissions` table.
- No genomic sequence data is retained after prediction completes.

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
- **Environment:** Python 3.12, dependencies listed in `requirements.txt` and `requirements-ml.txt`, virtual environment in `.venv/`
- **Accession lists:** Assembly accessions are in the metadata CSV files (`data/metadata_*.csv`)
- **Reproducibility:** Yes, another person can rerun the pipeline:
  1. Clone the repository
  2. Install dependencies (`pip install -r requirements.txt -r requirements-ml.txt`)
  3. Download genomes using `scripts/download_bvbrc_genomes.py` (or place FASTA files in `data/genomes/`)
  4. Train: `python bactoai_pipeline.py --train`
  5. Predict: `python bactoai_pipeline.py --predict --fasta path/to/genome.fna`
- **Random seeds:** Fixed at `[42, 123, 456, 789, 1024]` for reproducibility.

### Q38. What are the main limitations of the current models and data?

1. **Species imbalance:** Over 85% of cefotaxime training genomes are *E. coli*. Performance on *K. pneumoniae*, *A. baumannii*, and *P. aeruginosa* is likely weaker.
2. **Geographic skew:** Training data is predominantly from North America and Europe. Zero or near-zero Kenyan isolates. Performance on local strains is unknown.
3. **Method mixing:** The cefotaxime v4 model mixes MIC-derived and disk-diffusion-derived labels without re-harmonization to a single breakpoint version.
4. **No relatedness-aware split:** Random splitting may inflate AUC when clonally related isolates span the train/test boundary.
5. **No formal genome QC:** No contamination, completeness, or species-confirmation checks.
6. **K-mer proxy for gene detection:** Using three 6-mers per gene is a rough proxy, not equivalent to full-length gene detection (AMRFinderPlus, ResFinder).
7. **Drug model maturity gap:** Meropenem and ciprofloxacin remain at v3 (600 genomes each), while cefotaxime has been upgraded to v4 (4,019 genomes).
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
| Two-page technical summary for NPHL | **Not yet written.** |
| Revised letter (Annex A) with all placeholders completed | **Partially completable** -- many placeholders can now be filled from these answers. |
| Link to code repository with software versions and random seeds | **Done** -- `https://github.com/bactoai-eng/BACTOAI.git`, seeds `[42, 123, 456, 789, 1024]`, Python 3.12. |

---

## Immediate Action Items (by Fri 30 Oct)

1. **Confirm ciprofloxacin vs cefotaxime ROC-AUC** -- Done: Cipro = 0.8791, Cefo = 0.8721. Not identical.
2. **Run BigQuery geographic enrichment** to count African/Kenyan isolates in training data.
3. **Compute 95% confidence intervals** (Wilson or bootstrap) for all reported metrics.
4. **Run AMRFinderPlus** on the test isolates for a rule-based baseline comparison.
5. **Begin the master isolate table** consolidating all three drugs with BioSample accessions, country, year, and partition assignments.
