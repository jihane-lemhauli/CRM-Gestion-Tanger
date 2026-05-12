import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1️⃣ CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="ERP Solaire - Gestion de l'inventaire", layout="wide")

# ---------------------------------------------------------
# 2️⃣ CONNEXION À LA BASE DE DONNÉES
# ---------------------------------------------------------
def obtenir_connexion():
    try:
        # Connexion au fichier database.db
        return sqlite3.connect('database.db', check_same_thread=False)
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

# -------------------------
# 3️⃣ AUTHENTIFICATION (Section 3)
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def check_login(username, password):
    return username == "admin" and password == "pass1234"

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🔐 Connexion au Système CRM</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        user = st.text_input("Nom d'utilisateur")
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter", use_container_width=True):
            if check_login(user, pwd):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("⚠️ Identifiants incorrects")
    st.stop()

# -------------------------
# 4️⃣ DESIGN CSS
# -------------------------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%); }
.noms-ticker {
    background: #1e3a8a; color: white; padding: 10px; border-radius: 8px;
    margin-bottom: 20px; font-weight: bold; overflow-x: auto; white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------------------------------------------------
# 5️⃣ CHARGEMENT DES DONNÉES (Section 5)
# ---------------------------------------------------------
conn = obtenir_connexion()
clients_options = ["Tous les clients"]
df_inventaire = pd.DataFrame()

if conn:
    try:
        # Récupérer les noms des clients pour la liste de filtrage
        df_c = pd.read_sql("SELECT DISTINCT nom_client FROM Clients ORDER BY nom_client ASC", conn)
        clients_options += df_c['nom_client'].tolist()
        
        # Récupérer toutes les données de l'inventaire
        df_inventaire = pd.read_sql("SELECT * FROM Inventaire", conn)
    except:
        pass
    finally:
        conn.close()

# ---------------------------------------------------------
# 6️⃣ INTERFACE PRINCIPALE (Aperçu Ticker)
# ---------------------------------------------------------
st.title("🏙️ ERP Solaire : Gestion de l'inventaire")

# Ticker rapide en haut pour la visibilité
if len(clients_options) > 1:
    noms_str = "  •  ".join(clients_options[1:])
    st.markdown(f'<div class="noms-ticker">👥 Clients Actifs : &nbsp;&nbsp; {noms_str}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 7️⃣ FILTRE PAR LISTE DE CLIENT (La partie que tu voulais)
# ---------------------------------------------------------
# Had l-selectbox hiya "Liste de client" li t-cliqui 3liha
client_selectionne = st.selectbox(
    "📂 Liste de client", 
    options=clients_options,
    help="Sélectionnez un client pour filtrer l'inventaire ci-dessous"
)

# ---------------------------------------------------------
# 8️⃣ AFFICHAGE DE L'INVENTAIRE FILTRÉ (Section 6)
# ---------------------------------------------------------
if not df_inventaire.empty:
    if client_selectionne != "Tous les clients":
        # Filtrage dynamique par la colonne client_concerne
        df_filtre = df_inventaire[df_inventaire['client_concerne'] == client_selectionne]
    else:
        df_filtre = df_inventaire

    st.write(f"Affichage de **{len(df_filtre)}** lignes après filtrage.")
    st.dataframe(df_filtre, use_container_width=True, hide_index=True)
else:
    st.info("Aucune donnée d'inventaire disponible.")

st.divider()

# ---------------------------------------------------------
# 9️⃣ ACTIONS (Boutons en bas b7al image_8f4f80.jpg)
# ---------------------------------------------------------
c1, c2 = st.columns(2)
with c1:
    if st.button("💾 Sauvegarder direct f Excel", use_container_width=True):
        st.success("Exportation simulée avec succès !")
with c2:
    st.button("📩 Télécharger une copie (Backup)", use_container_width=True)
