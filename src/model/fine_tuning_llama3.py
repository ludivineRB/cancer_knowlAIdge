from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch

# 🔥 Utilise la version quantifiée de LLaMA 3
BASE_MODEL = "meta-llama/Llama-3-8b-hf"  # ou "Llama-2-7b-hf" si GPU limité
OUTPUT_DIR = "models/llama3-cancer-qa"
DATA_PATH = "raw/data/processed/cancer_qa.jsonl"

def load_data():
    dataset = load_dataset("json", data_files=DATA_PATH)
    return dataset

def fine_tune():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        load_in_8bit=True,  # 🪶 utilise bitsandbytes pour alléger
        device_map="auto"
    )

    # 🧠 Préparer pour LoRA
    model = prepare_model_for_kbit_training(model)
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],  # modules à adapter
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)

    dataset = load_data()
    dataset = dataset["train"].train_test_split(test_size=0.1)

    def format_prompt(example):
        return tokenizer(
            f"<s>[INST] {example['prompt']} [/INST] {example['response']}</s>",
            truncation=True,
            padding="max_length",
            max_length=512
        )

    tokenized_ds = dataset.map(format_prompt, batched=True)

    # ⚙️ Arguments d’entraînement
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        evaluation_strategy="steps",
        save_strategy="steps",
        eval_steps=50,
        save_steps=50,
        logging_steps=10,
        learning_rate=2e-4,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=4,
        warmup_steps=20,
        max_steps=500,  # nombre d’étapes total
        fp16=True,
        save_total_limit=2
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds["train"],
        eval_dataset=tokenized_ds["test"],
        tokenizer=tokenizer,
        data_collator=data_collator
    )

    # 🚀 Lancement du fine-tuning
    trainer.train()
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"✅ Modèle fine-tuné sauvegardé dans {OUTPUT_DIR}")

if __name__ == "__main__":
    fine_tune()
