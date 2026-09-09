import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tool Fantacalcio - Tabellone Asta", page_icon="⚽", layout="wide")

st.title("⚽ Tabellone Asta in Tempo Reale")
st.markdown("Gestisci le rose delle squadre partecipanti direttamente nella griglia sottostante.")

# Caricamento del listone completo (rimane nascosto ma disponibile se serve)
@st.cache_data
def load_data():
    try:
        return pd.read_csv("giocatori.csv")
    except:
        return pd.DataFrame(columns=["Ruolo", "Nome", "Squadra", "FVM", "Prezzo"])

df_listone = load_data()

# Configurazione del numero di squadre (colonne del tabellone)
num_squadre = st.sidebar.slider("Numero di squadre partecipanti", min_value=6, max_value=12, value=8)

# Creazione della struttura dati per il tabellone editabile
# Righe totali: 1 (Nome Squadra) + 1 (Titolo Portieri) + 3 (Slot P) + 1 (Titolo D) + 8 (Slot D) + 1 (Titolo C) + 8 (Slot C) + 1 (Titolo A) + 6 (Slot A) = 30 righe
@st.cache_data
def get_initial_board(n_cols):
    col_names = [f"Squadra {i+1}" for i in range(n_cols)]
    
    rows = []
    # 0: Nome Squadra
    rows.append(col_names)
    # 1: Header Portieri
    rows.append(["--- PORTIERI ---"] * n_cols)
    # 3 slot Portieri
    for _ in range(3):
        rows.append([""] * n_cols)
        
    # Header Difensori
    rows.append(["--- DIFENSORI ---"] * n_cols)
    # 8 slot Difensori
    for _ in range(8):
        rows.append([""] * n_cols)
        
    # Header Centrocampisti
    rows.append(["--- CENTROCAMPISTI ---"] * n_cols)
    # 8 slot Centrocampisti
    for _ in range(8):
        rows.append([""] * n_cols)
        
    # Header Attaccanti
    rows.append(["--- ATTACCANTI ---"] * n_cols)
    # 6 slot Attaccanti
    for _ in range(6):
        rows.append([""] * n_cols)
        
    index_labels = [
        "Nome Squadra", "Sezione", "P 1", "P 2", "P 3", 
        "Sezione", "D 1", "D 2", "D 3", "D 4", "D 5", "D 6", "D 7", "D 8",
        "Sezione", "C 1", "C 2", "C 3", "C 4", "C 5", "C 6", "C 7", "C 8",
        "Sezione", "A 1", "A 2", "A 3", "A 4", "A 5", "A 6"
    ]
    
    return pd.DataFrame(rows, index=index_labels, columns=col_names)

# Inizializzazione dello stato della griglia
if "board_df" not in st.session_state:
    st.session_state.board_df = get_initial_board(num_squadre)

# Se cambia il numero di squadre, ricostruiamo la tabella
if len(st.session_state.board_df.columns) != num_squadre:
    st.session_state.board_df = get_initial_board(num_squadre)

st.subheader("📋 Griglia Rose Partecipanti")
st.info("Clicca sulle celle per inserire i giocatori acquistati e i relativi prezzi. Modifica la prima riga per mettere il nome della tua squadra.")

# Tabella interattiva e modificabile
edited_board = st.data_editor(
    st.session_state.board_df, 
    use_container_width=True,
    num_rows="fixed"
)

# Salvataggio modifiche nello stato
st.session_state.board_df = edited_board

# Sezione opzionale di ricerca rapida nascosta o comprimibile per consultare il listone
with st.expander("🔍 Cerca rapida nel Listone ufficiale (Nascosto di default)"):
    search_query = st.text_input("Cerca nome giocatore:")
    if search_query:
        res = df_listone[df_listone["Nome"].str.contains(search_query, case=False, na=False)]
        st.dataframe(res, use_container_width=True)
