# BactoAI, Revised Letter to NPHL/KNPHI

**Annex A to:** BactoAI: Validating a Genomic AMR Prediction Model  
**Date:** [dd Month 2026]  
**Reference:** [KU/IvE/…/2026]

---

Dear [Name],

I am writing on behalf of the BactoAI team to request your support in validating our machine learning model for predicting antibiotic resistance from bacterial genome sequences.

## What we have built

BactoAI predicts resistance to three antibiotics, meropenem, ciprofloxacin, and cefotaxime, from an assembled genome in under ten minutes. Conventional culture-based phenotypic AST takes an additional approximately 16-20 hours after isolation. The model was trained on more than 5,200 clinical isolates from NCBI Pathogen Detection and BV-BRC, covering five Gram-negative species: Escherichia coli, Klebsiella pneumoniae, Acinetobacter baumannii, Pseudomonas aeruginosa, and Salmonella enterica. The data comes predominantly from USA, UK, and European submissions, with 52 African isolates (3.1%), including 2 from Kenya. AST labels were derived from broth microdilution (MIC) per CLSI M100 for NCBI data, and disk diffusion interpreted with EUCAST clinical breakpoints for BV-BRC data.

## What the model can do

On a 25% held-out test set, the model achieved:

- Meropenem: ROC-AUC 0.987 (95% CI [0.973, 1.000]), sensitivity 97.1%, specificity 96.4%
- Ciprofloxacin: ROC-AUC 0.879 (95% CI [0.820, 0.938]), sensitivity 94.1%, specificity 94.4%
- Cefotaxime: ROC-AUC 0.872 (95% CI [0.807, 0.937]), sensitivity 94.5%, specificity 94.5%

On an independent BV-BRC dataset of 500 E. coli genomes, cefotaxime prediction achieved ROC-AUC 0.933, sensitivity 82.8%, specificity 95.2%.

These results come from retrospective analysis of public data. The training data is largely from North America and Europe (only 2 Kenyan isolates in training out of 5,200+ total), so performance on local strains is not yet known.

## What we need from NPHL

We are writing to request four things, in this order:

1. **Validation of the model on NPHL isolates.** We propose testing the model against broth microdilution AST (ISO 20776-1) on a set of Kenyan clinical isolates. We would split any NPHL data you share into a locked validation portion (30-40%) and a retraining portion (60-70%), so the validation remains independent. The model version used for testing would be frozen and recorded before any new data is touched.

2. **Guidance on the clinical pathway and regulatory requirements.** BactoAI is a clinical decision support tool, not a standalone diagnostic. We need to understand what the Pharmacy and Poisons Board requires, and what steps are needed before the tool can be used in routine clinical practice in Kenya.

3. **A data partnership for model retraining.** There are over 8,000 Kenyan bacterial genomes with AST data publicly available in NCBI databases. Incorporating even a fraction of these into retraining would materially improve performance on local strains. We would like to discuss how NPHL could support this.

4. **Incubation and mentorship through the IvE programme.** We have been selected for a CDIE Catalyst Grant through the Kenyatta University Design Studio. Technical mentorship from the IvE team on validation study design, regulatory navigation, and STARD/TRIPOD+AI reporting would be invaluable.

## About the tool

A working prototype is deployed with a live web platform (bactoai.co.ke) and hosted model backend (Render, Oregon, USA). Uploaded genomes are processed in-memory and deleted after analysis. We acknowledge that hosting US-based servers constitutes cross-border data transfer under the Data Protection Act, 2019. We plan to deploy a Kenya-hosted instance before processing any NPHL data.

## Limitations we are aware of

- The training data is geographically skewed (minimal Kenyan representation). Model performance on local strains is unverified.
- The cefotaxime model mixes MIC-derived and disk-diffusion labels without re-harmonisation to a single breakpoint version.
- Relatedness-aware splitting has not been performed; random train/test splits may inflate AUC when near-clonal isolates span both sets.
- No formal genome quality control (contamination, completeness, species confirmation) is applied.
- A rule-based baseline (AMRFinderPlus or ResFinder) has not yet been run on the test isolates.

We believe these limitations are addressable with the right partnership and data. We would welcome the chance to discuss them with you.

Please find attached a two-page technical summary with fuller details on data, methods, results, and the proposed validation design.

We would be grateful for the opportunity to meet and discuss how we might work together.

Yours sincerely,

[Name]
[Title]
BactoAI Team
Kenyatta University

---

**Attachments:**
- BactoAI Two-Page Technical Summary for NPHL
- BactoAI Validation Capture Workbook (guidance document)
- Code repository: https://github.com/bactoai-eng/BACTOAI.git