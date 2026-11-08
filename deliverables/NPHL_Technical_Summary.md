# BactoAI Technical Summary for NPHL

**8 November 2026** · Current model artifacts: `data/models_v4/`

## Purpose and status

BactoAI predicts susceptible or resistant calls for meropenem, ciprofloxacin and cefotaxime from assembled bacterial genomes. It is a clinical decision-support prototype, not a replacement for phenotypic antimicrobial susceptibility testing (AST). The intended next step is prospective validation against reference AST on Kenyan clinical isolates.

## Data and method

Each deployed drug model uses 600 NCBI Pathogen Detection records; after excluding unavailable or unreadable FASTAs, the training partitions contained 369 meropenem, 429 ciprofloxacin and 433 cefotaxime isolates. Across drugs there are 1,673 unique NCBI accessions, including 52 from Africa and two from Kenya. Each `metadata_{drug}.csv` contains NCBI labels only (600 per drug; zero BV-BRC labels).

Labels are pre-classified susceptible/intermediate/resistant calls recorded as `MIC_or_mixed`. Submitter methods and breakpoint editions are not consistently available, and the labels have not been re-harmonised. The separate BV-BRC cefotaxime data was not used by deployed models.

Five saved `CalibratedClassifierCV` models are used per drug. Each wraps a soft-voting classifier with XGBoost, Random Forest and LightGBM. Features combine 5-mer counts and 18 binary AMR-marker proxies; these proxies do not replace full gene or mutation detection. The holdout was a stratified random 25% split. No ANI/SNP-relatedness split or formal genome quality-control step has been performed.

## Held-out results

| Drug | n (R/S) | Sensitivity | Specificity | VME | ME | AUC (95% CI) | Low confidence |
|:--|--:|--:|--:|--:|--:|:--|--:|
| Meropenem | 124 (70/54) | 91.4% | 87.0% | 8.6% (6/70) | 13.0% (7/54) | 0.9421 (0.9009–0.9832) | 0/124 |
| Ciprofloxacin | 143 (70/73) | 80.0% | 83.6% | 20.0% (14/70) | 16.4% (12/73) | 0.8773 (0.8189–0.9357) | 0/143 |
| Cefotaxime | 145 (71/74) | 83.1% | 74.3% | 16.9% (12/71) | 25.7% (19/74) | 0.8723 (0.8132–0.9314) | 0/145 |

These are retrospective holdout results, not external validation. The live rule raises the resistance cutoff from 0.50 by `min(0.5 × ensemble standard deviation, 0.15)`; confidence cutoffs are 0.05 and 0.15. It produced no call changes in the 412 holdout rows. Threshold provenance is undocumented, and raising the cutoff can increase missed resistance; it is not a validated safety feature.

The in-corpus BV-BRC benchmark has AUC 0.9333 from 500 rows. Its stored 0.20 operating point gives TP=207, TN=238, FP=12 and FN=43; the threshold-selection rationale is undocumented, so this is not independent validation. The reported 0.7793 combined-model AUC is withdrawn because its row-level predictions are unavailable. The current cefotaxime v4 holdout AUC is 0.872288 (114/145 correct; 78.62% accuracy); the historical v3 summary reports AUC 0.872097 and 79.31%, but its model and predictions are unavailable for reconciliation.

## Limitations and validation plan

The dataset is geographically skewed, label breakpoints are not harmonised, and performance on local strains is unknown. Random splitting may place related isolates across train and test; this has not been measured. No independent external validation or head-to-head AMRFinderPlus/ResFinder comparison has been completed.

For NPHL validation, freeze and hash the model before accessing outcomes; compare blinded predictions with broth microdilution AST (ISO 20776-1), interpreted under one agreed CLSI or EUCAST edition. Keep a locked validation partition separate from any retraining data and report categorical agreement, sensitivity, specificity, VME/ME and confidence intervals. Obtain ethics approval, a NACOSTI licence and regulatory guidance before clinical use.

## Reproducibility

The included prediction CSVs, test splits, verification script, model manifest, metadata and source data support independent metric checks. `scripts/verify_regenerated_predictions.py` verifies the CSVs without FASTAs. Regeneration requires the matching FASTAs listed in `validation_results/all_metadata_genome_manifest.csv`; the 1,765 genome files (about 8.76 GB) are not tracked in Git. The repository branch contains the scripts and outputs, but full sequence-level regeneration requires obtaining those files.
