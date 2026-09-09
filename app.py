import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tool Fantacalcio - Live Auction", page_icon="⚽", layout="wide")

st.title("⚽ Tabellone Asta in Tempo Real")
st.markdown("Cerca un giocatore dal listone e assegnalo direttamente alla squadra acquirente.")

# Caricamento del listone
@st.cache_data
def load_data():
    try:
        return pd.read_csv("giocatori.csv")
    except:
        return pd.DataFrame(columns=["Ruolo", "Nome", "Squadra", "FVM", "Prezzo"])

df_listone = load_data()

# Configurazione Squadre nella Sidebar
st.sidebar.header("⚙️ Configurazione Lega")
default_squadre = ["Fede", "Riky", "Gio", "Penno", "Ale", "Aldo", "Margy", "Lupo"]
squadre = []
for i, nome_def in enumerate(default_squadre):
    s = st.sidebar.text_input(f"Squadra {i+1}", value=nome_def)
    squadre.append(s)

# Struttura slot per ruolo
SLOT_CONFIG = {
    "P": 3,
    "D": 8,
    "C": 8,
    "A": 6
}

# Inizializzazione dello stato delle rose nel session_state
if "rose" not in st.session_state:
    st.session_state.rose = {}
    for sq in squadre:
        st.session_state.rose[sq] = {
            "P": ["" for _ in range(SLOT_CONFIG["P"])],
            "D": ["" for _ in range(SLOT_CONFIG["D"])],
            "C": ["" for _ in range(SLOT_CONFIG["C"])],
            "A": ["" for _ in range(SLOT_CONFIG["A"])]
        }

# Se cambiano i nomi delle squadre o la lista, sincronizziamo lo stato
for sq in squadre:
    if sq not in st.session_state.rose:
        st.session_state.rose[sq] = {
            "P": ["" for _ in range(SLOT_CONFIG["P"])],
            "D": ["" for _ in range(SLOT_CONFIG["D"])],
            "C": ["" for _ in range(SLOT_CONFIG["C"])],
            "A": ["" for _ in range(SLOT_CONFIG["A"])]
        }

# --- SEZIONE ASTA / ASSEGNAZIONE ---
st.subheader("🛒 Assegnazione Giocatore")
col_search1, col_search2, col_search3, col_search4 = st.columns([2, 1, 1, 1])

with col_search1:
    search_name = st.selectbox("Cerca Giocatore dal Listone", options=[""] + df_listone["Nome"].tolist())

selected_player_row = None
if search_name:
    selected_player_row = df_listone[df_listone["Nome"] == search_name].iloc[0]
    st.write(f"**Ruolo:** {selected_player_row['Ruolo']} | **Squadra Serie A:** {selected_player_row['Squadra']} | **FVM:** {selected_player_row['FVM']} | **Prezzo Consigliato:** {selected_player_row['Prezzo']}")

with col_search2:
    prezzo_pagato = st.number_input("Prezzo d'asta", min_value=1, value=int(selected_player_row['Prezzo']) if search_name else 1)

with col_search3:
    squadra_acquirente = st.selectbox("Assegna a Squadra", options=squadre)

with col_search4:
    st.text("") # Spaziatura
    st.text("")
    assegna_btn = st.button("Assegna Giocatore", type="primary")

if assegna_btn and search_name:
    ruolo = selected_player_row['Ruolo']
    nome_giocatore = f"{search_name} ({prezzo_pagato} cr)"
    
    # Trova il primo slot libero per quel ruolo nella squadra scelta
    slot_trovato = False
    if ruolo in st.session_state.rose[squadra_acquirente]:
        for idx, slot_val in enumerate(st.session_state.rose[squadra_acquirente][ruolo]):
            if slot_val == "":
                st.session_state.rose[squadra_acquirente][ruolo][idx] = nome_giocatore
                slot_trovato = True
                st.success(f"Assegnato {search_name} a {squadra_acquirente}!")
                break
        if not slot_trovato:
            st.error(f"Tutti gli slot per il ruolo {ruolo} di {squadra_acquirente} sono pieni!")

st.markdown("---")

# --- COSTRUZIONE TABELLONE VISIVO ---
st.subheader("📋 Tabellone Rose")

table_data = []

# Header Portieri
table_data.append(["--- PORTIERI ---"] * len(squadre))
for i in range(SLOT_CONFIG["P"]):
    row = [st.session_state.rose[sq]["P"][i] for sq in squadre]
    table_data.append(row)

# Header Difensori
table_data.append(["--- DIFENSORI ---"] * len(squadre))
for i in range(SLOT_CONFIG["D"]):
    row = [st.session_state.rose[sq]["D"][i] for sq in squadre]
    table_data.append(row)

# Header Centrocampisti
table_data.append(["--- CENTROCAMPISTI ---"] * len(squadre))
for i in range(SLOT_CONFIG["C"]):
    row = [st.session_state.rose[sq]["C"][i] for sq in squadre]
    table_data.append(row)

# Header Attaccanti
table_data.append(["--- ATTACCANTI ---"] * len(squadre))
for i in range(SLOT_CONFIG["A"]):
    row = [st.session_state.rose[sq]["A"][i] for sq in squadre]
    table_data.append(row)

row_labels = (
    ["Sezione P"] + [f"P {i+1}" for i in range(SLOT_CONFIG["P"])] +
    ["Sezione D"] + [f"D {i+1}" for i in range(SLOT_CONFIG["D"])] +
    ["Sezione C"] + [f"C {i+1}" for i in range(SLOT_CONFIG["C"])] +
    ["Sezione A"] + [f"A {i+1}" for i in range(SLOT_CONFIG["A"])]
)

board_df = pd.DataFrame(table_data, index=row_labels, columns=squadre)

st.dataframe(board_df, use_container_width=True)
