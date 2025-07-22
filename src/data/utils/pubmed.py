from Bio import Entrez

Entrez.email = "ludivine.raby@gmail.com"  # Obligatoire pour l'API NCBI
# cancer_type = "lung cancer"
# handle = Entrez.esearch(db="pubmed", term=cancer_type, retmax=100)
# record = Entrez.read(handle)
# id_list = record["IdList"]

# # Récupérer les abstracts
# handle = Entrez.efetch(db="pubmed", id=id_list, rettype="abstract", retmode="text")
# abstracts = handle.read()

# with open(f"data/raw/{cancer_type.replace(' ', '_')}.txt", "w") as f:
#     f.write(abstracts)

cancer_liste=['lung cancer', 'breast cancer', 'brain cancer',
                'bone cancer', 'skin cancer', 'colorectal cancer',
                'bladder cancer', 'lymphoma', 'cervical cancer', 'leukemia',
                'melanoma', 'prostate cancer', 'bowel cancer', 'kidney cancer',
                'childhood cancer', 'uterine cancer', 'sarcoma', 'appendix cancer',
                'liver cancer', 'pancreatic cancer', 'myeloma', 'carcinoma',
                'esophageal cancer', 'endometrial cancer', 'retinoblastoma',
                'gastric cancer', 'testicular cancer', 'ovarian cancer', 'metastatic cancer',
                'neuroblastoma',
                ]

for i, _ in enumerate(cancer_liste):
    cancer_type = cancer_liste[i]
    handle = Entrez.esearch(db="pubmed", term=cancer_type, retmax=100)
    record = Entrez.read(handle)
    id_list = record["IdList"]

    # Récupérer les abstracts
    handle = Entrez.efetch(db="pubmed", id=id_list, rettype="abstract", retmode="text")
    abstracts = handle.read()

    with open(f"data/raw/{cancer_type.replace(' ', '_')}.txt", "w") as f:
        f.write(abstracts)




