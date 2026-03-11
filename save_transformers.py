import os
import joblib
import pandas as pd
from bactoai_pipeline_v2 import extract_features, ANTIBIOTIC_FILES, DATA_DIR

TRANSFORMERS_DIR = os.path.join(DATA_DIR, "transformers")
os.makedirs(TRANSFORMERS_DIR, exist_ok=True)

def save_all_transformers():
    for ab, meta_file in ANTIBIOTIC_FILES.items():
        if not os.path.exists(meta_file):
            print(f"Skipping {ab}, metadata missing.")
            continue
            
        vec_path = os.path.join(TRANSFORMERS_DIR, f"vectorizer_{ab}.joblib")
        sel_path = os.path.join(TRANSFORMERS_DIR, f"selector_{ab}.joblib")
        
        if os.path.exists(vec_path) and os.path.exists(sel_path):
            print(f"Skipping {ab}, transformers already exist.")
            continue
            
        print(f"\nRebuilding transformers for {ab}...")
        df = pd.read_csv(meta_file)
        X, y, sp_arr, vec, sel = extract_features(df, training=True)
        
        joblib.dump(vec, vec_path)
        joblib.dump(sel, sel_path)
        print(f"Saved {vec_path} and {sel_path}")

if __name__ == "__main__":
    save_all_transformers()
