import requests, time
from tqdm import tqdm
from utils import get_token, pick
from db import insert_auctions
import os
from datetime import datetime

REALM_ID = 1305
REGION = os.getenv("BLIZZ_REGION", "eu").strip()
LOCALE = os.getenv("LOCALE", "fr_FR").strip()

def fetch_and_store_auctions():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    ah_url = (
        f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/"
        f"{REALM_ID}/auctions?namespace=dynamic-{REGION}&locale={LOCALE}"
    )
    print("Téléchargement des enchères ...")
    r = requests.get(ah_url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    now = datetime.utcnow().isoformat()

    fields = [
        "id", "item.id", "buyout", "unit_price", "quantity",
        "time_left", "bid", "rand", "context", "pet_species_id"
    ]

    rows = []
    for auc in tqdm(data["auctions"], unit="enchère"):
        row = [pick(auc, f) for f in fields]
        row.append(now)  # add timestamp
        rows.append(tuple(row))

    insert_auctions(rows)
    print(f"{len(rows)} enchères enregistrées.")
    return {pick(auc, "item.id") for auc in data["auctions"] if "item" in auc}
