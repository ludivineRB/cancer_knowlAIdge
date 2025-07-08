# # 
# import os
# import json
# import re
# import glob
# import threading
# from datetime import datetime
# from concurrent.futures import ThreadPoolExecutor, as_completed

# import pandas as pd
# import pydicom
# from sentence_transformers import SentenceTransformer
# from tqdm import tqdm

# # === CONFIGURATION ===
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# DATA_FOLDER = os.path.join(BASE_DIR, "data", "raw")
# CHUNK_SIZE = 500
# CHUNK_OVERLAP = 50
# EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
# OUTPUT_FILE = os.path.join(BASE_DIR, "processed_embeddings3.json")
# MAX_THREADS = 4  # Ajuste selon ton CPU

# # === LOAD EMBEDDING MODEL ===
# print("[INFO] Loading embedding model...")
# import torch
# if torch.cuda.is_available():
#     device = "cuda"
# else:
#     device = "cpu"
#     print("[WARN] CUDA not available, using CPU.")
# model = SentenceTransformer(EMBEDDING_MODEL, device=device)
# model_lock = threading.Lock()

# # === TEXT CLEANING ===
# def clean_text(text):
#     text = re.sub(r"<[^>]+>", "", text)
#     text = re.sub(r"\s+", " ", text)
#     return text.strip()

# # === CHUNKING ===
# def split_text(text, chunk_size=500, overlap=50):
#     chunks = []
#     start = 0
#     while start < len(text):
#         end = start + chunk_size
#         chunks.append(text[start:end].strip())
#         start += chunk_size - overlap
#     return chunks

# # === METADATA INFERENCE ===
# def infer_metadata(file_path):
#     name = os.path.basename(file_path).lower()
#     parent_folder = os.path.basename(os.path.dirname(file_path)).lower()

#     folder_mapping = {
#         "PubMed": ("PubMed", "scientifique"),
#         "pubmed": ("pubmed", "scientifique"),
#         "rond": ("ROND", "radiothérapie"),
#         "soda": ("SODA", "social health"),
#         "tcia": ("TCIA", "imagerie"),
#         "cancergov": ("cancergov", "recommandation"),
#         "who": ("who_cancer", "statistiques"),
#         "clinialtial": ("clinicaltrial", "essais cliniques"),
#         "patient": ("CancerNet", "vulgarisation"),
#         "pubmed-NLP": ("PubMed-Cancer-NLP", "tests NLP cancer")
#     }

#     meta = folder_mapping.get(parent_folder)

#     if meta:
#         source, type_ = meta
#     else:
#         if "pubmed" in name:
#             source, type_ = "PubMed", "scientifique"
#         elif "rond" in name:
#             source, type_ = "ROND", "radiothérapie"
#         elif "soda" in name:
#             source, type_ = "SODA", "social health"
#         elif "tcia" in name:
#             source, type_ = "TCIA", "imagerie"
#         elif "trials" in name:
#             source, type_ = "clinicaltrial", "essai clinique"
#         elif "cancergov" in name:
#             source, type_ = "cancergov", "recommandation"
#         elif "who" in name:
#             source, type_ = "who_cancer", "statistiques"
#         elif "patient" in name:
#             source, type_ = "CancerNet", "vulgarisation"
#         else:
#             source, type_ = "Unknown", "Unknown"

#     return {
#         "source": source,
#         "type": type_,
#         "date": datetime.now().strftime("%Y-%m-%d")
#     }

# # === PARSE METADATA ===
# def parse_metadata_from_content(data, fallback_meta):
#     meta = fallback_meta.copy()
#     if isinstance(data, dict):
#         meta["source"] = data.get("source", meta["source"])
#         meta["type"] = data.get("type", meta["type"])
#         meta["date"] = data.get("date", meta["date"])
#         meta["title"] = data.get("title", None)
#     elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
#         first_item = data[0]
#         meta["source"] = first_item.get("source", meta["source"])
#         meta["type"] = first_item.get("type", meta["type"])
#         meta["date"] = first_item.get("date", meta["date"])
#         meta["title"] = first_item.get("title", None)
#     return meta

# # === FILE PROCESSING ===
# def process_file(file_path):
#     try:
#         print(f"[PROCESSING] {file_path}")
#         fallback_meta = infer_metadata(file_path)
#         results = []

#         if file_path.endswith(".json"):
#             with open(file_path, "r", encoding="utf-8") as f:
#                 data = json.load(f)
#             meta = parse_metadata_from_content(data, fallback_meta)
#             texts = [json.dumps(item) if isinstance(item, dict) else str(item) for item in (data if isinstance(data, list) else [data])]

#         elif file_path.endswith(".jsonl"):
#             texts = []
#             with open(file_path, "r", encoding="utf-8") as f:
#                 for line in f:
#                     line_data = json.loads(line)
#                     meta = parse_metadata_from_content(line_data, fallback_meta)
#                     text = line_data.get("context", line.strip())
#                     texts.append(text)

#         elif file_path.endswith(".tsv"):
#             df = pd.read_csv(file_path, sep="\t")
#             meta = fallback_meta
#             if "text" in df.columns:
#                 texts = df['text'].dropna().astype(str).tolist()
#             else:
#                 print(f"[WARN] No 'text' column in {file_path}")
#                 return []

#         elif file_path.endswith(".txt"):
#             meta = fallback_meta
#             with open(file_path, "r", encoding="utf-8") as f:
#                 texts = [f.read()]

#         elif file_path.endswith(".dcm"):
#             ds = pydicom.dcmread(file_path)
#             dicom_text = str(ds)
#             meta = fallback_meta
#             texts = [dicom_text]

#         else:
#             print(f"⚠️ Unsupported file type: {file_path}")
#             return []

#         for text in texts:
#             clean = clean_text(text)
#             chunks = split_text(clean, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
#             with model_lock:
#                 for chunk in chunks:
#                     try:
#                         embedding = model.encode(chunk, normalize_embeddings=True)
#                         embedding_list = [float(x) for x in embedding]  # <-- 🔥 force conversion
#                         results.append({
#                             "text": chunk,
#                             "embedding": embedding_list,
#                             "metadata": meta
#                         })
#                     except Exception as embed_err:
#                         print(f"[WARN] Failed to embed chunk: {embed_err}")

#         return results

#     except Exception as e:
#         print(f"[ERROR] Failed to process {file_path}: {e}")
#         return []

# # === MAIN FUNCTION ===
# def main():
#     print(f"[INFO] Searching files in: {DATA_FOLDER}")
#     files = glob.glob(os.path.join(DATA_FOLDER, "**", "*.*"), recursive=True)
#     files = [f for f in files if f.endswith((".json", ".jsonl", ".tsv", ".txt", ".dcm"))]
#     print(f"[INFO] Found {len(files)} files.")

#     all_results = []
#     with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
#         futures = [executor.submit(process_file, file_path) for file_path in files]
#         for future in tqdm(as_completed(futures), total=len(futures), desc="Processing files"):
#             all_results.extend(future.result())

#     # Sauvegarde
#     with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#         json.dump(all_results, f, ensure_ascii=False, indent=2)
#     print(f"[SUCCESS] Data saved to {OUTPUT_FILE}")

# if __name__ == "__main__":
#     main()


import os
import json
import re
import glob
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import pydicom
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# === CONFIGURATION ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FOLDER = os.path.join(BASE_DIR, "data", "raw")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
OUTPUT_FILE = os.path.join(BASE_DIR, "processed_embeddings3.json")
MAX_THREADS = 4  # Ajuste selon ton CPU

# === LOAD EMBEDDING MODEL ===
print("[INFO] Loading embedding model...")
import torch
if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
    print("[WARN] CUDA not available, using CPU.")
model = SentenceTransformer(EMBEDDING_MODEL, device=device)
model_lock = threading.Lock()

# === TEXT CLEANING ===
def clean_text(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# === CHUNKING ===
def split_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return chunks

# === METADATA INFERENCE ===
def infer_metadata(file_path):
    name = os.path.basename(file_path).lower()
    parent_folder = os.path.basename(os.path.dirname(file_path)).lower()

    folder_mapping = {
        "pubmed": ("PubMed", "scientifique"),
        "rond": ("ROND", "radiothérapie"),
        "soda": ("SODA", "social health"),
        "tcia": ("TCIA", "imagerie"),
        "cancergov": ("cancergov", "recommandation"),
        "who": ("who_cancer", "statistiques"),
        "clinicaltrial": ("clinicaltrial", "essais cliniques"),
        "patient": ("CancerNet", "vulgarisation"),
        "pubmed-nlp": ("PubMed-Cancer-NLP", "tests NLP cancer")
    }

    # Cherche clé dans folder_mapping
    meta = None
    for key in folder_mapping:
        if key == parent_folder:
            meta = folder_mapping[key]
            break

    if meta:
        source, type_ = meta
    else:
        # fallback sur nom fichier
        if "pubmed" in name:
            source, type_ = "PubMed", "scientifique"
        elif "rond" in name:
            source, type_ = "ROND", "radiothérapie"
        elif "soda" in name:
            source, type_ = "SODA", "social health"
        elif "tcia" in name:
            source, type_ = "TCIA", "imagerie"
        elif "trials" in name:
            source, type_ = "clinicaltrial", "essai clinique"
        elif "cancergov" in name:
            source, type_ = "cancergov", "recommandation"
        elif "who" in name:
            source, type_ = "who_cancer", "statistiques"
        elif "patient" in name:
            source, type_ = "CancerNet", "vulgarisation"
        else:
            source, type_ = "Unknown", "Unknown"

    return {
        "source": source,
        "type": type_,
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# === ASSURE QUE LES METADATA SONT COMPLETES ===
def ensure_complete_metadata(meta, fallback_meta):
    for key in ["source", "type", "date"]:
        if not meta.get(key):
            meta[key] = fallback_meta.get(key)
    return meta

# === PARSE METADATA FROM CONTENT ===
def parse_metadata_from_content(data, fallback_meta):
    meta = fallback_meta.copy()
    if isinstance(data, dict):
        meta["source"] = data.get("source", meta["source"])
        meta["type"] = data.get("type", meta["type"])
        meta["date"] = data.get("date", meta["date"])
        meta["title"] = data.get("title", None)
    elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
        first_item = data[0]
        meta["source"] = first_item.get("source", meta["source"])
        meta["type"] = first_item.get("type", meta["type"])
        meta["date"] = first_item.get("date", meta["date"])
        meta["title"] = first_item.get("title", None)
    meta = ensure_complete_metadata(meta, fallback_meta)
    return meta

# === PROCESS FILE ===
def process_file(file_path):
    try:
        print(f"[PROCESSING] {file_path}")
        fallback_meta = infer_metadata(file_path)
        results = []

        if file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            meta = parse_metadata_from_content(data, fallback_meta)
            texts = [json.dumps(item) if isinstance(item, dict) else str(item) for item in (data if isinstance(data, list) else [data])]
            texts = [(text, meta) for text in texts]

        elif file_path.endswith(".jsonl"):
            texts = []
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line_data = json.loads(line)
                    meta = parse_metadata_from_content(line_data, fallback_meta)
                    text = line_data.get("context", line.strip())
                    texts.append((text, meta))

        elif file_path.endswith(".tsv"):
            df = pd.read_csv(file_path, sep="\t")
            meta = fallback_meta
            if "text" in df.columns:
                texts = df['text'].dropna().astype(str).tolist()
                texts = [(text, meta) for text in texts]
            else:
                print(f"[WARN] No 'text' column in {file_path}")
                return []

        elif file_path.endswith(".txt"):
            meta = fallback_meta
            with open(file_path, "r", encoding="utf-8") as f:
                texts = [(f.read(), meta)]

        elif file_path.endswith(".dcm"):
            ds = pydicom.dcmread(file_path)
            dicom_text = str(ds)
            meta = fallback_meta
            texts = [(dicom_text, meta)]

        else:
            print(f"⚠️ Unsupported file type: {file_path}")
            return []

        for text, text_meta in texts:
            clean = clean_text(text)
            chunks = split_text(clean, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
            with model_lock:
                for chunk in chunks:
                    try:
                        embedding = model.encode(chunk, normalize_embeddings=True)
                        embedding_list = [float(x) for x in embedding]
                        results.append({
                            "text": chunk,
                            "embedding": embedding_list,
                            "metadata": text_meta
                        })
                    except Exception as embed_err:
                        print(f"[WARN] Failed to embed chunk: {embed_err}")

        return results

    except Exception as e:
        print(f"[ERROR] Failed to process {file_path}: {e}")
        return []

# === MAIN ===
def main():
    print(f"[INFO] Searching files in: {DATA_FOLDER}")
    files = glob.glob(os.path.join(DATA_FOLDER, "**", "*.*"), recursive=True)
    files = [f for f in files if f.endswith((".json", ".jsonl", ".tsv", ".txt", ".dcm"))]
    print(f"[INFO] Found {len(files)} files.")

    all_results = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(process_file, file_path) for file_path in files]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing files"):
            all_results.extend(future.result())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
