import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tool Fantacalcio", page_icon="⚽", layout="wide")

st.title("⚽ Tool Fantacalcio - Live Auction")
st.markdown("Il tuo assistente intelligente per gestire l'asta in tempo reale con la lista completa.")

# Caricamento automatico del file CSV dei giocatori
@st.cache_data
def load_data():
    try:
        return pd.read_csv("giocatori.csv")
    except Exception as e:
        st.error(f"Errore nel caricamento del file CSV: {e}")
        return pd.DataFrame(columns=["Ruolo", "Nome", "Squadra", "FVM", "Prezzo"])

df = load_data()

# Sidebar per la gestione crediti
st.sidebar.header("💰 Gestione Crediti")
crediti_iniziali = st.sidebar.number_input("Crediti Iniziali", value=500, step=50)
crediti_spesi = st.sidebar.number_input("Crediti Spesi", value=0, step=1)
crediti_residui = crediti_iniziali - crediti_spesi

st.sidebar.metric(label="Crediti Residui", value=crediti_residui)

# Filtri di ricerca
st.subheader("🔍 Cerca Calciatore")
col1, col2, col3 = st.columns(3)

with col1:
    search_query = st.text_input("Nome giocatore:")

with col2:
    selected_role = st.selectbox("Filtra per Ruolo", ["Tutti", "P", "D", "C", "A"])

with col3:
    # Filtro opzionale per squadra se il dataframe non è vuoto
    squadre = ["Tutte"] + sorted(df["Squadra"].unique().tolist()) if not df.empty else ["Tutte"]
    selected_team = st.selectbox("Filtra per Squadra", squadre)

# Applicazione filtri
filtered_df = df.copy()
if search_query:
    filtered_df = filtered_df[filtered_df["Nome"].str.contains(search_query, case=False, na=False)]
if selected_role != "Tutti":
    filtered_df = filtered_df[filtered_df["Ruolo"] == selected_role]
if selected_team != "Tutte":
    filtered_df = filtered_df[filtered_df["Squadra"] == selected_team]

# Tabella dei risultati
st.markdown(f"**Giocatori trovati:** {len(filtered_df)}")
st.dataframe(filtered_df, use_container_width=True)
