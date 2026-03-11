import os
import io
import gzip
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
from xgboost import XGBClassifier
from Bio import SeqIO

app = Flask(__name__)
CORS(app)

DATA_DIR = "data"
MODELS_DIR = os.path.join(DATA_DIR, "models")
TRANSFORMERS_DIR = os.path.join(DATA_DIR, "transformers")
KMER_SIZE = 5

# Antibiotics to load
ANTIBIOTICS = ["meropenem", "ciprofloxacin", "cefotaxime"]

# Global dict to hold loaded models/transformers
loaded_objects = {}

def load_objects():
    for ab in ANTIBIOTICS:
        model_path = os.path.join(MODELS_DIR, f"model_{ab}.json")
        vec_path = os.path.join(TRANSFORMERS_DIR, f"vectorizer_{ab}.joblib")
        sel_path = os.path.join(TRANSFORMERS_DIR, f"selector_{ab}.joblib")
        
        if os.path.exists(model_path) and os.path.exists(vec_path) and os.path.exists(sel_path):
            model = XGBClassifier()
            model.load_model(model_path)
            vec = joblib.load(vec_path)
            sel = joblib.load(sel_path)
            loaded_objects[ab] = {"model": model, "vec": vec, "sel": sel}
            print(f"Loaded components for {ab}")
        else:
            print(f"Missing components for {ab}")

def read_fasta(file_bytes):
    seq = ""
    try:
        # Check if gzip
        if file_bytes[:2] == b'\x1f\x8b':
            fh = io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(file_bytes)))
        else:
            fh = io.StringIO(file_bytes.decode('utf-8'))
            
        for record in SeqIO.parse(fh, "fasta"):
            seq += str(record.seq).upper()
            
    except Exception as e:
        print(f"Error reading fasta: {e}")
    return seq

def build_kmers(seq, k):
    return " ".join(seq[i:i+k] for i in range(len(seq) - k + 1))

@app.before_request
def setup():
    if not loaded_objects:
        load_objects()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    file_bytes = file.read()
    seq = read_fasta(file_bytes)
    if not seq:
        return jsonify({"error": "Could not parse FASTA genome sequence"}), 400

    kmer_str = build_kmers(seq, KMER_SIZE)

    results = []
    
    for ab, objects in loaded_objects.items():
        vec = objects["vec"]
        sel = objects["sel"]
        model = objects["model"]
        
        # Transform
        X = vec.transform([kmer_str])
        X = sel.transform(X)
        
        # Predict
        prob = float(model.predict_proba(X)[0][1])
        label = "Resistant" if prob > 0.5 else "Susceptible"
        
        results.append({
            "antibiotic": ab.capitalize(),
            "probability": prob,
            "label": label
        })

    return jsonify({"results": results, "filename": file.filename})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
