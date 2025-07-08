import requests
import json
import os
import time

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


def fetch_clinical_trials_v2(query, page_size=10, page_token=None):
    params = {
        "query.cond": query,
        "pageSize": page_size,
    }
    if page_token:
        params["pageToken"] = page_token

    url = "https://clinicaltrials.gov/api/v2/studies"
    print(f"Calling API: {url} with params {params}")
    r = requests.get(url, params=params)
    if r.status_code != 200:
        raise Exception(f"API error {r.status_code}: {r.text}")
    return r.json()

def parse_trials(data):
    trials = []
    for study in data.get("studies", []):
        sec = study.get("protocolSection", {})
        trials.append({
            "nctId": sec.get("identificationModule", {}).get("nctId"),
            "title": sec.get("identificationModule", {}).get("officialTitle", ""),
            "status": sec.get("statusModule", {}).get("overallStatus", ""),
            "summary": sec.get("descriptionModule", {}).get("briefSummary", ""),
        })
    return trials

def fetch_all_trials_for_cancer(cancer_type, max_trials=50, page_size=10):
    print(f"\nFetching trials for: {cancer_type}")
    all_trials = []
    seen_tokens = set()
    page_token = None

    while len(all_trials) < max_trials:
        try:
            data = fetch_clinical_trials_v2(cancer_type, page_size=page_size, page_token=page_token)
        except Exception as e:
            print(f"❌ Error fetching {cancer_type}: {e}")
            break

        trials = parse_trials(data)
        all_trials.extend(trials)

        # Stop if nextPageToken loops
        page_token = data.get("nextPageToken")
        if not page_token or page_token in seen_tokens:
            break
        seen_tokens.add(page_token)

        time.sleep(1)

    # Trim to max_trials
    all_trials = all_trials[:max_trials]

    out_path = f"data/raw/clinicaltrial/{cancer_type.replace(' ', '_')}.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_trials, f, ensure_ascii=False, indent=2)
    print(f"✅ {len(all_trials)} results saved to {out_path}")


for cancer in cancer_liste:
    fetch_all_trials_for_cancer(cancer, max_trials=50)
