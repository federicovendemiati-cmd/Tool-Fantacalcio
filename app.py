import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="Tool Fantacalcio - Live Auction con IA", page_icon="⚽", layout="wide")

st.title("⚽ Tabellone Asta in Tempo Reale + Consulente IA")
st.markdown("Gestione rose, crediti, assegnazione automatica e consigli strategici in tempo reale.")

# Configurazione automatica della chiave API dai Secrets di Streamlit
ai_attiva = False
gemini_api_key = None

if "GEMINI_API_KEY" in st.secrets:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    try:
        genai.configure(api_key=gemini_api_key)
        ai_model = genai.GenerativeModel('gemini-3.6-flash')
        ai_attiva = True
    except Exception as e:
        st.sidebar.error(f"Errore configurazione API: {e}")

# Caricamento del listone con cache
@st.cache_data
def load_data():
    try:
        return pd.read_csv("giocatori.csv")
    except:
        return pd.DataFrame(columns=["Ruolo", "Nome", "Squadra", "FVM", "Prezzo"])

df_listone = load_data()

# Configurazione Dinamica Numero Partecipanti nella Sidebar
st.sidebar.header("⚙️ Configurazione Lega")
num_squadre = st.sidebar.slider("Numero di partecipanti", min_value=6, max_value=12, value=8)
budget_iniziale = st.sidebar.number_input("Budget Iniziale per Squadra", value=500, step=50)

default_names = ["Fede", "Riky", "Gio", "Penno", "Ale", "Aldo", "Margy", "Lupo", "Mago", "Kikko", "Bero", "Dandi"]
squadre = []
for i in range(num_squadre):
    nome_def = default_names[i] if i < len(default_names) else f"Squadra {i+1}"
    s = st.sidebar.text_input(f"Squadra {i+1}", value=nome_def, key=f"sq_{i}")
    squadre.append(s)

# Struttura slot per ruolo
SLOT_CONFIG = {
    "P": 3,
    "D": 8,
    "C": 8,
    "A": 6
}

# Inizializzazione sicura dello stato nel session_state
if "rose" not in st.session_state:
    st.session_state.rose = {}
if "crediti" not in st.session_state:
    st.session_state.crediti = {}

for sq in squadre:
    if sq not in st.session_state.rose:
        st.session_state.rose[sq] = {
            "P": ["" for _ in range(SLOT_CONFIG["P"])],
            "D": ["" for _ in range(SLOT_CONFIG["D"])],
            "C": ["" for _ in range(SLOT_CONFIG["C"])],
            "A": ["" for _ in range(SLOT_CONFIG["A"])]
        }
    if sq not in st.session_state.crediti:
        st.session_state.crediti[sq] = budget_iniziale

# Pulizia delle squadre rimosse dallo stato se si riduce il numero
for sq_esistente in list(st.session_state.rose.keys()):
    if sq_esistente not in squadre:
        del st.session_state.rose[sq_esistente]
        if sq_esistente in st.session_state.crediti:
            del st.session_state.crediti[sq_esistente]

# --- PANNELLO CREDITI RESIDUI NELLA SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.header("💰 Crediti Residui")
for sq in squadre:
    crediti_attuali = st.session_state.crediti.get(sq, budget_iniziale)
    spesi = budget_iniziale - crediti_attuali
    st.sidebar.text(f"{sq}: {crediti_attuali} cr (Spesi: {spesi})")

# --- SEZIONE ASTA / ASSEGNAZIONE + CONSIGLI IA ---
st.subheader("🛒 Assegnazione Giocatore & Consulente IA")
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
    st.text("") 
    st.text("")
    assegna_btn = st.button("Assegna Giocatore", type="primary")

# Funzione in cache per velocizzare la risposta dell'IA
@st.cache_data(show_spinner=False)
def get_ai_advice(api_key, p_name, ruolo, squadra_ita, fvm, prezzo_cons, sq_acq, p_pagato, crediti_rim):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.6-flash')
    prompt = (
        f"Fantacalcio: {p_name} ({ruolo}, {squadra_ita}). "
        f"FVM {fvm}, Prezzo guida {prezzo_cons}. "
        f"Offerta: {p_pagato} cr da {sq_acq} (ha {crediti_rim} cr residui). "
        f"In 2 righe secche: affare o overpay? Consiglio rapido."
    )
    return model.generate_content(prompt).text

# Mostra il consiglio in automatico non appena selezioni il giocatore
if search_name:
    if ai_attiva:
        with st.spinner("⚡ IA in ascolto..."):
            try:
                crediti_rimasti_acquirente = st.session_state.crediti[squadra_acquirente]
                consiglio = get_ai_advice(
                    gemini_api_key, 
                    search_name, 
                    selected_player_row['Ruolo'], 
                    selected_player_row['Squadra'], 
                    selected_player_row['FVM'], 
                    selected_player_row['Prezzo'], 
                    squadra_acquirente, 
                    prezzo_pagato, 
                    crediti_rimasti_acquirente
                )
                st.info(f"🤖 **Parere Flash IA:** {consiglio}")
            except Exception as e:
                st.error(f"Errore IA: {e}")
    else:
        st.warning("⚠️ Chiave API non trovata nei secrets di Streamlit.")

if assegna_btn and search_name:
    ruolo = selected_player_row['Ruolo']
    nome_giocatore = f"{search_name} ({prezzo_pagato} cr)"
    
    if st.session_state.crediti[squadra_acquirente] < prezzo_pagato:
        st.error(f"{squadra_acquirente} non ha abbastanza crediti residui!")
    else:
        slot_trovato = False
        if ruolo in st.session_state.rose[squadra_acquirente]:
            for idx, slot_val in enumerate(st.session_state.rose[squadra_acquirente][ruolo]):
                if slot_val == "":
                    st.session_state.rose[squadra_acquirente][ruolo][idx] = nome_giocatore
                    st.session_state.crediti[squadra_acquirente] -= prezzo_pagato
                    slot_trovato = True
                    st.success(f"Assegnato {search_name} a {squadra_acquirente} per {prezzo_pagato} crediti!")
                    break
            if not slot_trovato:
                st.error(f"Tutti gli slot per il ruolo {ruolo} di {squadra_acquirente} sono pieni!")

# --- OPZIONE DI CORREZIONE / RIMOZIONE ACQUISTO ERRORE ---
with st.expander("🛠️ Correggi / Rimuovi un giocatore assegnato per errore"):
    sq_err = st.selectbox("Seleziona Squadra", options=squadre, key="err_sq")
    ruolo_err = st.selectbox("Seleziona Ruolo", options=["P", "D", "C", "A"], key="err_ruolo")
    
    gioccorrenti = [g for g in st.session_state.rose[sq_err][ruolo_err] if g != ""]
    gioc_sel = st.selectbox("Seleziona giocatore da rimuovere", options=[""] + gioccorrenti, key="err_gioc")
    
    if st.button("Rimuovi e Rimborsa Crediti"):
        if gioc_sel:
            try:
                prezzo_estratto = int(gioc_sel.split("(")[1].split(" ")[0])
            except:
                prezzo_estratto = 0
            
            idx_to_clear = st.session_state.rose[sq_err][ruolo_err].index(gioc_sel)
            st.session_state.rose[sq_err][ruolo_err][idx_to_clear] = ""
            st.session_state.crediti[sq_err] += prezzo_estratto
            st.success(f"Rimosso {gioc_sel} da {sq_err} e rimborsati {prezzo_estratto} crediti!")
            st.rerun()

st.markdown("---")

# --- COSTRUZIONE TABELLONE VISIVO ---
st.subheader("📋 Tabellone Rose")

table_data = []

table_data.append(["--- PORTIERI ---"] * len(squadre))
for i in range(SLOT_CONFIG["P"]):
    row = [st.session_state.rose[sq]["P"][i] for sq in squadre]
    table_data.append(row)

table_data.append(["--- DIFENSORI ---"] * len(squadre))
for i in range(SLOT_CONFIG["D"]):
    row = [st.session_state.rose[sq]["D"][i] for sq in squadre]
    table_data.append(row)

table_data.append(["--- CENTROCAMPISTI ---"] * len(squadre))
for i in range(SLOT_CONFIG["C"]):
    row = [st.session_state.rose[sq]["C"][i] for sq in squadre]
    table_data.append(row)

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
