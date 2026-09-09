import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tool Fantacalcio", page_icon="⚽", layout="wide")

st.title("⚽ Tool Fantacalcio - Live Auction")
st.markdown("Il tuo assistente intelligente per gestire l'asta in tempo reale.")

# Creazione di un database iniziale basato sul listone ufficiale fornito
data = [
    {"Ruolo": "P", "Nome": "Carnesecchi", "Squadra": "Atalanta", "FVM": 55, "Prezzo": 17},
    {"Ruolo": "P", "Nome": "Sportiello", "Squadra": "Atalanta", "FVM": 1, "Prezzo": 1},
    {"Ruolo": "D", "Nome": "Scalvini", "Squadra": "Atalanta", "FVM": 28, "Prezzo": 10},
    {"Ruolo": "D", "Nome": "Zappacosta", "Squadra": "Atalanta", "FVM": 19, "Prezzo": 8},
    {"Ruolo": "D", "Nome": "Hien", "Squadra": "Atalanta", "FVM": 11, "Prezzo": 7},
    {"Ruolo": "D", "Nome": "Bellanova", "Squadra": "Atalanta", "FVM": 17, "Prezzo": 6},
    {"Ruolo": "C", "Nome": "Samardzic", "Squadra": "Atalanta", "FVM": 44, "Prezzo": 13},
    {"Ruolo": "C", "Nome": "Ederson D.S.", "Squadra": "Atalanta", "FVM": 46, "Prezzo": 12},
    {"Ruolo": "A", "Nome": "Scamacca", "Squadra": "Atalanta", "FVM": 110, "Prezzo": 19},
    {"Ruolo": "A", "Nome": "Krstovic", "Squadra": "Atalanta", "FVM": 98, "Prezzo": 18},
    {"Ruolo": "A", "Nome": "De Ketelaere", "Squadra": "Atalanta", "FVM": 95, "Prezzo": 17},
    {"Ruolo": "P", "Nome": "Skorupski", "Squadra": "Bologna", "FVM": 32, "Prezzo": 10},
    {"Ruolo": "D", "Nome": "Miranda J.", "Squadra": "Bologna", "FVM": 23, "Prezzo": 8},
    {"Ruolo": "C", "Nome": "Orsolini", "Squadra": "Bologna", "FVM": 177, "Prezzo": 25},
    {"Ruolo": "A", "Nome": "Dovbyk", "Squadra": "Bologna", "FVM": 51, "Prezzo": 15},
    {"Ruolo": "P", "Nome": "Caprile", "Squadra": "Cagliari", "FVM": 25, "Prezzo": 10},
    {"Ruolo": "C", "Nome": "Paz N.", "Squadra": "Como", "FVM": 245, "Prezzo": 29},
    {"Ruolo": "A", "Nome": "Kean", "Squadra": "Como", "FVM": 183, "Prezzo": 24},
    {"Ruolo": "P", "Nome": "De Gea", "Squadra": "Fiorentina", "FVM": 30, "Prezzo": 11},
    {"Ruolo": "P", "Nome": "Martinez Jo.", "Squadra": "Inter", "FVM": 68, "Prezzo": 17},
    {"Ruolo": "D", "Nome": "Dimarco", "Squadra": "Inter", "FVM": 240, "Prezzo": 31},
    {"Ruolo": "C", "Nome": "Calhanoglu", "Squadra": "Inter", "FVM": 243, "Prezzo": 28},
    {"Ruolo": "A", "Nome": "Martinez L.", "Squadra": "Inter", "FVM": 361, "Prezzo": 33},
    {"Ruolo": "A", "Nome": "Thuram", "Squadra": "Inter", "FVM": 249, "Prezzo": 28},
    {"Ruolo": "P", "Nome": "Vicario", "Squadra": "Juventus", "FVM": 70, "Prezzo": 17},
    {"Ruolo": "D", "Nome": "Bremer", "Squadra": "Juventus", "FVM": 60, "Prezzo": 16},
    {"Ruolo": "A", "Nome": "Kolo Muani", "Squadra": "Juventus", "FVM": 165, "Prezzo": 25},
    {"Ruolo": "P", "Nome": "Maignan", "Squadra": "Milan", "FVM": 52, "Prezzo": 15},
    {"Ruolo": "C", "Nome": "Pulisic", "Squadra": "Milan", "FVM": 150, "Prezzo": 24},
    {"Ruolo": "A", "Nome": "Ramos G.", "Squadra": "Milan", "FVM": 237, "Prezzo": 27},
    {"Ruolo": "P", "Nome": "Meret", "Squadra": "Napoli", "FVM": 48, "Prezzo": 11},
    {"Ruolo": "C", "Nome": "Mctominay", "Squadra": "Napoli", "FVM": 220, "Prezzo": 27},
    {"Ruolo": "A", "Nome": "Hojlund", "Squadra": "Napoli", "FVM": 260, "Prezzo": 28},
    {"Ruolo": "P", "Nome": "Svilar", "Squadra": "Roma", "FVM": 85, "Prezzo": 19},
    {"Ruolo": "A", "Nome": "Malen", "Squadra": "Roma", "FVM": 450, "Prezzo": 38}
]

df = pd.DataFrame(data)

# Sidebar per la gestione crediti e rosa
st.sidebar.header("💰 Gestione Crediti")
crediti_iniziali = st.sidebar.number_input("Crediti Iniziali", value=500, step=50)
crediti_spesi = st.sidebar.number_input("Crediti Spesi", value=0, step=1)
crediti_residui = crediti_iniziali - crediti_spesi

st.sidebar.metric(label="Crediti Residui", value=crediti_residui)

# Filtri di ricerca
st.subheader("🔍 Cerca Calciatore")
col1, col2 = st.columns(2)

with col1:
    search_query = st.text_input("Nome giocatore:")

with col2:
    selected_role = st.selectbox("Filtra per Ruolo", ["Tutti", "P", "D", "C", "A"])

# Applicazione filtri
filtered_df = df.copy()
if search_query:
    filtered_df = filtered_df[filtered_df["Nome"].str.contains(search_query, case=False, na=False)]
if selected_role != "Tutti":
    filtered_df = filtered_df[filtered_df["Ruolo"] == selected_role]

# Tabella dei risultati
st.dataframe(filtered_df, use_container_width=True)
