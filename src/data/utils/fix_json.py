import json

def fix_jsonl(input_file, output_file):
    fixed_lines = 0
    with open(input_file, "r", encoding="utf-8") as fin, open(output_file, "w", encoding="utf-8") as fout:
        for line in fin:
            try:
                data = json.loads(line)
                prompt = data.get("prompt", "").strip()
                completion = data.get("response", "").strip()

                if not prompt or not completion:
                    continue  # skip incomplete or empty entries

                # Ollama expects a space before completion
                fixed_data = {
                    "prompt": prompt,
                    "completion": " " + completion
                }
                fout.write(json.dumps(fixed_data, ensure_ascii=False) + "\n")
                fixed_lines += 1
            except json.JSONDecodeError:
                continue  # skip malformed lines
    print(f"✅ {fixed_lines} lignes corrigées et enregistrées dans {output_file}")

# Utilisation
fix_jsonl(
    input_file="src/data/processed/cancer_qa.jsonl",
    output_file="src/data/processed/cancer_qa_ollama.jsonl"
)
