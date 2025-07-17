import requests
import os

def Login():
    # 1. Get token
    resp = requests.post(
        f"{os.getenv("API_URL")}/login",
        data={
            "username": os.getenv("API_USER"),
            "password": os.getenv("API_PASSWORD"),    # or wherever you have it
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]

    # 2. Call protected endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    return headers