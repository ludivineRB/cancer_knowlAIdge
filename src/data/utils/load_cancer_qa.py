# src/data/utils/load_cancer_qa.py

import pandas as pd
import json

def convert_csv_to_jsonl(
    csv_path="src/data/raw/QA/CancerQA.csv",
    jsonl_path="src/data/processed/cancer_qa.jsonl"
):
    df = pd.read_csv(csv_path)
    count = 0
    with open(jsonl_path, "w") as fout:
        for _, row in df.iterrows():
            q = str(row.get("question") or row.get("Question") or row.get("Q", "")).strip()
            a = str(row.get("answer") or row.get("Answer") or row.get("A", "")).strip()
            if not q or not a:
                continue
            fout.write(json.dumps({"prompt": q, "response": a}, ensure_ascii=False) + "\n")
            count += 1
    print(f"✅ {count} paires prompt/response créées dans {jsonl_path}")

if __name__ == "__main__":
    convert_csv_to_jsonl()
