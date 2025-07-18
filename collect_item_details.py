import requests
import time
from config import Config
from db_helper import get_db_connection

def get_blizzard_token():
    auth_url = f"https://{Config.BLIZZ_REGION}.battle.net/oauth/token"
    payload = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(auth_url, auth=(Config.BLIZZ_CLIENT_ID, Config.BLIZZ_CLIENT_SECRET), data=payload)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get token: {response.text}")

def fetch_item_details(item_id):
    token = get_blizzard_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Battlenet-Namespace': f'static-{Config.BLIZZ_REGION}'
    }
    url = f"https://{Config.BLIZZ_REGION}.api.blizzard.com/data/wow/item/{item_id}?namespace=static-{Config.BLIZZ_REGION}&locale={Config.LOCALE}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch item {item_id}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching item {item_id}: {str(e)}")
        return None

def process_item_details():
    connection = get_db_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        # Get all unique item_ids from auctions that don't have complete details
        cursor.execute("""
            SELECT DISTINCT a.item_id
            FROM auctions a
            LEFT JOIN items i ON a.item_id = i.item_id
            WHERE i.name LIKE 'Unknown Item%' OR i.quality IS NULL
        """)
        item_ids = [row[0] for row in cursor.fetchall()]

        print(f"Found {len(item_ids)} items needing details")

        for item_id in item_ids:
            print(f"Processing item {item_id}")
            item_data = fetch_item_details(item_id)
            if item_data:
                try:
                    name = item_data.get('name', f"Unknown Item {item_id}")
                    quality = item_data.get('quality', {}).get('name', None)
                    item_class = item_data.get('item_class', {}).get('name', None)
                    item_subclass = item_data.get('item_subclass', {}).get('name', None)
                    level = item_data.get('level', None)
                    required_level = item_data.get('required_level', None)
                    is_equippable = item_data.get('is_equippable', False)

                    cursor.execute("""
                        INSERT INTO items
                        (item_id, name, quality, item_class, item_subclass, level, required_level, is_equippable)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            quality = VALUES(quality),
                            item_class = VALUES(item_class),
                            item_subclass = VALUES(item_subclass),
                            level = VALUES(level),
                            required_level = VALUES(required_level),
                            is_equippable = VALUES(is_equippable)
                    """, (item_id, name, quality, item_class, item_subclass, level, required_level, is_equippable))

                    connection.commit()
                except Exception as e:
                    print(f"Error processing item {item_id}: {str(e)}")
                    connection.rollback()

            # Be gentle with the API
            time.sleep(0.005) # 5 milliseconds delay to avoid hitting rate limits
        return True
    except Exception as e:
        print(f"Error processing item details: {str(e)}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("Starting item details collection...")
    process_item_details()
    print("Item details collection completed.")
