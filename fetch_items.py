import requests, time
from tqdm import tqdm
from utils import get_token
from db import update_item_names
import os

REGION = os.getenv("BLIZZ_REGION", "eu").strip()
LOCALE = os.getenv("LOCALE", "fr_FR").strip()

def fetch_item_names(item_ids):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    item_names = {}

    for item_id in tqdm(item_ids, desc="Objets"):
        url = f"https://{REGION}.api.blizzard.com/data/wow/item/{item_id}?namespace=static-{REGION}&locale={LOCALE}"
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            item_names[item_id] = data.get("name", f"Item {item_id}")
        else:
            item_names[item_id] = f"Item {item_id}"
        time.sleep(0.05)

    update_item_names(item_names)
    print(f"{len(item_names)} objets mis à jour.")
