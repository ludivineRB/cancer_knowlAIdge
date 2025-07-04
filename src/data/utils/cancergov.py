import requests
from bs4 import BeautifulSoup
import json
import os

BASE_URL = "https://www.cancer.gov"

def scrape_cancer_gov_articles():
    url = f"{BASE_URL}/about-cancer/treatment/types"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    articles = []

    # Créer dossier si nécessaire
    os.makedirs("data/raw/cancergov", exist_ok=True)

    cards = soup.find_all("li", class_="nci-card")
    for card in cards:
        link = card.find("a")
        if not link:
            continue

        href = link.get("href")
        article_url = BASE_URL + href if href.startswith("/") else href

        article_resp = requests.get(article_url, headers=headers)
        if article_resp.status_code != 200:
            print(f"⚠️ Could not fetch {article_url}")
            continue

        article_soup = BeautifulSoup(article_resp.content, "html.parser")

        title = article_soup.find("h1").get_text(strip=True)

        # Récupérer tout le texte dans la div id="cgvBody"
        content_div = article_soup.find("div", id="cgvBody")
        full_text = content_div.get_text(separator="\n", strip=True) if content_div else "No content found"

        article_data = {
            "title": title,
            "url": article_url,
            "content": full_text
        }
        articles.append(article_data)
        print(f"✅ {title}")

        # Sauvegarder dans un fichier JSON
        filename = f"data/raw/cancergov/{title.replace('/', '-')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)

    return articles

# Test
cancer_articles = scrape_cancer_gov_articles()
print(f"\n📄 {len(cancer_articles)} articles found")

