# BactoAI: Project Accomplishments and Roadmap for Local Application in Kenya

## 1. What We Have Accomplished So Far
We have successfully built the core foundation for **BactoAI**, an end-to-end machine learning pipeline that predicts antibiotic resistance in Gram-negative bacteria from raw genomic sequences. Our key achievements include:

### 1.1 Automated Cloud Data Acquisition
- **BigQuery Integration**: We developed a robust data mining script (`expand_dataset.py`) that queries the `ncbi-pathogen-detect` public dataset on Google Cloud BigQuery. 
- **Targeted Assembly**: Concurrently extracts both **resistant** and **susceptible** cohorts for critical Gram-negative pathogens (e.g., *E. coli*, *Klebsiella pneumoniae*, *Pseudomonas aeruginosa*, *Salmonella enterica*).
- **Automated Genome Fetching**: Connected the pipeline to the NCBI Datasets API to seamlessly download, manage, and extract whole-genome FASTA sequences based on the acquired metadata.

### 1.2 Multi-Antibiotic Machine Learning Pipeline
- **End-to-End Predictor (`bactoai_pipeline_v2.py`)**: Built an automated training and prediction pipeline focused on highly relevant antibiotic classes: Carbapenems (*meropenem*), Fluoroquinolones (*ciprofloxacin*), and Cephalosporins (*cefotaxime*).
- **Smart Feature Engineering**: Translated whole-genome assemblies into computational features using k-mer frequency distributions (5-mers) combined with statistical feature selection (`SelectKBest`, chi-squared) to isolate the most predictive DNA sequences.
- **Optimized XGBoost Models**: Configured tree-based models capable of handling non-linear genomic patterns. We tackled significant hurdles like class imbalance by dynamically adjusting `scale_pos_weight` and focusing training to improve recall on the critical "Resistant" class.
- **Predictive Engine**: Integrated an inference CLI that accepts raw genomic sequences, parses them, runs them through our pre-trained models, and provides immediate resistance probabilities in a terminal-friendly format.

---

## 2. How to Proceed with Local Application in Kenya
To translate this prototype into a functional, life-saving tool in Kenyan healthcare settings, we need to transition from global public datasets to localized data and workflows. Here is the strategic roadmap:

### Phase 1: Local Data Partnerships & AMR Surveillance
- **Establish Partnerships**: Collaborate with local research institutes such as the **Kenya Medical Research Institute (KEMRI)**, the **ILRI** (International Livestock Research Institute), and major referral hospitals (e.g., Kenyatta National Hospital, Moi Teaching and Referral Hospital).
- **Curate Local Strains**: Global datasets (NCBI) are often heavily skewed toward North America and Europe. We must collect, sequence, and integrate local Kenyan clinical isolates into our training data. This ensures BactoAI learns the specific genetic resistance mechanisms (e.g., local ESBL or NDM variants) circulating in East Africa.

### Phase 2: Accessible & Cost-Effective Sequencing
- **Nanopore Integration**: Traditional Illumina sequencing is highly centralized and expensive. We should optimize BactoAI to accept and accurately process noisy long-read data from **Oxford Nanopore MinION** devices. These devices are portable, require low capital investment, and are actively being deployed in Kenya for real-time pathogen surveillance.
- **Rapid Turnaround**: Fine-tune the pipeline to run on incomplete genome assemblies or raw reads directly to hasten the turnaround time from patient sample to clinical decision.

### Phase 3: Deployment & Infrastructure Adaptation
- **Low-Bandwidth Web/Mobile Application**: Wrap the BactoAI prediction engine into a lightweight offline-first application or a minimal-bandwidth web portal. Clinic technicians should be able to process sequences with local computing power (e.g., a standard hospital laptop or local specialized server) without needing to upload gigabytes of genomic data over unstable internet connections.
- **Privacy and Data Sovereignty**: Ensure the pipeline processes genomic data locally so that sensitive national health data does not need to cross borders, complying with Kenya's Data Protection Act.

### Phase 4: Capacity Building and Clinical Translation
- **Training Workshops**: Develop training modules for Kenyan bioinformaticians, clinical microbiologists, and laboratory technologists on how to operate the BactoAI platform and interpret its predictions.
- **Clinical Pilot Study**: Run a parallel pilot study in a Kenyan hospital where BactoAI predictions are tested directly against traditional phenotypic AST (Antimicrobial Susceptibility Testing) laboratory results. This will serve to validate the model's accuracy on the ground and build trust among clinicians.
- **Policy Integration**: Work alongside the Kenyan Ministry of Health's National Antimicrobial Resistance Action Plan to position BactoAI as a frontline digital epidemiology and diagnostics tool.

---

## 3. Current Dataset Statistics and Model Diagnostics
### 3.1 Global Dataset Footprint (NCBI Pathogen Detection Data)
Our automated data pipeline successfully pulled and curated a master dataset encompassing **over 1,800 clinical isolates**. The data highlights critical Gram-negative bacteria categorized by resistance to three priority antibiotics:
- **Meropenem (Carbapenem)**: ~600 sequenced isolates evenly split between resistant and susceptible phenotypes.
- **Ciprofloxacin (Fluoroquinolone)**: ~600 sequenced isolates processed for genetic resistance markers to fluoroquinolones.
- **Cefotaxime (Cephalosporin)**: ~600 sequenced isolates evaluated for predicting beta-lactamase (ESBL) driven resistance.
- **Key Pathogens Targeted**: The dataset features heavily modeled representations of *Klebsiella pneumoniae*, *E. coli* & *Shigella*, *Pseudomonas aeruginosa*, *Acinetobacter baumannii*, and *Salmonella enterica*.

### 3.2 Evaluation of Initial Machine Learning Prototypes
The predictive performance generated from our localized XGBoost pipeline (`bactoai_pipeline_v2.py`) using an 80/20 train-test split showcases highly promising clinical viability metrics:

| Antibiotic Focus | Prediction Accuracy | ROC-AUC Score | Test Set Profile (Class Balance) |
|------------------|---------------------|---------------|--------------------------------------------|
| **Meropenem**    | 89.5%               | 0.952         | 70 Resistant / 54 Susceptible              |
| **Ciprofloxacin**| 81.1%               | 0.872         | 70 Resistant / 73 Susceptible              |
| **Cefotaxime**   | 79.3%               | 0.872         | 71 Resistant / 74 Susceptible              |

**Interpretation of Metrics:** 
- The **Meropenem** prediction capability is exceptionally robust, obtaining a 0.95 ROC-AUC. This emphasizes that genomic 5-mer sequences alone strongly and reliably pinpoint carbapenem resistance mutations.
- By configuring class weight adjustments (`scale_pos_weight`), the ML engine avoids simply guessing the majority class. Instead, it maintains consistently high recall rates across predicting both the target "Susceptible" and "Resistant" classes—a crucial requirement for screening patient samples.
