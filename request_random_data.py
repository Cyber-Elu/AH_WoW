import os
import random
import mysql.connector
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les informations de connexion à la base de données
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Connexion à la base de données
def get_db_connection():
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    return conn

# Fonction pour obtenir des lignes aléatoires d'une table
def get_random_rows(table_name, num_rows):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Requête pour obtenir des lignes aléatoires
    query = f"SELECT * FROM {table_name} ORDER BY RAND() LIMIT %s"
    cursor.execute(query, (num_rows,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

# Obtenir 5 lignes aléatoires des tables auctions et items
random_auctions = get_random_rows("auctions", 1)
random_items = get_random_rows("items", 1)

print("5 lignes aléatoires de la table auctions:")
for row in random_auctions:
    print(row)

print("\n5 lignes aléatoires de la table items:")
for row in random_items:
    print(row)
