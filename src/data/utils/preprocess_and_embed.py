import os
import json
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# === CONFIGURATION ===
DATA_FOLDER = "./data/raw"  # Dossier où sont tes fichiers .json et .txt
CHUNK_SIZE = 500  # Nb de tokens ou caractères par chunk
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # ou "all-MiniLM-L6-v2"

# === LOAD EMBEDDING MODEL ===
print("[INFO] Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)

# === TEXT CLEANING ===
def clean_text(text):
    """
    Nettoyer un texte brut : enlever le bruit, normaliser espaces, supprimer HTML.
    """
    text = re.sub(r"<[^>]+>", "", text)  # enlever balises HTML
    text = re.sub(r"\s+", " ", text)  # normaliser espaces
    text = text.replace("\xa0", " ").strip()
    return text

# === CHUNKING ===
def split_text(text, chunk_size=500, overlap=50):
    """
    Découpe un texte en chunks avec overlap.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks

# === METADATA EXTRACTION ===
def infer_metadata(file_path, source_hint=None):
    """
    Infère des métadonnées de base depuis le nom du fichier ou un hint.
    """
    base_name = os.path.basename(file_path).lower()
    metadata = {}

    if "pubmed" in base_name or source_hint == "PubMed":
        metadata["source"] = "PubMed"
        metadata["type"] = "scientifique"
    elif "trials" in base_name or source_hint == "Trials":
        metadata["source"] = "Trials"
        metadata["type"] = "essai clinique"
    elif "cancergov" in base_name or source_hint == "CancerGov":
        metadata["source"] = "CancerGov"
        metadata["type"] = "recommandation"
    elif "who" in base_name or source_hint == "WHO":
        metadata["source"] = "WHO"
        metadata["type"] = "statistiques"
    elif "patient" in base_name or source_hint == "Patient":
        metadata["source"] = "CancerNet"
        metadata["type"] = "vulgarisation"
    else:
        metadata["source"] = "Unknown"
        metadata["type"] = "Unknown"

    metadata["date"] = datetime.now().strftime("%Y-%m-%d")
    metadata["url"] = None  # Peut être ajouté plus tard si dispo
    return metadata

# === PROCESSING ===
def process_file(file_path):
    """
    Charge un fichier, nettoie et prépare les chunks avec embeddings.
    """
    print(f"[PROCESSING] {file_path}")

    # Charger le contenu
    if file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        if isinstance(raw_data, list):  # Liste de documents
            texts = [json.dumps(item) for item in raw_data]
        else:
            texts = [json.dumps(raw_data)]
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            texts = [f.read()]
    else:
        print(f"Unsupported file type: {file_path}")
        return []

    # Nettoyer et chunker
    metadata = infer_metadata(file_path)
    results = []

    for text in texts:
        clean = clean_text(text)
        chunks = split_text(clean, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)

        for chunk in chunks:
            embedding = model.encode(chunk).tolist()
            results.append({
                "text": chunk,
                "embedding": embedding,
                "metadata": metadata
            })

    return results

def get_all_files(data_folder, extensions=(".json", ".txt")):
    """
    Parcourt tous les sous-dossiers pour trouver des fichiers avec les extensions données.
    """
    files = []
    for root, dirs, filenames in os.walk(data_folder):
        for filename in filenames:
            if filename.endswith(extensions):
                files.append(os.path.join(root, filename))
    return files

def main():
    all_results = []

    files = get_all_files(DATA_FOLDER)
    print(f"[INFO] Found {len(files)} files to process.")

    for file_path in tqdm(files, desc="Processing files"):
        file_results = process_file(file_path)
        all_results.extend(file_results)

    # Sauvegarder résultats
    output_file = "processed_embeddings.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] Processed data saved to {output_file}")

if __name__ == "__main__":
    main()

