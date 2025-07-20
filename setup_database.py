import mysql.connector
from mysql.connector import Error
from config import Config

def create_database():
    connection = None
    cursor = None
    try:
        # First, connect to MySQL server without specifying a database
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
            print(f"Database '{Config.DB_NAME}' created or already exists")

            # Connect to the database
            connection.database = Config.DB_NAME

            # Create items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    item_id INT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    quality VARCHAR(50),
                    item_class VARCHAR(50),
                    item_subclass VARCHAR(50),
                    level INT,
                    required_level INT,
                    is_equippable BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            print("Table 'items' created or already exists")

            # Create auctions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auctions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT NOT NULL,
                    quantity INT,
                    unit_price BIGINT,
                    buyout_price BIGINT,
                    time_left VARCHAR(50),
                    bid_price BIGINT,
                    auction_duration VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES items(item_id)
    )
""")
            print("Table 'auctions' created or already exists")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection is not None and connection.is_connected():
            if cursor is not None:
                cursor.close()
            connection.close()
            print("MySQL connection is closed")
if __name__ == "__main__":
    print("Starting database setup...")
    create_database()
    print("Database setup completed.")
