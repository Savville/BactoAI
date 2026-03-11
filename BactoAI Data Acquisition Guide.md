Here is a complete, documented Markdown guide detailing your immediate next steps and exactly how to acquire the correct data for the BactoAI pipeline.

You can save the text below directly as a .md file (e.g., BactoAI\_Data\_Guide.md) in your project folder.

# ---

**BactoAI: Data Acquisition & Project Setup Guide**

## **🎯 1\. The Goal: What You Need**

To build a supervised machine learning model that predicts antibiotic resistance, your dataset must contain two paired components:

1. **The Input (Features):** The raw bacterial DNA sequences (.fasta or .fna files).  
2. **The Output (Labels):** The ground-truth lab test results showing whether that specific bacteria was Resistant (1) or Susceptible (0) to a specific antibiotic. This is called the **AST (Antimicrobial Susceptibility Test) phenotype**.

*Note: The CSV you downloaded earlier contains the genotypes (the genes inside the bacteria) but is missing the AST phenotypes (the actual lab results). We need to pull a new metadata file that includes these labels.*

## **📥 2\. How to Get the Correct Metadata (CSV)**

We will use the NCBI Pathogen Detection Isolates Browser to get a list of *E. coli* samples that have known lab results for Carbapenems.

**Step-by-Step Instructions:**

1. Navigate to the [NCBI Pathogen Isolates Browser](https://www.ncbi.nlm.nih.gov/pathogens/isolates/).  
2. In the search bar, enter the following query to filter for *E. coli* that have AST data for your target antibiotic class:  
   Plaintext  
   taxgroup\_name:"Escherichia coli and Shigella" AND ast\_phenotype:\*"meropenem"\* \`\`\`  
   \*(Note: Meropenem is a common Carbapenem. You can swap this with "ceftriaxone" for Cephalosporins or "ciprofloxacin" for Fluoroquinolones).\*

3. Click **Search**.  
4. Once the table loads, ensure the column **AST phenotypes** is visible. You should see values like meropenem=R (Resistant) or meropenem=S (Susceptible).  
5. Click the **Download** button to export this table as a CSV file. Name it Ecoli\_Carbapenem\_Metadata.csv.

## **🧬 3\. How to Get the Genomic Data (FASTA files)**

Now that you have the metadata, you need to download the actual DNA sequences for the isolates in your CSV. The best way to do this in bulk is using the **NCBI Datasets Command Line Tool**.

**Step-by-Step Instructions:**

1. **Install NCBI Datasets CLI:**  
   Follow the instructions on the [NCBI Datasets page](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/download-and-install/) to install the tool for your operating system.  
2. **Extract Accession IDs:**  
   Open your Ecoli\_Carbapenem\_Metadata.csv. Copy the entire column named **Assembly** (these IDs look like GCA\_0128...). Paste them into a plain text file named assembly\_ids.txt, with one ID per line.  
3. **Run the Download Command:**  
   Open your terminal or command prompt, navigate to where you saved assembly\_ids.txt, and run:  
   Bash  
   datasets download genome accession \--inputfile assembly\_ids.txt \--include genome

   This will download a .zip file containing all the .fasta / .fna sequence files for your bacteria.  
4. Unzip the downloaded file.

## **📁 4\. Structuring Your Project Directory**

To keep your ML pipeline organized, arrange your project folder exactly like this:

Plaintext

BactoAI\_Project/  
│  
├── data/  
│   ├── metadata/  
│   │   └── Ecoli\_Carbapenem\_Metadata.csv  \# Your labels (R/S)  
│   │  
│   └── genomes/  
│       ├── GCA\_012812345.1.fna            \# Unzipped FASTA files  
│       ├── GCA\_012812346.1.fna  
│       └── ...  
│  
├── notebooks/  
│   └── 01\_data\_exploration.ipynb          \# Jupyter notebook for loading data  
│  
└── scripts/  
    └── kmer\_extraction.py                 \# Script to convert FASTA to k-mers

*(If you are building this within the soils/DATA directory structure you mentioned previously, simply map these subfolders inside your existing workspace.)*

## **🚀 5\. Next Immediate Steps**

Once you have the directory set up and populated with the CSV and FASTA files, you are ready to begin **Phase 2: Feature Extraction**.

You will need a script that reads each .fna file, breaks the DNA sequence into $k$-mers, counts their frequencies, and maps them to the R or S label found in the CSV.

---

Would you like me to draft the Python script (kmer\_extraction.py) that will read your newly downloaded FASTA files and convert them into the mathematical feature matrix required for your XGBoost model?