# test_database.py
import mysql.connector
from mysql.connector import Error
from config import Config
from blizzard_auth import BlizzardAuth

def test_database_connection():
    try:
        # Test database connection
        print("Testing database connection...")
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Successfully connected to MySQL Server version {db_info}")

            # Test inserting a sample item
            cursor = connection.cursor()
            print("\nTesting item insertion...")

            try:
                cursor.execute("""
                    INSERT INTO items (item_id, name, quality, item_class, item_subclass, level)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (1, "Test Item", "Common", "Armor", "Cloth", 1))
                connection.commit()
                print("✅ Sample item inserted successfully")

                # Verify the insertion
                cursor.execute("SELECT * FROM items WHERE item_id = 1")
                result = cursor.fetchone()
                print("\nVerifying insertion:")
                print(f"Retrieved item: {result}")

            except Error as e:
                print(f"❌ Error inserting test item: {e}")
                connection.rollback()

            # Test inserting a sample auction
            print("\nTesting auction insertion...")
            try:
                cursor.execute("""
                    INSERT INTO auctions
                    (item_id, quantity, unit_price, buyout_price, time_left, bid_price, auction_duration)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (1, 1, 10000, 50000, "LONG", 10000, "LONG"))
                connection.commit()
                print("✅ Sample auction inserted successfully")

                # Verify the insertion
                cursor.execute("SELECT * FROM auctions WHERE item_id = 1")
                result = cursor.fetchone()
                print("\nVerifying insertion:")
                print(f"Retrieved auction: {result}")

            except Error as e:
                print(f"❌ Error inserting test auction: {e}")
                connection.rollback()

    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nDatabase connection closed")

                # Test Blizzard API connection
    print("\nTesting Blizzard API connection...")
    auth = BlizzardAuth()
    token = auth.get_access_token()

    if token:
        print("✅ Successfully obtained Blizzard API token")
        print(f"Token expires in: {int(auth.token_expires - time.time())} seconds")
    else:
        print("❌ Failed to obtain Blizzard API token")

if __name__ == "__main__":
    test_database_connection()
