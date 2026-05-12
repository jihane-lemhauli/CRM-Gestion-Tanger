import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1️⃣ CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="ERP Solaire - Inventaire", layout="wide")

# ---------------------------------------------------------
# 2️⃣ CONNEXION À LA BASE DE DONNÉES
# ---------------------------------------------------------
def obtenir_connexion():
    try:
        return sqlite3.connect('database.db', check_same_thread=False)
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

# -------------------------
# 3️⃣ AUTHENTIFICATION
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # (Le code d'authentification reste le même que celui que vous avez déjà)
    user = st.sidebar.text_input("Admin")
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Connexion"):
        if user == "admin" and pwd == "pass1234":
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# ---------------------------------------------------------
# 4️⃣ CHARGEMENT DES DONNÉES (Clients et Inventaire)
# ---------------------------------------------------------
conn = obtenir_connexion()
clients_list = ["Tous les clients"] # Option par défaut
df_inventaire = pd.DataFrame()

if conn:
    try:
        # 1. Récupérer la liste des clients pour les onglets
        df_c = pd.read_sql("SELECT DISTINCT nom_client FROM Clients ORDER BY nom_client", conn)
        clients_list += df_c['nom_client'].tolist()
        
        # 2. Récupérer toutes les données de l'inventaire
        df_inventaire = pd.read_sql("SELECT * FROM Inventaire", conn) # Assurez-vous que la table s'appelle Inventaire
    except:
        st.warning("⚠️ Vérifiez que les tables 'Clients' et 'Inventaire' existent.")
    finally:
        conn.close()

# ---------------------------------------------------------
# 5️⃣ INTERFACE : LISTE DES CLIENTS (TABS)
# ---------------------------------------------------------
st.title("📦 Gestion de l'inventaire")

# Création des onglets en haut
tabs = st.tabs(clients_list)

# Logique de filtrage
for i, tab in enumerate(tabs):
    with tab:
        client_selectionne = clients_list[i]
        
        # Filtrer le DataFrame selon le client cliqué
        if client_selectionne == "Tous les clients":
            df_filtre = df_inventaire
        else:
            # On suppose que vous avez une colonne 'client_concerne' dans votre table Inventaire
            df_filtre = df_inventaire[df_inventaire['client_concerne'] == client_selectionne]

        # ---------------------------------------------------------
        # 6️⃣ AFFICHAGE DU TABLEAU FILTRÉ
        # ---------------------------------------------------------
        if not df_filtre.empty:
            st.write(f"Affichage de **{len(df_filtre)}** lignes pour : `{client_selectionne}`")
            st.dataframe(df_filtre, use_container_width=True, hide_index=True)
        else:
            st.info(f"Aucun article en inventaire pour {client_selectionne}")

# ---------------------------------------------------------
# 7️⃣ ACTIONS (Boutons en bas comme sur votre image)
# ---------------------------------------------------------
col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    if st.button("💾 Sauvegarder direct f Excel"):
        st.toast("Exportation en cours...")
with col_btn2:
    st.download_button("📩 Télécharger une copie (Backup)", data="...", file_name="backup.csv")
