import requests
import time
import json
import os
from tqdm import tqdm
from utils import get_token
from db import update_item_names

REGION = os.getenv("BLIZZ_REGION", "eu").strip()
LOCALE = os.getenv("LOCALE", "fr_FR").strip()
CACHE_FILE = "item_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def fetch_item_names(item_ids):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    item_names = load_cache()

    for item_id in tqdm(item_ids, desc="Objets"):
        if str(item_id) in item_names:
            continue  # Skip if item is already in cache

        url = f"https://{REGION}.api.blizzard.com/data/wow/item/{item_id}?namespace=static-{REGION}&locale={LOCALE}"
        resp = requests.get(url, headers=headers, timeout=15)

        if resp.status_code == 200:
            data = resp.json()
            item_names[str(item_id)] = data.get("name", f"Item {item_id}")
        else:
            item_names[str(item_id)] = f"Item {item_id}"

        time.sleep(0.05)

    save_cache(item_names)
    update_item_names(item_names)
    print(f"{len(item_names)} objets mis à jour.")

