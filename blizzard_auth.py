# blizzard_auth.py
import requests
from config import Config
import time

class BlizzardAuth:
    def __init__(self):
        self.config = Config()
        self.token = None
        self.token_expires = 0

    def get_access_token(self):
        """Get a fresh Blizzard API access token"""
        if time.time() < self.token_expires and self.token:
            return self.token

        auth_url = f"https://{self.config.BLIZZ_REGION}.battle.net/oauth/token"
        payload = {
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(
                auth_url,
                data=payload,
                auth=(self.config.BLIZZ_CLIENT_ID, self.config.BLIZZ_CLIENT_SECRET)
            )
            response.raise_for_status()
            data = response.json()

            self.token = data['access_token']
            self.token_expires = time.time() + data['expires_in'] - 60  # Subtract 60s as buffer

            return self.token
        except requests.exceptions.RequestException as e:
            print(f"Error getting Blizzard API token: {e}")
            return None