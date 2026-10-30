# BactoAI: Dataset Composition Analysis and AMR Acquisition Strategy

**Document:** Dataset Audit and Expansion Roadmap  
**Date:** October 2026  
**Status:** Active Strategy  
**Target Antibiotics:** Cefotaxime, Ciprofloxacin, Meropenem  

---

## 1. Executive Summary

This report reviews the microorganisms, phenotypic test data, and antimicrobial resistance (AMR) targets used across the two data batches in BactoAI: the original NCBI dataset and the subsequent BV-BRC integration.

While integrating BV-BRC expanded the Cefotaxime training cohort to over 4,000 genomes, it created a severe taxonomic imbalance. Over 85% of all project genomes belong to *Escherichia coli*, leaving other high-priority pathogens (*Klebsiella pneumoniae*, *Acinetobacter baumannii*, and *Pseudomonas aeruginosa*) underrepresented. In addition, Ciprofloxacin and Meropenem remain trained only on the original 600-genome NCBI batch.

This report details the exact composition of both datasets, outlines the risks of the current distribution, and defines a prioritized roadmap for acquiring new organisms and resistance phenotypes.

---

## 2. Inventory of Existing Datasets

### 2.1 Batch 1: NCBI Reference Set
* **Source:** NCBI Pathogen Detection and SRA databases.
* **Volume:** 600 isolates per antibiotic model (~1,800 records across 3 antibiotics; 300 resistant and 300 susceptible in each split).
* **Testing modality:** Minimum Inhibitory Concentration (MIC) via broth microdilution.
* **Organism distribution:** Multi-species Gram-negative clinical pathogen panel:
  * *Escherichia coli* and *Shigella*
  * *Klebsiella pneumoniae*
  * *Acinetobacter baumannii*
  * *Pseudomonas aeruginosa* (present in Ciprofloxacin and Meropenem cohorts)
  * *Salmonella enterica* (present in Ciprofloxacin and Cefotaxime cohorts)
* **Metadata files:**
  * [metadata_cefotaxime.csv](file:///c:/Users/User/Documents/RESEARCH/Bacto_AI/data/metadata_cefotaxime.csv)
  * [metadata_ciprofloxacin.csv](file:///c:/Users/User/Documents/RESEARCH/Bacto_AI/data/metadata_ciprofloxacin.csv)
  * [metadata_meropenem.csv](file:///c:/Users/User/Documents/RESEARCH/Bacto_AI/data/metadata_meropenem.csv)

### 2.2 Batch 2: BV-BRC Clinical Hospital Set
* **Source:** Bacterial and Viral Bioinformatics Resource Center (BV-BRC), derived from clinical hospital surveys (PubMed ID: 38219757).
* **Volume:** 6,260 raw entries; 6,090 full FASTA genomes downloaded to `data/bvbrc_genomes/`. 3,419 clean deduplicated records merged with NCBI data to produce 4,019 training/validation isolates.
* **Testing modality:** Disk diffusion (inhibition zone diameter in millimeters).
* **Organisms used:** Exclusively *Escherichia coli* (NCBI Taxon ID: 562).
* **Antibiotics covered:** Cefotaxime only.
* **Metadata file:** [BVBRC_genome_amr.csv](file:///c:/Users/User/Documents/RESEARCH/Bacto_AI/data/BVBRC_genome_amr.csv), merged into [metadata_combined_cefotaxime.csv](file:///c:/Users/User/Documents/RESEARCH/Bacto_AI/data/metadata_combined_cefotaxime.csv).

### 2.3 Cohort Comparison Table

| Metric | Batch 1 (NCBI) | Batch 2 (BV-BRC) | Combined Status |
| :--- | :--- | :--- | :--- |
| **Total Genomes** | ~600 per drug | 6,090 downloaded | 4,019 in active v4 model |
| **Species Included** | *E. coli*, *K. pneumoniae*, *A. baumannii*, *P. aeruginosa*, *S. enterica* | *E. coli* only | >85% *E. coli* |
| **Testing Method** | Broth microdilution (MIC) | Disk diffusion (mm) | Mixed modalities |
| **Cefotaxime Status** | 600 genomes (v3) | 3,419 genomes added | 4,019 genomes (v4 model) |
| **Ciprofloxacin Status**| 600 genomes (v3) | None | 600 genomes (v3 model) |
| **Meropenem Status** | 600 genomes (v3) | None | 600 genomes (v3 model) |

---

## 3. Risks of the Current Dataset Skew

1. **Species-specific feature bias:**
   K-mer models trained predominantly on *E. coli* can learn background genomic signatures characteristic of *E. coli* rather than generalizable resistance mechanisms. When tested on *Klebsiella* or *Acinetobacter*, the model risks false predictions driven by species identification instead of AMR determinants.

2. **Antibiotic capability gap:**
   Cefotaxime has an ensemble model trained on 4,019 genomes with SMOTE and threshold calibration. Meropenem and Ciprofloxacin remain at v3 specifications with only 600 genomes each. Clinicians treating septic patients need reliable carbapenem and quinolone predictions as urgently as cephalosporins.

3. **Phenotypic method divergence:**
   NCBI data reflects MIC thresholds, while BV-BRC data reflects disk diffusion diameters. While EUCAST breakpoints were used to bridge this gap for Cefotaxime, future acquisitions should explicitly track and balance measurement methods.

---

## 4. Priority Organisms and AMR Resistance Targets to Acquire

To build a balanced, clinically dependable diagnostic tool, data expansion should target the following pathogen-drug combinations.

### Priority 1: *Klebsiella pneumoniae* (Carbapenem and Extended-Spectrum Cephalosporin Resistance)
* **Target Antibiotics:** Meropenem, Cefotaxime, Ceftriaxone.
* **Target Genes / Mechanisms:**
  * Carbapenemases: *blaKPC*, *blaNDM*, *blaOXA-48-like*, *blaVIM*.
  * ESBLs: *blaCTX-M-15*, *blaSHV*, *blaTEM*.
  * Porin mutations: *ompK35*, *ompK36* disruptions.
* **Clinical Rationale:**
  Carbapenem-resistant *Klebsiella pneumoniae* (CRKP) is a primary agent of hospital-acquired bacteremia, ventilator-associated pneumonia, and neonatal sepsis. In Kenyan surveillance studies, *Klebsiella* demonstrates high discordance between local phenotypic testing and clinical outcomes. Expanding this species from ~150 isolates to over 2,000 isolates is the single most urgent priority.

### Priority 2: *Acinetobacter baumannii* (Carbapenem and Fluoroquinolone Resistance)
* **Target Antibiotics:** Meropenem, Ciprofloxacin.
* **Target Genes / Mechanisms:**
  * Acquired oxacillinases: *blaOXA-23*, *blaOXA-24/40*, *blaOXA-58*.
  * Overexpression of intrinsic *blaOXA-51* via ISAba1 insertion.
  * Efflux systems: *AdeABC*, *AdeIJK*.
* **Clinical Rationale:**
  Designated a Priority 1 Critical pathogen by the World Health Organization. Most clinical *A. baumannii* strains in ICU settings are multidrug-resistant or extensively drug-resistant. The current training set contains fewer than 150 *A. baumannii* genomes.

### Priority 3: *Escherichia coli* and *Klebsiella pneumoniae* (Fluoroquinolone Resistance)
* **Target Antibiotic:** Ciprofloxacin.
* **Target Genes / Mechanisms:**
  * Quinolone resistance-determining regions (QRDR): point mutations in *gyrA* (S83L, D87N) and *parC* (S80I).
  * Plasmid-mediated quinolone resistance (PMQR): *qnrA*, *qnrB*, *qnrS*, *aac(6')-Ib-cr*.
* **Clinical Rationale:**
  Ciprofloxacin resistance exceeds 60% in many low- and middle-income country hospital settings. Because BV-BRC has tens of thousands of quinolone-tested Enterobacterales, downloading 3,000 to 4,000 ciprofloxacin isolates is technically straightforward and directly leverages existing pipeline scripts.

### Priority 4: *Pseudomonas aeruginosa* (Multidrug Resistance)
* **Target Antibiotics:** Meropenem, Ciprofloxacin, Ceftazidime.
* **Target Genes / Mechanisms:**
  * Loss or downregulation of the *OprD* outer membrane porin.
  * Upregulation of *MexAB-OprM* and *MexXY-OprM* efflux pumps.
  * Metallo-beta-lactamases (*blaVIM*, *blaIMP*).
* **Clinical Rationale:**
  *P. aeruginosa* has the lowest representation in BactoAI (fewer than 50 isolates in the NCBI batch). Given its importance in burn wounds, cystic fibrosis, and ICU infections, acquiring at least 500 to 1,000 characterized genomes is required before making claims of pan-Gram-negative diagnostic utility.

### Priority 5: *Salmonella enterica* (Invasive Non-Typhoidal Salmonella Quinolone Resistance)
* **Target Antibiotics:** Ciprofloxacin, Ceftriaxone.
* **Target Genes / Mechanisms:**
  * Mutations in *gyrA* / *gyrB* / *parC*.
  * Extended-spectrum cephalosporinases (*blaCTX-M*).
* **Clinical Rationale:**
  Invasive non-typhoidal Salmonella (iNTS) is a leading cause of bloodstream infection and mortality among children and immunocompromised patients in sub-Saharan Africa. Reliable quinolone prediction is essential where ciprofloxacin is used as first-line therapy.

---

## 5. Acquisition Roadmap and Technical Implementation

```
+-------------------------------------------------------------------------------+
|                       Phase 1: Quinolone Expansion                            |
| Target: 3,000 E. coli + 1,500 K. pneumoniae tested against Ciprofloxacin       |
| Source: BV-BRC API | Target Script: scripts/download_bvbrc_genomes.py        |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                     Phase 2: Carbapenem Multi-Species Batch                   |
| Target: 2,000 K. pneumoniae + 1,000 A. baumannii tested against Meropenem     |
| Source: BV-BRC & NCBI Pathogen Detection                                      |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                     Phase 3: Pseudomonas & Local Isolates                     |
| Target: 1,000 P. aeruginosa + Kenyan hospital/surveillance isolate sequences   |
| Source: KEMRI partnerships, NCBI Bioprojects, local hospital collaborations   |
+-------------------------------------------------------------------------------+
```

### 5.1 Query Filters for BV-BRC API
When querying the BV-BRC REST endpoint, apply the following parameter filters to collect target records:
* **Taxon ID filters:**
  * `eq(taxon_id,562)` for *Escherichia coli*
  * `eq(taxon_id,573)` for *Klebsiella pneumoniae*
  * `eq(taxon_id,470)` for *Acinetobacter baumannii*
  * `eq(taxon_id,287)` for *Pseudomonas aeruginosa*
* **Antibiotic filters:**
  * `eq(antibiotic,ciprofloxacin)`
  * `eq(antibiotic,meropenem)`
* **Quality constraints:**
  * Filter for records with `laboratory_typing_method` present.
  * Require either a standard phenotype label (`Resistant` / `Susceptible`) or numerical measurements with documented units (`mg/L` for MIC or `mm` for disk diffusion).

### 5.2 Breakpoint Standardization
All newly gathered numerical data must be converted using official EUCAST clinical breakpoint tables (v14.0 or v15.0):
* **Meropenem (Enterobacterales):** Susceptible $\le 2\text{ mg/L}$, Resistant $> 8\text{ mg/L}$ (MIC); Susceptible $\ge 22\text{ mm}$, Resistant $< 16\text{ mm}$ (Disk).
* **Ciprofloxacin (Enterobacterales):** Susceptible $\le 0.25\text{ mg/L}$, Resistant $> 0.5\text{ mg/L}$ (MIC); Susceptible $\ge 25\text{ mm}$, Resistant $< 22\text{ mm}$ (Disk).

### 5.3 Storage and Memory Management
* Continue using the `KmerGenomeIterator` generator implemented in [bactoai_pipeline.py](file:///c:/Users/User/Documents/RESEARCH/Bacto_AI/bactoai_pipeline.py) so that processing thousands of newly downloaded FASTA files keeps memory consumption under 200 MB.
* Save raw genomes to dedicated subfolders (`data/bvbrc_genomes_ciprofloxacin/`, `data/bvbrc_genomes_meropenem/`) and ensure paths remain registered in [.gitignore](file:///c:/Users/User/Documents/RESEARCH/Bacto_AI/.gitignore).

---

## 6. Summary of Action Items

1. **Ciprofloxacin BV-BRC download:** Run an automated query for *E. coli* and *K. pneumoniae* ciprofloxacin records from BV-BRC.
2. **Meropenem BV-BRC download:** Query *K. pneumoniae* and *A. baumannii* meropenem records to balance the carbapenem model.
3. **Model retrain (v4 specification):** Apply SMOTE, Platt scaling, and the 5-seed ensemble to Ciprofloxacin and Meropenem, bringing them to parity with the Cefotaxime pipeline.
4. **Local validation:** Prioritize obtaining East African clinical isolate sequences (e.g. from KEMRI studies) to test model performance against regional genomic epidemiology.
