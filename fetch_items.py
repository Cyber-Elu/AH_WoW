import requests
import time
import os
import tqdm
from utils import get_token

REGION = os.getenv("BLIZZ_REGION", "eu").strip()
LOCALE = os.getenv("LOCALE", "fr_FR").strip()
NAMESPACE = f"static-{REGION}"

def get_all_item_ids():
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Charset": "utf-8"
    }

    url = f"https://{REGION}.api.blizzard.com/data/wow/item/index"
    params = {"namespace": NAMESPACE, "locale": LOCALE}
    
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    items_data = response.json()
    item_refs = items_data.get("items", [])

    item_ids = [item["id"] for item in item_refs if "id" in item]

    return item_ids


def fetch_item_names(item_ids, token, region="eu", locale="fr_FR", delay=0.05):
    headers = {"Authorization": f"Bearer {token}"}
    item_names = []

    for item_id in tqdm(item_ids, desc="Objets"):
        if item_id is None:
            continue

        item_url = f"https://{region}.api.blizzard.com/data/wow/item/{item_id}?namespace=static-{region}&locale={locale}"

        try:
            response = requests.get(item_url, headers=headers, timeout=10)
            if response.status_code == 404:
                print(f"Objet {item_id} introuvable.")
                continue
            response.raise_for_status()
            data = response.json()

            name_data = data.get("name")
            if isinstance(name_data, dict):
                name = name_data.get(locale, "")
            else:
                name = name_data or ""

            if name:
                item_names.append((item_id, name))

        except requests.RequestException as e:
            print(f"Erreur pour l'objet {item_id} : {e}")
            continue

        time.sleep(delay)

    return item_names

if __name__ == "__main__":
    try:
        ids = get_all_item_ids()
        print(f"Nombre total d'IDs d'objets récupérés : {len(ids)}")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
