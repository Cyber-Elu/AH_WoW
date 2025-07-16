import os, requests
from dotenv import load_dotenv

load_dotenv()

def get_token():
    region = os.getenv("BLIZZ_REGION", "eu").strip().lower().split("#")[0]
    url = f"https://{region}.battle.net/oauth/token"
    cid = os.getenv("BLIZZ_CLIENT_ID")
    secret = os.getenv("BLIZZ_CLIENT_SECRET")
    resp = requests.post(url, data={"grant_type": "client_credentials"}, auth=(cid, secret), timeout=15)
    resp.raise_for_status()
    return resp.json()["access_token"]

def pick(obj, dotted):
    cur = obj
    for part in dotted.split('.'):
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur
