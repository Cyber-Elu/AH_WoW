# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'wow_ah_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'wow_auction_house')

    # Blizzard API configuration
    BLIZZ_CLIENT_ID = os.getenv('BLIZZ_CLIENT_ID', '')
    BLIZZ_CLIENT_SECRET = os.getenv('BLIZZ_CLIENT_SECRET', '')
    BLIZZ_REGION = os.getenv('BLIZZ_REGION', 'eu')
    LOCALE = os.getenv('LOCALE', 'fr_FR')
    CONNECTED_REALM_ID = os.getenv('CONNECTED_REALM_ID', '')  # Add this line

    # You can add this helper property if needed
    @property
    def auction_api_url(self):
        return f"https://{self.BLIZZ_REGION}.api.blizzard.com/data/wow/connected-realm/{self.CONNECTED_REALM_ID}/auctions"
