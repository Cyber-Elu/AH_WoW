import sqlite3

DB_NAME = "auctions.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY,
            item_name TEXT
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS auctions (
            id INTEGER PRIMARY KEY,
            item_id INTEGER,
            buyout INTEGER,
            unit_price INTEGER,
            quantity INTEGER,
            time_left TEXT,
            bid INTEGER,
            rand INTEGER,
            context INTEGER,
            pet_species_id INTEGER,
            bonus_lists TEXT,
            modifiers TEXT,
            pet_breed_id INTEGER,
            pet_level INTEGER,
            item_context INTEGER,
            owner TEXT,
            owner_realm TEXT,
            scraped_at TEXT,
            FOREIGN KEY(item_id) REFERENCES items(item_id)
        )
        """)
        conn.commit()

def insert_auctions(auction_rows):
    with get_connection() as conn:
        c = conn.cursor()
        c.executemany("""
        INSERT OR REPLACE INTO auctions (
            id, item_id, buyout, unit_price, quantity,
            time_left, bid, rand, context, pet_species_id,
            bonus_lists, modifiers, pet_breed_id, pet_level,
            item_context, owner, owner_realm, scraped_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, auction_rows)
        conn.commit()

def insert_items(items):
    """items: list of tuples (item_id, item_name)"""
    with get_connection() as conn:
        c = conn.cursor()
        c.executemany("""
        INSERT INTO items (item_id, item_name)
        VALUES (?, ?)
        ON CONFLICT(item_id) DO UPDATE SET item_name=excluded.item_name
        """, items)
        conn.commit()

def check_auctions_with_items():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        SELECT auctions.id, items.item_name, auctions.buyout, auctions.quantity,
               auctions.unit_price, auctions.time_left, auctions.bid, auctions.rand,
               auctions.context, auctions.pet_species_id, auctions.bonus_lists,
               auctions.modifiers, auctions.pet_breed_id, auctions.pet_level,
               auctions.item_context, auctions.owner, auctions.owner_realm,
               auctions.scraped_at
        FROM auctions
        JOIN items ON auctions.item_id = items.item_id
        """)
        results = c.fetchall()
        for row in results:
            print(row)
