import urllib.request
url = 'https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/GCA_012802165.1/download?include_annotation_type=GENOME_FASTA'
try:
    urllib.request.urlretrieve(url, 'test.zip')
    print("Download successful")
except Exception as e:
    print("Error:", e)
