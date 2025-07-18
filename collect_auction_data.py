import requests
import json
from datetime import datetime
from config import Config
from db_helper import get_db_connection

# Initialize Config once at the module level
config = Config()

def get_blizzard_token():
    """Get OAuth token from Blizzard API"""
    auth_url = f"https://{config.BLIZZ_REGION}.battle.net/oauth/token"
    payload = {
        'grant_type': 'client_credentials'
    }
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
        raise Exception(f"Failed to get token: {str(e)}")

def fetch_auction_data():
    """Fetch auction data from Blizzard API"""
    try:
        token = get_blizzard_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Battlenet-Namespace': f'dynamic-{config.BLIZZ_REGION}'
        }

        url = f"https://{config.BLIZZ_REGION}.api.blizzard.com/data/wow/connected-realm/{config.CONNECTED_REALM_ID}/auctions"

        params = {
            'namespace': f'dynamic-{config.BLIZZ_REGION}',
            'locale': config.LOCALE
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch auction data: {str(e)}")

def process_auction_data(auction_data):
    """Process and store auction data in the database"""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            raise Exception("Failed to get database connection")

        cursor = connection.cursor()

        # Get current timestamp
        current_time = datetime.utcnow()

        # Process auctions
        auctions = auction_data.get('auctions', [])
        if not auctions:
            print("No auctions found in the response")
            return False

        processed_count = 0
        for auction in auctions:
            try:
                item_id = auction['item']['id']
                quantity = auction.get('quantity', 1)
                unit_price = auction.get('unit_price', 0)
                buyout_price = auction.get('buyout', 0)
                time_left = auction.get('time_left', '')
                bid_price = auction.get('bid', 0)
                auction_duration = auction.get('duration', '')

                # Check if item exists in items table
                cursor.execute("SELECT 1 FROM items WHERE item_id = %s", (item_id,))
                if not cursor.fetchone():
                    # Insert placeholder for unknown items
                    cursor.execute("""
                        INSERT INTO items (item_id, name)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE name = name
                    """, (item_id, f"Unknown Item {item_id}"))

                # Insert auction data with timestamp
                cursor.execute("""
                    INSERT INTO auctions
                    (item_id, quantity, unit_price, buyout_price,
                     time_left, bid_price, auction_duration, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (item_id, quantity, unit_price, buyout_price,
                      time_left, bid_price, auction_duration, current_time))

                processed_count += 1

            except Exception as e:
                print(f"Error processing auction {auction.get('id', 'unknown')}: {str(e)}")
                continue

        connection.commit()
        print(f"Successfully processed {processed_count}/{len(auctions)} auctions")
        return True

    except Exception as e:
        print(f"Error processing auction data: {str(e)}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("Starting auction data collection...")

    try:
        # Verify we have all required configuration
        required_configs = [
            'BLIZZ_CLIENT_ID', 'BLIZZ_CLIENT_SECRET',
            'BLIZZ_REGION', 'LOCALE', 'CONNECTED_REALM_ID'
        ]

        missing_configs = [cfg for cfg in required_configs if not getattr(config, cfg)]
        if missing_configs:
            raise Exception(f"Missing required configuration: {', '.join(missing_configs)}")

        auction_data = fetch_auction_data()
        if auction_data:
            process_auction_data(auction_data)

        print("Auction data collection completed successfully.")

    except Exception as e:
        print(f"Error in auction data collection: {str(e)}")
