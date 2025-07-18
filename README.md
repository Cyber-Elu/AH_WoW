#THIS IS A STUDENT PROJECT - NO PUBLIC USE, ONLY PERSONNAL

A Python projet to collect, analyse, visualize and apply ML to indicate when is the best moment to sell an item in World of Warcraft

First you need to create a API token to access to API Request from Blizzard and add them t a .env file in the directory.
Setup your SQL server and save your configuration in the .env file

collect_auction_data.py use your blizzard Client ID and Client Secret to request the Blizzard Auction House database to collect current data.
collect_item_details.py will then collect the item details for each unique item_id in the table auction and add these informations into items table.

daily_data_collector.py will store information day by day to keep track of price and number of item, these information will be used in the streamlit_dashboard.py to show graphic about the price and number of item to be sold

Your .env file should look like this :
# Blizzard Informations
BLIZZ_CLIENT_ID=
BLIZZ_CLIENT_SECRET=
BLIZZ_REGION=
LOCALE=
CONNECTED_REALM_ID=


# Database configuration
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=

Run db_helper.py to check the connection between your IDE and the SQL server.

run collect_auction_data.py AND THEN collect_item_details.py

Add a task to run collect_auction_data.py periodically.
