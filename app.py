import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

DB_PATH = "auctions.db"

st.set_page_config(page_title="Données des enchères WoW", layout="wide")

# Fonctions avec cache
@st.cache_data(ttl=600)  # Cache pour 10 minutes
def get_total_auctions(_conn):
    query = "SELECT COUNT(*) FROM auctions"
    return pd.read_sql_query(query, _conn).iloc[0, 0]

@st.cache_data
def get_items(_conn):
    return pd.read_sql_query("""
        SELECT DISTINCT i.item_id, i.item_name
        FROM items i
        JOIN auctions a ON a.item_id = i.item_id
        ORDER BY i.item_name ASC
    """, _conn)

@st.cache_data(ttl=600)
def get_auction_data(_conn, item_id):
    query = """
        SELECT a.unit_price, a.buyout, a.scraped_at
        FROM auctions a
        WHERE a.item_id = ?
        ORDER BY a.scraped_at ASC
    """
    return pd.read_sql_query(query, _conn, params=(item_id,))

# Interface principale
def main():
    with sqlite3.connect(DB_PATH) as conn:
        page = st.sidebar.selectbox("Naviguer vers :", ["📊 Statistiques globales", "📈 Prix par objet"])

        if page == "📊 Statistiques globales":
            st.title("Nombre d’objets en vente")
            total = get_total_auctions(conn)
            st.metric("Nombre d’enchères", total)

        elif page == "📈 Prix par objet":
            st.title("Évolution des prix par objet")
            items_df = get_items(conn)

            if items_df.empty:
                st.warning("Aucun objet trouvé dans la base.")
                return

            item_name = st.selectbox("Choisissez un objet :", items_df["item_name"])
            filtered = items_df.loc[items_df["item_name"] == item_name, "item_id"]

            if filtered.empty:
                st.error("Aucun ID trouvé pour l’objet sélectionné.")
                return

            item_id = filtered.values[0]
            df = get_auction_data(conn, item_id)

            if df.empty:
                st.warning("Aucune donnée disponible pour cet objet.")
            else:
                df['scraped_at'] = pd.to_datetime(df['scraped_at'])
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(df['scraped_at'], df['unit_price'], label='Prix unitaire', marker='o')

                if pd.notna(df['buyout']).any():
                    ax.plot(df['scraped_at'], df['buyout'], label='Prix d\'achat immédiat', marker='x')

                ax.set_title(f"Évolution des prix – {item_name}")
                ax.set_xlabel("Date")
                ax.set_ylabel("Prix (cuivre)")
                ax.grid(True)
                ax.legend()
                st.pyplot(fig)

if __name__ == "__main__":
    main()
