# BactoAI, Two-Page Technical Summary for NPHL

**Prepared:** 30 October 2026  
**Version:** v4.1  
**Repository:** https://github.com/bactoai-eng/BACTOAI.git

---

## 1. Intended Use

BactoAI is a **clinical decision support tool** that predicts antibiotic resistance from bacterial genome sequences. It outputs a resistance call (Susceptible or Resistant) for three antibiotics, meropenem, ciprofloxacin, and cefotaxime, for five Gram-negative pathogen species. The tool is intended to **complement** (not replace) conventional phenotypic AST, providing results within minutes of genome assembly.

**Target users:** Clinical microbiology laboratories, reference centres, and public health labs performing antimicrobial resistance surveillance.

**Intended context:** Kenya and East Africa, where carbapenem and fluoroquinolone resistance rates are among the highest globally, and where rapid resistance profiling could change empiric therapy decisions.

---

## 2. Data

### Training Data (5,219 isolates)

| Source | Isolates | Antibiotics | Organisms |
|--------|---------:|-------------|-----------|
| NCBI Pathogen Detection AST Browser | ~1,800 | All three | E. coli, K. pneumoniae, A. baumannii, P. aeruginosa, S. enterica |
| BV-BRC (formerly PATRIC) | 3,419 | Cefotaxime only | E. coli |

**Geographic distribution:** Predominantly North America and Europe. African isolates: 52 (3.1%), including 2 from Kenya. Over 8,400 Kenyan genomes with AST are publicly available in NCBI BigQuery but not yet incorporated into training.

**AST methods:** Broth microdilution (MIC) for NCBI batch; disk diffusion for BV-BRC batch. Breakpoint standards: CLSI M100 (NCBI), EUCAST (BV-BRC). **Limitation:** Labels have not been re-harmonized to a single breakpoint version.

**Input:** Assembled genome in FASTA format (`.fna`, `.fasta`, or `.fna.gz`). No raw read processing. Platform-agnostic (Illumina and Nanopore assemblies both work).

---

## 3. Methods

### Model Architecture

**Ensemble of 3 classifiers, deep stacked 5 times:**

1. **XGBoost**, 300 estimators, max depth 6, learning rate 0.05
2. **Random Forest**, 200 estimators, max depth 10, balanced class weights
3. **LightGBM**, 300 estimators, max depth 6, learning rate 0.05

Each wrapped in Platt sigmoid calibration (5-fold CV). Five random seeds: 42, 123, 456, 789, 1024. Prediction = mean probability across all 15 models.

### has

- **K-mer frequencies (k=5):** CountVectorizer tokenizes all 5-character substrings; SelectKBest(chi-squared) selects top 50,000 has. For the v4 cefotaxime model, 1,321 unique 5-mers passed the significance threshold.
- **AMR gene signatures (18 binary has):** Presence/absence proxies for known resistance genes:
  - Carbapenemases: blaKPC, blaNDM, blaVIM, blaIMP, blaOXA-48
  - ESBLs: blaCTX-M, blaTEM, blaSHV, blaPER, blaACC
  - Fluoroquinolone targets: gyrA mutations, parC mutations
  - Efflux: acrAB, ramA
  - Other: ermB, mphA, aac(6')-I, aph(3')

### Training Pipeline

- Class balance: SMOTE oversampling when minority class < 60%; scale_pos_weight for tree models
- Train/test split: 75/25 random stratified split (random_state=42)
- Feature extraction fitted only on training set (no data leakage)
- Depicted in `bactoai_pipeline.py` (Created: 2026-07-22)

---

## 4. Results

### Internal Holdout (25% test split, threshold = 0.50)

| Drug | n | Sensitivity | 95% CI | Specificity | 95% CI | AUC | 95% CI | VME | ME |
|------|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Meropenem | 125 | 97.1% | [90.0%, 99.2%] | 96.4% | [87.9%, 99.0%] | 0.987 | [0.973, 1.000] | 2.9% | 3.6% |
| Ciprofloxacin | 140 | 94.1% | [87.8%, 97.3%] | 94.4% | [88.0%, 97.5%] | 0.879 | [0.820, 0.938] | 5.9% | 5.6% |
| Cefotaxime (v3) | 145 | 94.5% | [88.8%, 97.5%] | 94.5% | [88.8%, 97.5%] | 0.872 | [0.807, 0.937] | 5.5% | 5.5% |

*VME = Very Major Error (resistant called susceptible); ME = Major Error (susceptible called resistant)*

### External Validation (BV-BRC E. coli cefotaxime cohort)

| Metric | Value |
|--------|------:|
| Test isolates | 500 |
| AUC | 0.933 |
| Sensitivity | 82.8% |
| Specificity | 95.2% |
| VME | 17.2% (43/250) |
| ME | 4.8% (12/250) |

**Note:** Ciprofloxacin and meropenem have not yet been externally validated on an independent dataset.

### 95% Confidence Intervals

Computed using Wilson score intervals (exact for binomial proportions) for sensitivity and specificity; Delta method (Hanley & McNeil 1982) for AUC CIs. Full methodology in `scripts/compute_q24_cis.py` and `validation_results/q24_ci_report_*.md`.

---

## 5. Limitations

1. **Geographic skew:** Training data is predominantly North American and European. Only 2 of 5,200+ training isolates are Kenyan. Performance on local strains is unknown. ~8,400 Kenyan genomes with AST are publicly available in NCBI BigQuery and should be incorporated before clinical deployment.

2. **Species imbalance:** Over 85% of cefotaxime training genomes are E. coli. Performance on K. pneumoniae, A. baumannii, and P. aeruginosa is likely weaker.

3. **Mixed AST methods:** Cefotaxime model combines MIC-derived and disk-diffusion labels without re-harmonization to a single breakpoint version.

4. **No relatedness-aware split:** Random train/test split may inflate AUC when clonally related isolates appear in both sets. A phylogeny-aware split has not been performed.

5. **No formal genome QC:** No contamination, completeness, or species-confirmation checks are applied to input genomes.

6. **K-mer proxy for gene detection:** The 18 AMR gene signature has use short k-mer matches as proxies, not full-length gene detection. This is a simplification relative to tools like AMRFinderPlus or ResFinder.

7. **Drug maturity gap:** Meropenem and ciprofloxacin are at model version 3 (600 genomes each); cefotaxime is at version 4 (4,019 genomes).

8. **No rule-based baseline comparison:** AMRFinderPlus was not run on the test isolates. A simplified gene-signature-only baseline exists but is not equivalent to full gene detection.

---

## 6. Proposed Validation Design for NPHL

### Study Objective

Estimate the clinical performance of BactoAI for predicting meropenem, ciprofloxacin, and cefotaxime resistance in Kenyan clinical isolates, against broth microdilution AST as the reference standard.

### Sample Size

- Minimum **100 isolates per species-drug combination** (5 species × 3 drugs = 15 cells)
- Preferred: **200 isolates per cell** for adequate power to detect VME > 1.5%
- Total: approximately **1,500–3,000 isolates** depending on species distribution

### Reference Method

- Broth microdilution per **ISO 20776-1**
- Interpretation per **CLSI M100 Ed34** or **EUCAST v14.0** (to be agreed with NPHL)
- Quality control strains per CLSI guidelines

### Blinding

- Laboratory staff performing phenotypic AST will be **blinded** to BactoAI predictions
- Genome sequencing and prediction will be performed from a **frozen model version** before phenotypic results are available
- Predictions generated by the deployed model at `bactoai.co.ke` using the locked code version

### Data Separation

- On receipt, NPHL isolates will be randomly assigned to:
  - **Locked validation partition (30–40%):** Excluded from all training, tuning, and feature selection
  - **Retraining partition (60–70%):** Available for model improvement after validation is complete
- Partition assignments will be logged in writing and shared with NPHL before any retraining begins
- The model version used for validation will be tagged (e.g., `v4.1-nphl-frozen`) and all artifacts hashed (SHA-256)

### Reporting

- Primary: categorical agreement, sensitivity, specificity, VME rate, ME rate with 95% CIs
- Secondary: AUC, PPV, NPV, calibration
- Reporting standards: **STARD 2015** (diagnostic accuracy) and **TRIPOD+AI** (prediction model)
- Results shared with NPHL before any publication

### Regulatory Pathway

BactoAI is positioned as a clinical decision support tool, not a standalone diagnostic. Prior to clinical deployment in Kenya, the team will:
1. Draft an intended-use statement
2. Seek regulatory guidance from the **Pharmacy and Poisons Board**
3. Complete ODPC registration and a Data Protection Impact Assessment
4. Obtain ethics approval from the Kenyatta University Ethical Review Committee and NACOSTI research licence

---

## 7. Code and Reproducibility

- **Repository:** https://github.com/bactoai-eng/BACTOAI.git
- **Synchronized mirrors:** https://github.com/Savville/BactoAI.git
- **Environment:** Python 3.12, virtual environment in `.venv/`
- **Dependencies:** `requirements.txt` (Flask, Supabase), `requirements-ml.txt` (XGBoost, scikit-learn, LightGBM)
- **Random seeds:** [42, 123, 456, 789, 1024]
- **To reproduce:** Clone repo → install deps → `python bactoai_pipeline.py --train`
- **Model files:** `data/models_v4/` (15 `.joblib` files), `data/transformers_v4/` (6 `.joblib` files)
- **Validation scripts:** `scripts/compute_q24_cis.py`, `scripts/kenya_audit_fast.py`, `scripts/amrfinder_baseline.py`

---

*This document is a living summary. For full methodology, see `deliverables/KU_IvE_Validation_Answers.md` and the code repository.*