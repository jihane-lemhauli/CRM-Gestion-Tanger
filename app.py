import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1️⃣ CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="ERP Solaire - Gestion Pro", layout="wide")

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
.carte-client {
    background: white; padding: 30px; border-radius: 15px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    border-top: 5px solid #2563eb; margin-top: 20px; color: #1e293b;
}
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
# 5️⃣ CHARGEMENT DES DONNÉES
# ---------------------------------------------------------
conn = obtenir_connexion()
clients_list = []
df_inventaire = pd.DataFrame()

if conn:
    try:
        # Liste des clients pour le menu et le ticker
        df_c = pd.read_sql("SELECT nom_client FROM Clients ORDER BY nom_client ASC", conn)
        clients_list = df_c['nom_client'].tolist()
        # Données inventaire
        df_inventaire = pd.read_sql("SELECT * FROM Inventaire", conn)
    except:
        pass
    finally:
        conn.close()

# ---------------------------------------------------------
# 6️⃣ INTERFACE PRINCIPALE
# ---------------------------------------------------------
st.title("🏙️ ERP Solaire : Gestion & Inventaire")

# Ticker des noms en haut
if clients_list:
    noms_str = "  •  ".join(clients_list)
    st.markdown(f'<div class="noms-ticker">👥 Clients : &nbsp;&nbsp; {noms_str}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 7️⃣ GESTION DE L'INVENTAIRE AVEC FILTRAGE (TABS)
# ---------------------------------------------------------
st.subheader("📦 Gestion de l'inventaire")
tabs_list = ["Tous"] + clients_list
tabs = st.tabs(tabs_list)

for i, tab in enumerate(tabs):
    with tab:
        selection = tabs_list[i]
        if selection == "Tous":
            df_filtre = df_inventaire
        else:
            # On filtre par le nom du client (colonne 'client_concerne')
            df_filtre = df_inventaire[df_inventaire['client_concerne'] == selection] if not df_inventaire.empty else pd.DataFrame()
        
        st.write(f"Affichage de **{len(df_filtre)}** lignes après filtrage.")
        st.dataframe(df_filtre, use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------
# 8️⃣ AJOUTER / MODIFIER UN CLIENT
# ---------------------------------------------------------
st.subheader("➕ Ajouter un nouveau client")
with st.form("form_ajout", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        new_nom = st.text_input("Nom du client")
        new_tel = st.text_input("Téléphone")
    with c2:
        new_email = st.text_input("Email")
        new_type = st.selectbox("Type", ["PME", "Particulier", "Grande Entreprise", "Commune"])
    new_adr = st.text_area("Adresse")
    
    if st.form_submit_button("Enregistrer le client"):
        if new_nom:
            conn = obtenir_connexion()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Clients (nom_client, telephone, email, type_client, adresse) VALUES (?,?,?,?,?)",
                                   (new_nom, new_tel, new_email, new_type, new_adr))
                    conn.commit()
                    st.success(f"✅ {new_nom} ajouté !")
                    st.rerun()
                finally: conn.close()
        else: st.warning("Le nom est obligatoire.")

# ---------------------------------------------------------
# 9️⃣ BOUTONS D'ACTION (BACKUP/EXCEL)
# ---------------------------------------------------------
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.button("💾 Sauvegarder direct f Excel")
with col_btn2:
    st.button("📩 Télécharger une copie (Backup)")
