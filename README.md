# BactoAI

**BactoAI** is a machine learning-powered web application for predicting antibiotic resistance from raw bacterial whole-genome sequences (.fna / .fasta).

It utilizes **XGBoost** models trained on k-mer representations of DNA sequences, extracted directly from the NCBI Pathogen Detection Browser database.

Currently predicts resistance for:

- 🔵 **Meropenem** (Carbapenems)
- 🟡 **Ciprofloxacin** (Fluoroquinolones)
- 🔴 **Cefotaxime** (Cephalosporins)

Across multiple Gram-negative species including *Escherichia coli*, *Klebsiella pneumoniae*, and *Acinetobacter baumannii*.

## Running Locally (Backend & Frontend)

Since BactoAI is built using Flask, both the **backend** (the Python machine learning API) and the **frontend** (the HTML/JS user interface located in the `templates` and `static` folders) are served together by a single local server.

### 1. Open Your Terminal

Open your PowerShell or Command Prompt and navigate to your project directory:

```powershell
cd C:\Users\User\Documents\RESEARCH\Bacto_AI
```

### 2. Activate the Virtual Environment

To ensure the application uses the correct dependencies (like Flask, XGBoost, and Biopython), activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

*(Note: If you haven't installed the necessary packages yet, run `pip install -r requirements.txt`)*

### 3. Start the Application Server

Start the Flask application by running the main Python script:

```powershell
python app.py
```

### 4. Access the Frontend in Your Browser

With the server running, open your preferred web browser and navigate to:
**[http://localhost:5000](http://localhost:5000)**
This URL will load the BactoAI web interface. From here, you can upload your `.fna` or `.fasta` files, and the frontend will automatically communicate with the local backend to process the predictions.

### 5. Stopping the Server

When finished, stop the local server by pressing `Ctrl + C` in your terminal. To exit the virtual environment, type:

```powershell
deactivate
```
