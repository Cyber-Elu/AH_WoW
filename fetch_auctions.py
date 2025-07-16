import requests
from tqdm import tqdm
from utils import get_token
from db import init_db, insert_auctions, insert_items
import os
import time
from datetime import datetime

REALM_ID = 1305
REGION = os.getenv("BLIZZ_REGION", "eu").strip()
LOCALE = os.getenv("LOCALE", "fr_FR").strip()
NAMESPACE_DYNAMIC = f"dynamic-{REGION}"
NAMESPACE_STATIC = f"static-{REGION}"

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

def fetch_and_store_auctions():
    init_db()

    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params_dynamic = {"namespace": NAMESPACE_DYNAMIC, "locale": LOCALE}

    ah_url = f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/{REALM_ID}/auctions"

    print("Téléchargement des enchères...")
    response = requests.get(ah_url, headers=headers, params=params_dynamic, timeout=30)
    response.raise_for_status()

    data = response.json()
    now = datetime.utcnow().isoformat()

    rows = []
    item_ids = set()

    for auc in tqdm(data["auctions"], unit="enchère"):
        item_id = auc.get("item", {}).get("id")
        item_ids.add(item_id)

        row = (
            auc.get("id"), item_id,
            auc.get("buyout"), auc.get("unit_price"), auc.get("quantity"),
            auc.get("time_left"), auc.get("bid"), auc.get("rand"),
            auc.get("context"), auc.get("pet_species_id"),
            str(auc.get("bonus_lists", [])), str(auc.get("modifiers", [])),
            auc.get("pet_breed_id"), auc.get("pet_level"),
            auc.get("item_context"), auc.get("owner"), auc.get("owner_realm"),
            now
        )
        rows.append(row)

    insert_auctions(rows)
    print(f"{len(rows)} enchères enregistrées.")

    print("Téléchargement des noms d'objets...")
    item_names = fetch_item_names(item_ids, token, region=REGION, locale=LOCALE)
    insert_items(item_names)
    print(f"{len(item_names)} noms d'objets enregistrés.")

if __name__ == "__main__":
    fetch_and_store_auctions()
