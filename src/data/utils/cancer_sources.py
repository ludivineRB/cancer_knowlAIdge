import os
import subprocess
import requests
from huggingface_hub import snapshot_download

# 📁 Créer un dossier de travail
BASE_DIR = "src/data/raw/"
os.makedirs(BASE_DIR, exist_ok=True)

# ✅ 1. Télécharger Radiation Oncology NLP Database (ROND) depuis GitHub
def download_rond():
    print("📥 Téléchargement de ROND...")
    rond_dir = os.path.join(BASE_DIR, "ROND")
    if not os.path.exists(rond_dir):
        subprocess.run([
            "git", "clone",
            "https://github.com/zl-liu/Radiation-Oncology-NLP-Database.git",
            rond_dir
        ])
        print("✅ ROND téléchargé.")
    else:
        print("✔️ ROND déjà téléchargé.")

# ✅ 2. Télécharger PubMed‑Cancer‑NLP‑Textual‑Dataset (Hugging Face)
def download_pubmed_cancer():
    print("📥 Téléchargement de PubMed‑Cancer‑NLP...")
    pubmed_dir = os.path.join(BASE_DIR, "PubMed-Cancer-NLP")
    if not os.path.exists(pubmed_dir):
        snapshot_download(
            repo_id="cyberpsych/PubMed-Cancer-NLP-Textual-Dataset",
            local_dir=pubmed_dir,
            repo_type="dataset"
        )
        print("✅ PubMed‑Cancer‑NLP téléchargé.")
    else:
        print("✔️ PubMed‑Cancer‑NLP déjà téléchargé.")

# ✅ 3. Télécharger SODA – Social Determinants of Health (GitHub)
def download_soda():
    print("📥 Téléchargement de SODA...")
    soda_dir = os.path.join(BASE_DIR, "SODA")
    if not os.path.exists(soda_dir):
        subprocess.run([
            "git", "clone",
            "https://github.com/uf-hobiinformatics-lab/SDoH_SODA.git",
            soda_dir
        ])
        print("✅ SODA téléchargé.")
    else:
        print("✔️ SODA déjà téléchargé.")

# ✅ 4. Télécharger une archive depuis Cancer Imaging Archive (TCIA)
def download_tcia_sample():
    print("📥 Téléchargement d’un exemple depuis TCIA...")
    tcia_dir = os.path.join(BASE_DIR, "TCIA")
    os.makedirs(tcia_dir, exist_ok=True)
    # Exemple : télécharger une archive publique
    tcia_url = "https://wiki.cancerimagingarchive.net/download/attachments/68550653/TCGA-LUAD.zip"
    zip_path = os.path.join(tcia_dir, "TCGA-LUAD.zip")
    if not os.path.exists(zip_path):
        response = requests.get(tcia_url, stream=True)
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("✅ Exemple TCIA téléchargé.")
    else:
        print("✔️ Exemple TCIA déjà téléchargé.")

# 🚀 Exécuter tous les téléchargements
if __name__ == "__main__":
    print("🚀 Téléchargement des datasets de vulgarisation cancer")
    download_rond()
    download_pubmed_cancer()
    download_soda()
    download_tcia_sample()
    print("🎉 Tous les datasets sont prêts dans le dossier :", BASE_DIR)
