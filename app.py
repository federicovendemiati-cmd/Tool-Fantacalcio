import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="Tool Fantacalcio - Live Auction con IA", page_icon="⚽", layout="wide")

st.title("⚽ Tabellone Asta in Tempo Reale + Consulente IA")
st.markdown("Gestione rose, crediti, assegnazione automatica e consigli strategici in tempo reale.")

# Configurazione API IA nella Sidebar
st.sidebar.header("🤖 Configurazione IA")
gemini_api_key = st.sidebar.text_input("Inserisci Gemini API Key", type="password", help="Incolla qui la tua chiave API di Google Gemini.")

ai_attiva = False
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        # Usiamo il modello standard gemini-1.5-flash
        ai_model = genai.GenerativeModel('gemini-1.5-flash')
        ai_attiva = True
    except Exception as e:
        st.sidebar.error(f"Errore configurazione API: {e}")

# Caricamento del listone
@st.cache_data
def load_data():
    try:
        return pd.read_csv("giocatori.csv")
    except:
        return pd.DataFrame(columns=["Ruolo", "Nome", "Squadra", "FVM", "Prezzo"])

df_listone = load_data()

# Configurazione Dinamica Numero Partecipanti nella Sidebar
st.sidebar.markdown("---")
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

# Box Consigli IA in tempo reale per il giocatore selezionato
if search_name:
    with st.expander("🤖 Analisi e Consiglio IA su questo Giocatore", expanded=True):
        if ai_attiva:
            with st.spinner("L'IA sta analizzando il giocatore e la situazione della lega..."):
                crediti_rimasti_acquirente = st.session_state.crediti[squadra_acquirente]
                prompt = (
                    f"Sei un esperto di Fantacalcio italiano. Stiamo facendo l'asta. "
                    f"Il giocatore selezionato è {search_name}, Ruolo: {selected_player_row['Ruolo']}, "
                    f"Squadra Serie A: {selected_player_row['Squadra']}, FVM: {selected_player_row['FVM']}, "
                    f"Prezzo guida consigliato: {selected_player_row['Prezzo']}. "
                    f"La squadra che lo sta acquistando ({squadra_acquirente}) ha ancora {crediti_rimasti_acquirente} crediti su {budget_iniziale} iniziali. "
                    f"Il prezzo inserito per l'asta è {prezzo_pagato} crediti. "
                    f"Fai un'analisi breve e pungente (massimo 3-4 righe): conviene prenderlo a questo prezzo? È un affare o un overpay? Che consigli dai a {squadra_acquirente}?"
                )
                try:
                    response = ai_model.generate_content(prompt)
                    st.success(response.text)
                except Exception as e:
                    st.error(f"Errore durante la generazione della risposta IA: {e}")
        else:
            st.info("💡 Inserisci la tua chiave API di Gemini nella barra laterale per sbloccare l'analisi e i consigli istantanei dell'IA.")

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
