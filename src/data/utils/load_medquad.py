# scripts/load_medquad.py

from datasets import load_dataset

# def download_medquad(dest_jsonl="src/data/raw/QA/medquad_qa.jsonl"):
#     # Charger le dataset Hugging Face
#     ds = load_dataset("Laurent1/MedQuad-MedicalQnADataset_128tokens_max", split="train")

#     count = 0
#     with open(dest_jsonl, "w") as fout:
#         for item in ds:
#             question = item.get("Instruction") or item.get("Question") or item.get("question")
#             answer = item.get("Response") or item.get("Answer") or item.get("answer")
#             if not question or not answer:
#                 continue
#             # Écrire une paire JSON
#             fout.write(json.dumps({"prompt": question.strip(), "response": answer.strip()}, ensure_ascii=False) + "\n")
#             count += 1

#     print(f"✅ {count} paires prompt/response sauvegardées dans {dest_jsonl}")

# if __name__ == "__main__":
#     download_medquad()

# Charge le dataset
ds = load_dataset("Laurent1/MedQuad-MedicalQnADataset_128tokens_max", split="train")

# Affiche 3 exemples
for i in range(3):
    print(ds[i])
