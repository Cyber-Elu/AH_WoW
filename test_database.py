# test_database.py

import mysql.connector
from mysql.connector import Error
from config import Config
import time
from contextlib import closing

def test_database_connection():
    connection = None
    cursor = None
    try:
        print("🔌 Testing database connection...")
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )

        if connection.is_connected():
            db_info = connection.server_info  # Use property instead of deprecated method
            print(f"✅ Connected to MySQL Server version {db_info}")

            cursor = connection.cursor()

            with closing(connection.cursor()) as cursor:
                # Test inserting a sample item
                print("\n📦 Testing item insertion...")
                try:
                    cursor.execute("""
                        INSERT INTO items (item_id, name, quality, item_class, item_subclass, level)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (1, "Test Item", "Common", "Armor", "Cloth", 1))
                    connection.commit()
                    print("✅ Sample item inserted")

                    cursor.execute("SELECT * FROM items WHERE item_id = 1")
                    result = cursor.fetchone()
                    print("🔍 Retrieved item:", result)
                    
                except Error as e:
                    print(f"❌ Item insertion error: {e}")
                    connection.rollback()

                # Test inserting a sample auction
                print("\n📈 Testing auction insertion...")
                try:
                    cursor.execute("""
                        INSERT INTO auctions
                        (item_id, quantity, unit_price, buyout_price, time_left, bid_price, auction_duration)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (1, 1, 10000, 50000, "LONG", 10000, "LONG"))
                    connection.commit()
                    print("✅ Sample auction inserted")

                    cursor.execute("SELECT * FROM auctions WHERE item_id = 1")
                    result = cursor.fetchone()
                    print("🔍 Retrieved auction:", result)

                except Error as e:
                    print(f"❌ Auction insertion error: {e}")
                    connection.rollback()
                cursor.close()

    except Error as e:
        print(f"❌ Database connection error: {e}")

    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n🔒 Database connection closed")
    # Test Blizzard API connection
    print("\n🌐 Testing Blizzard API connection...")
    try:
        from blizzard_auth import BlizzardAuth
        auth = BlizzardAuth()
        token = auth.get_access_token()
        if token:
            print("✅ Blizzard API token obtained")
            print(f"🕒 Token expires in: {int(auth.token_expires - time.time())} seconds")
        else:
            print("❌ Failed to obtain Blizzard API token")
    except Exception as e:
        print(f"❌ Blizzard API connection error: {e}")


if __name__ == "__main__":
    test_database_connection()
