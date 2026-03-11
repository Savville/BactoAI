If you want to avoid the clunky NCBI web interface entirely, there are much more robust, automated ways to build this pipeline. When building a production-level machine learning tool, relying on manual browser clicks and CSV downloads is prone to errors.

Here are the two best alternative methods to get paired genomic and AMR phenotype data, completely bypassing the NCBI website.

### ---

**Alternative 1: Google BigQuery \+ Google Cloud (The Automated NCBI Route)**

You mentioned earlier that NCBI data is accessible via Google BigQuery. This is the industry-standard way to handle this data for machine learning because you can query the exact labels you need using SQL and download the genomes via Python, all within a single script.

**How it works:**

Instead of fighting the website's search bar, you query NCBI's public database directly in Google Cloud.

1. **The Metadata (SQL):** You write a SQL query to get *exactly* what you want—for example, only *E. coli* isolates that have a definitively "Resistant" or "Susceptible" lab result for Meropenem, along with their Google Cloud Storage (GCS) URLs.  
2. **The Genomes (Python):** You use the gsutil command or the Python google-cloud-storage library to download the .fna files directly from those URLs into your soils/DATA folder.

**The SQL Query you would use in BigQuery:**

SQL

SELECT   
    target\_acc,   
    taxgroup\_name,   
    ast\_phenotype,  
    asm\_acc,  
    refseq\_ftp  
FROM   
    \`ncbi\-pathogen\-detect.pdbrowser.isolates\`   
WHERE   
    taxgroup\_name \= 'Escherichia coli and Shigella'   
    AND ast\_phenotype LIKE '%meropenem=R%' OR ast\_phenotype LIKE '%meropenem=S%'  
LIMIT 1000;

*To do this, you just need a free Google Cloud account. You can run this query in the BigQuery console, export the clean results as a CSV, and then use a Python script to fetch the genome files.*

### ---

**Alternative 2: BV-BRC / PATRIC (The Best Alternative Database)**

If you want to move away from NCBI entirely, the **Bacterial and Viral Bioinformatics Resource Center (BV-BRC)**, formerly known as PATRIC, is arguably better for machine learning projects focused on AMR.

They pre-package their data specifically for researchers looking at AMR phenotypes.

**How to get the data:**

1. **The Metadata (Direct FTP Download):** You can download one master text file containing the AMR lab results for *every* bacteria in their system directly from their FTP server. No searching required.  
   * **Link:** ftp://ftp.bvbrc.org/patric2/current\_release/RELEASE\_NOTES/PATRIC\_genomes\_AMR.txt  
2. **The Genomes (BV-BRC CLI):** BV-BRC has a dedicated Command Line Interface. Once you filter that master text file for your *E. coli* and Meropenem rows, you pass the Genome IDs to their CLI, and it downloads the FASTA files directly.  
   Bash  
   p3-extract-genomes \--file your\_filtered\_ids.txt \--out genomes\_folder/

### **Which should you choose?**

* **Go with BigQuery (Alternative 1\)** if you want to stick with the NCBI Pathogen Detection data but want a clean, programmatic way to filter the metadata and script the downloads. It is highly reliable and teaches great data engineering skills.  
* **Go with BV-BRC (Alternative 2\)** if you want a database that is fundamentally designed around mapping genomes to AMR phenotypes. Their master AMR text file is incredibly easy to load into a pandas DataFrame to sort out your 1s and 0s.

Would you prefer to stick with NCBI but automate it via a BigQuery Python script, or would you like to pivot to the BV-BRC database approach?