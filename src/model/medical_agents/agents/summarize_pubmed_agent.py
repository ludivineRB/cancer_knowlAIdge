from Bio import Entrez
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

# Configure l'API NCBI PubMed
Entrez.email = os.getenv("PUBMED_EMAIL") 

# Configure l'API Groq
groq_api_key = os.getenv("GROQ_API")
llm = ChatGroq(model_name="llama3-70b-8192", api_key=groq_api_key, temperature=0.2)


def clean_query(raw_query: str) -> str:
    """
    Nettoie la requête pour ne garder que le sujet scientifique
    """
    remove_words = ["complete summary", "summary", "scientist", "with sources", "about", "knowledge"]
    query = raw_query.lower()
    for word in remove_words:
        query = query.replace(word, "")
    return query.strip()


def search_pubmed(query, max_results=5):
    """
    Recherche PubMed et renvoie une liste d'identifiants d'articles
    """
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]


def fetch_pubmed_abstracts(id_list):
    """
    Récupère les résumés et liens pour une liste d'ID PubMed
    """
    ids = ",".join(id_list)
    handle = Entrez.efetch(db="pubmed", id=ids, rettype="abstract", retmode="text")
    abstracts_text = handle.read()
    handle.close()

    # Crée des liens PubMed
    links = [f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}" for pubmed_id in id_list]
    links_text = "\n".join([f"- 🔗 {link}" for link in links])

    return abstracts_text, links_text


def summarize_pubmed_results(raw_query, language="en"):
    """
    Recherche, résume et traduit les résultats PubMed
    """
    query = clean_query(raw_query)
    ids = search_pubmed(query)

    if not ids:
        # Fallback : Pas de résultats, on demande directement à Groq
        fallback_prompt = f"""
Tu es un assistant scientifique expert. Je n'ai trouvé aucun article PubMed pour : '{query}'.
Peux-tu me donner un résumé scientifique fiable (en {language}) sur ce sujet ?
Donne :
- 📝 Un résumé concis (5 lignes max)
- 📌 Trois points clés
"""
        response = llm.invoke(fallback_prompt)
        return f"⚠️ Aucun article trouvé sur PubMed. Voici un résumé généré :\n\n{response}"

    # Résumés + Liens
    abstracts, links_text = fetch_pubmed_abstracts(ids)

    prompt = f"""
Tu es un assistant scientifique expert. Résume les publications suivantes dans la langue '{language}' :
---
{abstracts}
---
Donne :
- 📝 Un résumé concis (5 lignes max)
- 📌 Trois points clés
- 🔗 Les liens PubMed suivants : 
{links_text}
"""
    response = llm.invoke(prompt)
    return response
