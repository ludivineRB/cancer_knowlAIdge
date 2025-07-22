# from Bio import Entrez
# from langchain_groq import ChatGroq
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Configure l'API NCBI PubMed
# Entrez.email = os.getenv("PUBMED_EMAIL")

# # Configure l'API Groq
# groq_api_key = os.getenv("GROQ_API")
# llm = ChatGroq(model_name="llama3-70b-8192", api_key=groq_api_key, temperature=0.2)


# def clean_query(raw_query: str) -> str:
#     """
#     Nettoie la requête pour ne garder que le sujet scientifique
#     """
#     remove_words = ["complete summary", "summary", "scientist", "with sources", "about", "knowledge"]
#     query = raw_query.lower()
#     for word in remove_words:
#         query = query.replace(word, "")
#     return query.strip()


# def search_pubmed(query, max_results=5):
#     """
#     Recherche PubMed et renvoie une liste d'identifiants d'articles
#     """
#     handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
#     record = Entrez.read(handle)
#     handle.close()
#     return record["IdList"]


# def fetch_pubmed_abstracts(id_list):
#     """
#     Récupère les résumés et liens pour une liste d'ID PubMed
#     """
#     ids = ",".join(id_list)
#     handle = Entrez.efetch(db="pubmed", id=ids, rettype="abstract", retmode="text")
#     abstracts_text = handle.read()
#     handle.close()

#     # Crée des liens PubMed
#     links = [f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}" for pubmed_id in id_list]
#     links_text = "\n".join([f"- 🔗 {link}" for link in links])

#     return abstracts_text, links_text


# def summarize_pubmed_results(raw_query, language="en"):
#     """
#     Recherche, résume et traduit les résultats PubMed
#     """
#     query = clean_query(raw_query)
#     ids = search_pubmed(query)

#     if not ids:
#         # Fallback : Pas de résultats, on demande directement à Groq
#         fallback_prompt = f"""
# Tu es un assistant scientifique expert. Je n'ai trouvé aucun article PubMed pour : '{query}'.
# Peux-tu me donner un résumé scientifique fiable (en {language}) sur ce sujet ?
# Donne :
# - 📝 Un résumé concis (5 lignes max)
# - 📌 Trois points clés
# """
#         response = llm.invoke(fallback_prompt)
#         return f"⚠️ Aucun article trouvé sur PubMed. Voici un résumé généré :\n\n{response}"

#     # Résumés + Liens
#     abstracts, links_text = fetch_pubmed_abstracts(ids)

#     prompt = f"""
# Tu es un assistant scientifique expert. Résume les publications suivantes dans la langue '{language}' :
# ---
# {abstracts}
# ---
# Donne :
# - 📝 Un résumé concis (5 lignes max)
# - 📌 Trois points clés
# - 🔗 Les liens PubMed suivants:
# {links_text}
# """
#     response = llm.invoke(prompt)
#     return response

from Bio import Entrez
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Configure l'API NCBI PubMed
Entrez.email = os.getenv("PUBMED_EMAIL")

# Configure l'API Groq
groq_api_key = os.getenv("GROQ_API")
llm = ChatGroq(model_name="llama3-70b-8192", api_key=groq_api_key, temperature=0.2)


def clean_query(raw_query: str) -> str:
    """
    Clean the user query to keep only the scientific subject.
    Removes polite/formal words but keeps the main scientific topic intact.
    """
    # Convert to lowercase
    query = raw_query.lower()

    # Remove polite or filler phrases
    remove_patterns = [
        r"\b(can you|could you|please|would you|i want|i need|give me|provide|tell me|explain|what is|may i|puis je|peux tu|pourrais tu)\b",
        r"\b(a|an|the|about|on|of|with sources|scientific|summary|résumé scientifique|un résumé scientifique|scientist)\b"
    ]
    for pattern in remove_patterns:
        query = re.sub(pattern, "", query, flags=re.IGNORECASE)

    # Remove non-alphanumeric characters except spaces
    query = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s\-]", "", query)

    # Collapse multiple spaces and trim
    query = re.sub(r"\s+", " ", query).strip()

    print(f"🔎 Cleaned PubMed Query: {query}")
    return query


def search_pubmed(query, max_results=5):
    """
    Recherche PubMed et renvoie une liste d'identifiants d'articles
    """
    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        print(f"🔗 PubMed found IDs: {record['IdList']}")
        return record["IdList"]
    except Exception as e:
        print(f"⚠️ PubMed search failed: {e}")
        return []


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
        # Fallback: No PubMed results found, ask LLM directly
        fallback_prompt = f"""
You are a scientific assistant specialized in biomedical literature.
No PubMed articles were found for the topic: '{query}'.

Please generate a reliable scientific summary in {language}, including:
- 📝 A detailed summary (about 10 lines)
- 📌 Three key takeaways
- 🔗 A note explaining that no PubMed sources were available for this topic
"""
        response = llm.invoke(fallback_prompt)
        return f"⚠️ No articles found on PubMed. Here is a generated summary:\n\n{response}"

    # Summarize PubMed abstracts and include links
    abstracts, links_text = fetch_pubmed_abstracts(ids)

    prompt = f"""
You are a scientific assistant specialized in biomedical literature.
Summarize the following PubMed abstracts in {language}:
---
{abstracts}
---
Provide:
- 📝 A detailed summary (around 10 lines to fully explain key insights)
- 📌 Three key takeaways
- 🔗 A list of PubMed sources (links provided below)

At the end of your response, clearly state: "These insights are derived from scientific publications on PubMed."

PubMed links:
{links_text}
"""
    response = llm.invoke(prompt)
    return response.content
