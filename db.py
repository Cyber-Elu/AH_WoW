import sqlite3

def get_connection():
    return sqlite3.connect("auctions.db")

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
            scraped_at TEXT,
            FOREIGN KEY(item_id) REFERENCES items(item_id)
        )
        """)
        conn.commit()

def insert_auctions(auction_rows):
    with get_connection() as conn:
        c = conn.cursor()
        c.executemany("""
        INSERT OR IGNORE INTO auctions
        (id, item_id, buyout, unit_price, quantity, time_left, bid, rand, context, pet_species_id, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, auction_rows)
        conn.commit()

def update_item_names(item_dict):
    with get_connection() as conn:
        c = conn.cursor()
        for item_id, name in item_dict.items():
            c.execute("""
            INSERT INTO items (item_id, item_name)
            VALUES (?, ?)
            ON CONFLICT(item_id) DO UPDATE SET item_name=excluded.item_name
            """, (item_id, name))
        conn.commit()
