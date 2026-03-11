# BactoAI

**BactoAI** is a machine learning-powered web application for predicting antibiotic resistance from raw bacterial whole-genome sequences (.fna / .fasta).

It utilizes **XGBoost** models trained on k-mer representations of DNA sequences, extracted directly from the NCBI Pathogen Detection Browser database.

Currently predicts resistance for:
- 🔵 **Meropenem** (Carbapenems)
- 🟡 **Ciprofloxacin** (Fluoroquinolones) 
- 🔴 **Cefotaxime** (Cephalosporins)

Across multiple Gram-negative species including *Escherichia coli*, *Klebsiella pneumoniae*, and *Acinetobacter baumannii*.

## Running Locally

1. Create virtual environment and install dependencies:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the Flask application:
```bash
python app.py
```

3. Open `http://localhost:5000` in your browser and upload a `.fna` or `.fasta` file.
