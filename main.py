from db import init_db
from fetch_auctions import fetch_and_store_auctions
from fetch_items import fetch_item_names

def main():
    init_db()
    item_ids = fetch_and_store_auctions()
    fetch_item_names(item_ids)

if __name__ == "__main__":
    main()
