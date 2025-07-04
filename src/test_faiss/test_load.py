import json

with open("src/processed_embeddings.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Type de data: {type(data)}")
print(f"Nombre d'éléments: {len(data)}")
print("Exemple d'entrée:")
print(data[0])
print("Keys de la première entrée:")
print(data[0].keys())
