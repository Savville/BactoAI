---
title: BactoAI -- Machine Learning Pipeline Concept Note
---

# Objective of the Model

Build a machine learning model that predicts antibiotic resistance in
Gram■negative bacteria using genomic data.

Input:

-   Bacterial genome sequence (FASTA / FASTQ)

Output:

-   Probability that the bacterium is resistant or susceptible to
    specific antibiotics.

# Machine Learning Problem Type

This is a supervised classification problem.

Input features: genomic features derived from DNA sequences. Target
variable: antibiotic resistance phenotype.

Label encoding:

1 = resistant

0 = susceptible

# Target Bacterial Species (Prototype)

Initial focus:

-   Escherichia coli

-   Klebsiella pneumoniae

# Antibiotic Classes to Predict

Prototype model will focus on:

-   Carbapenems

-   Cephalosporins

-   Fluoroquinolones

# Data Sources

Primary genomic dataset sources:

1.  NCBI (National Center for Biotechnology Information)

    -   Genome sequences (FASTA)

    -   Pathogen detection database

    -   Antibiotic resistance metadata

2.  CARD (Comprehensive Antibiotic Resistance Database)

    -   Curated resistance genes

    -   Resistance mechanisms

# Data Format

Genome FASTA example:

\>sample_001 ATGCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC

Metadata example columns:

sample_id \| species \| antibiotic \| resistant

# Feature Engineering

Recommended approach for prototype:

K■mer representation.

DNA sequences are broken into short substrings (k■mers) such as k=3 or
k=5.

Example sequence:

ATCGTAG

3■mers:

ATC, TCG, CGT, GTA, TAG

K■mer frequencies become numerical features used for model training.

# Model Candidates

Models to test:

-   Random Forest (robust baseline model)

-   XGBoost (high performance for tabular genomic features)

-   Logistic Regression (baseline comparison)

# Model Evaluation Metrics

Key evaluation metrics:

Accuracy = correct predictions / total predictions

Prototype target:

Accuracy \> 80%

Additional metrics:

-   ROC-AUC (\>0.85 target)

-   Precision

-   Recall (especially important for resistant class)

# Minimum Dataset Size

Initial prototype dataset size: 500 -- 2000 bacterial genomes

Recommended split:

70% Training

15% Validation

15% Testing

# ML Pipeline Workflow

Pipeline structure:

Genome Sequences

↓

Feature Extraction (k■mers)

↓

Feature Matrix

↓

Train Classifier

↓

Evaluate Model

↓

Resistance Prediction

# Example Output

Example prediction output: Sample ID: S105

Carbapenem → Resistant (0.91)

Cephalosporin → Resistant (0.83)

Fluoroquinolone → Sensitive (0.22)

# Deliverable for Prototype

For the early prototype demonstration:

1.  Load genome FASTA

2.  Extract k■mer features

3.  Run trained ML model

4.  Output resistance prediction

# Future Development

Possible later improvements:

-   Deep learning models for genomic sequences

-   Mutation detection

-   Integration with hospital laboratory systems

-   Real■time sequencing data analysis
