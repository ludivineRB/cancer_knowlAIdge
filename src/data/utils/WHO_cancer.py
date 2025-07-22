from bs4 import BeautifulSoup
import requests
import json

def scrape_who_fact_sheets():
    url = "https://www.who.int/news-room/fact-sheets/detail/cancer"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    paragraphs = [p.text for p in soup.find_all("p")]
    with open("data/raw/who_cancer/who_cancer.json", "w", encoding="utf-8") as f:
            json.dump(paragraphs, f, ensure_ascii=False, indent=2)
    return paragraphs

who_data = scrape_who_fact_sheets()
for p in who_data[:5]:
    print(p[:300], "\n---\n")
