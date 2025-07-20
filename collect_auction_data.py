import requests
import json
from datetime import datetime, timezone
from config import Config
from db_helper import get_db_connection

# Initialiser la configuration
config = Config()

def get_blizzard_token():
    """Obtenir un token OAuth depuis l'API de Blizzard"""
    auth_url = f"https://{config.BLIZZ_REGION}.battle.net/oauth/token"
    payload = {'grant_type': 'client_credentials'}
    try:
        response = requests.post(
            auth_url,
            auth=(config.BLIZZ_CLIENT_ID, config.BLIZZ_CLIENT_SECRET),
            data=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Erreur lors de l'obtention du token : {str(e)}")

def fetch_auction_data():
    """Récupérer les données d'enchères classiques et commodities"""
    try:
        token = get_blizzard_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Battlenet-Namespace': f'dynamic-{config.BLIZZ_REGION}'
        }

        params = {
            'namespace': f'dynamic-{config.BLIZZ_REGION}',
            'locale': config.LOCALE
        }

        # 🔹 Enchères classiques (liées au royaume connecté)
        classic_url = (
            f"https://{config.BLIZZ_REGION}.api.blizzard.com/data/wow/connected-realm/"
            f"{config.CONNECTED_REALM_ID}/auctions"
        )
        classic_response = requests.get(classic_url, headers=headers, params=params, timeout=30)
        classic_response.raise_for_status()
        classic_data = classic_response.json()

        # 🔹 Commodities (objets de consommation global)
        commodity_url = f"https://{config.BLIZZ_REGION}.api.blizzard.com/data/wow/auctions/commodities"
        commodity_response = requests.get(commodity_url, headers=headers, params=params, timeout=30)
        commodity_response.raise_for_status()
        commodity_data = commodity_response.json()

        return {
            'classic': classic_data.get('auctions', []),
            'commodities': commodity_data.get('auctions', [])
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Erreur lors de la récupération des données d'enchères : {str(e)}")

def process_auction_data(auctions_by_type):
    """Traite les données d'enchères classiques et commodities et les insère dans la base"""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            raise Exception("Impossible d'établir la connexion à la base de données")

        cursor = connection.cursor()
        now = datetime.now(timezone.utc)

        total_processed = 0
        new_items = 0
        existing_items = 0

        for auction_type, auctions in auctions_by_type.items():
            for auction in auctions:
                try:
                    item = auction.get('item', {})
                    item_id = item.get('id')
                    if not item_id:
                        continue

                    quantity = auction.get('quantity', 1)
                    unit_price = auction.get('unit_price', 0)
                    buyout_price = auction.get('buyout', 0)
                    time_left = auction.get('time_left', '')
                    bid_price = auction.get('bid', 0)
                    duration = auction.get('duration', '')

                    # Vérifie si l'objet est déjà connu
                    cursor.execute("SELECT 1 FROM items WHERE item_id = %s", (item_id,))
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO items (item_id, name) VALUES (%s, %s)",
                            (item_id, f"Objet inconnu {item_id}")
                        )
                        new_items += 1
                    else:
                        existing_items += 1

                    # Insère les données d'enchères
                    cursor.execute(
                        """
                        INSERT INTO auctions
                        (item_id, quantity, unit_price, buyout_price, time_left, bid_price, auction_duration, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (item_id, quantity, unit_price, buyout_price, time_left, bid_price, duration, now)
                    )

                    total_processed += 1

                except Exception as e:
                    print(f"Erreur lors du traitement de l'enchère {auction.get('id', 'inconnue')} : {str(e)}")

        connection.commit()

        print(f"✅ {total_processed} enchères traitées.")
        print(f"📦 {new_items} nouveaux objets ajoutés à la base de données.")
        print(f"📦 {existing_items} objets déjà connus ignorés.")

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"❌ Erreur lors du traitement des données : {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("\n🚀 Démarrage de la collecte des données d'enchères...")

    try:
        required_configs = [
            'BLIZZ_CLIENT_ID', 'BLIZZ_CLIENT_SECRET',
            'BLIZZ_REGION', 'LOCALE', 'CONNECTED_REALM_ID'
        ]
        missing = [k for k in required_configs if not getattr(config, k)]
        if missing:
            raise Exception(f"Configuration manquante : {', '.join(missing)}")

        auctions_by_type = fetch_auction_data()
        if auctions_by_type:
            process_auction_data(auctions_by_type)

        print("\n✅ Collecte des données d'enchères terminée avec succès.")

    except Exception as e:
        print(f"\n❌ Erreur critique : {str(e)}")
