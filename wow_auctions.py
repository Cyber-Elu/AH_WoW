from pathlib import Path
import csv, os, requests, time
from dotenv import load_dotenv
from tqdm import tqdm
import pandas as pd
import sqlite3

load_dotenv()

CID     = os.getenv("BLIZZ_CLIENT_ID")
SECRET  = os.getenv("BLIZZ_CLIENT_SECRET")
REGION = os.getenv("BLIZZ_REGION", "eu").strip().lower().split("#")[0]
LOCALE = os.getenv("LOCALE", "fr_FR").strip()
REALM_ID = 1305
OUT_CSV  = Path(f"auctions_{REALM_ID}_{int(time.time())}.csv")

# --- OAuth token ---
oauth_url = f"https://{REGION}.battle.net/oauth/token"
token_resp = requests.post(
    oauth_url,
    data={"grant_type": "client_credentials"},
    auth=(CID, SECRET),
    timeout=15,
)
token_resp.raise_for_status()
token = token_resp.json()["access_token"]

# --- Appel Auction House ---
ah_url = (
    f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/"
    f"{REALM_ID}/auctions?namespace=dynamic-{REGION}&locale={LOCALE}"
)
headers = {"Authorization": f"Bearer {token}"}

print("Téléchargement des enchères ...")
r = requests.get(ah_url, headers=headers, timeout=30)
r.raise_for_status()
data = r.json()

# --- Récupération des noms des objets ---
print("Récupération des noms d’objets ...")
item_ids = {auc["item"]["id"] for auc in data["auctions"] if "item" in auc}

item_names = {}
for item_id in tqdm(item_ids, desc="Objets"):
    item_url = (
        f"https://{REGION}.api.blizzard.com/data/wow/item/{item_id}"
        f"?namespace=static-{REGION}&locale={LOCALE}"
    )
    resp = requests.get(item_url, headers=headers, timeout=15)
    if resp.status_code == 200:
        item_data = resp.json()
        item_names[item_id] = item_data.get("name", f"Item {item_id}")
    else:
        item_names[item_id] = f"Item {item_id}"  # fallback
    time.sleep(0.05)  # léger délai pour éviter un blocage de l’API


# --- Sauvegarde simplifiée ---
FIELDS = [
    "id", "item.id", "item_name", "buyout", "unit_price", "quantity",
    "time_left", "bid", "rand", "context", "pet_species_id"
]


def pick(obj, dotted):
    cur = obj
    for part in dotted.split('.'):
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur

with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(FIELDS)
    for auc in tqdm(data["auctions"], unit="enchère"):
        writer.writerow([pick(auc, f) for f in FIELDS])

print(f"Fichier généré : {OUT_CSV.resolve()}")

# --- Lire le fichier CSV ---
df = pd.read_csv(OUT_CSV)

# Nettoyage de base :
# - Remplacer les NaN par 0 pour les champs numériques
# - Supprimer les lignes sans item.id (inutilisables)
df = df[df["item.id"].notna()].copy()
df["item.id"] = df["item.id"].astype(int)

# Conversion des types numériques
for col in ["buyout", "unit_price", "quantity", "bid", "rand", "context", "pet_species_id"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# Nettoyage des noms d’objet
df["item_name"] = df["item_name"].fillna("Inconnu")



# --- Connexion à la base SQLite (fichier .db) ---
conn = sqlite3.connect("auctions.db")
cursor = conn.cursor()

# Création de la table
cursor.execute("""
CREATE TABLE IF NOT EXISTS auctions (
    id INTEGER PRIMARY KEY,
    item_id INTEGER,
    item_name TEXT,
    buyout INTEGER,
    unit_price INTEGER,
    quantity INTEGER,
    time_left TEXT,
    bid INTEGER,
    rand INTEGER,
    context INTEGER,
    pet_species_id INTEGER
)
""")

# Insertion
df.to_sql("auctions", conn, if_exists="append", index=False)

conn.commit()
conn.close()
