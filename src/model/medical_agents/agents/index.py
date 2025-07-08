from langchain_community.vectorstores import FAISS
import json

# Charger les embeddings
data=[]
with open("src/processed_embeddings3.json", "r") as f:
    # data = [json.loads(line) for line in f]
    for line in f:
        line = line.strip()
        if not line:
            continue  # ignorer lignes vides
        try:
            data.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Ligne ignorée car invalide: {line[:100]}... -> {e}")

# On suppose que chaque item a un champ "embedding" et "text"
texts = [item["text"] for item in data]
embeddings = [item["embedding"] for item in data]

# Construire l'index FAISS
faiss_index = FAISS.from_embeddings(
    embeddings=embeddings,
    texts=texts,
    embedding_function=None  # embeddings déjà calculés
)

# Sauvegarder l'index
faiss_index.save_local("agents/generaliste_index")
