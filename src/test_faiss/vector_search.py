import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# === CONFIGURATION ===
EMBEDDINGS_FILE = "src/processed_embeddings2.json"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # Même modèle qu’à l’encodage
TOP_K = 5

# === LOAD EMBEDDING MODEL ===
print("[INFO] Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)

# === LOAD PROCESSED EMBEDDINGS ===
print("[INFO] Loading precomputed embeddings...")
with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

embeddings = []
texts = []
for item in data:
    if "embedding" in item and item["embedding"]:
        embeddings.append(np.array(item["embedding"], dtype="float32"))
        raw_text = item.get("text", "")
        try:
            content = json.loads(raw_text)  # Parse le JSON imbriqué
            title = content.get("title", "No title")
            status = content.get("status", "No status")
            summary = content.get("summary", "")
            # Formatage propre
            display_text = f"Title: {title}\nStatus: {status}\nSummary: {summary[:200]}{'...' if len(summary) > 200 else ''}"
        except json.JSONDecodeError:
            # Si échec parsing, afficher premier extrait brut
            display_text = raw_text[:300] + ("..." if len(raw_text) > 300 else "")
        texts.append(display_text)

if not embeddings:
    raise ValueError("Aucun embedding trouvé dans processed_embeddings.json")

print(f"[INFO] Loaded {len(embeddings)} embeddings.")

# === BUILD FAISS INDEX ===
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.vstack(embeddings).astype("float32"))
print(f"[INFO] FAISS index built with dimension {dimension}")

# === SEARCH FUNCTION ===
def search(query, k=TOP_K):
    query_embedding = model.encode(query).astype("float32")
    distances, indices = index.search(np.array([query_embedding]), k)
    results = []
    for idx, dist in zip(indices[0], distances[0]):
        results.append({
            "text": texts[idx],
            "distance": float(dist)
        })
    return results

# === TEST SEARCH ===
while True:
    user_query = input("\n❓ Enter your question (or 'exit' to quit): ").strip()
    if user_query.lower() == "exit":
        break

    print(f"\n🔎 Top {TOP_K} results for: '{user_query}'\n")
    results = search(user_query)
    for i, res in enumerate(results, 1):
        print(f"[{i}] Distance: {res['distance']:.4f}")
        print(f"{res['text']}\n")
