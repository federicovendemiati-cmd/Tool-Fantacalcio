import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tool Fantacalcio - Live Auction Master", page_icon="⚽", layout="wide")

st.title("⚽ Tabellone Asta in Tempo Reale + Master Consulente")
st.markdown("Gestione avanzata rose, crediti dinamici, analisi dell'andamento dell'asta e consigli tattici per ogni ruolo.")

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

# --- PANNELLO CREDITI E ANDAMENTO ASTA NELLA SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.header("💰 Situazione Crediti & Asta")

crediti_totali_lega = sum(st.session_state.crediti.values())
budget_iniziale_totale = num_squadre * budget_iniziale
crediti_spesi_totale = budget_iniziale_totale - crediti_totali_lega
media_crediti_rimasti = crediti_totali_lega / num_squadre

st.sidebar.markdown(f"**Media crediti residui per squadra:** `{int(media_crediti_rimasti)} cr`")
st.sidebar.markdown(f"**Totale crediti spesi nella lega:** `{crediti_spesi_totale} cr`")
st.sidebar.markdown("---")

for sq in squadre:
    crediti_attuali = st.session_state.crediti.get(sq, budget_iniziale)
    spesi = budget_iniziale - crediti_attuali
    st.sidebar.text(f"{sq}: {crediti_attuali} cr (Spesi: {spesi})")

# --- SEZIONE ASTA / ASSEGNAZIONE + MASTER CONSULENTE ---
st.subheader("🛒 Assegnazione Giocatore & Master Consulente Tattico")
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

# --- MOTORE MASTER DI ANALISI AVANZATA (RUOLO, ROSA E ANDAMENTO ASTA) ---
def master_analisi_asta(sq_target, nome_gioc, ruolo_gioc, squadra_ita, fvm, prezzo_inserito):
    # Controllo quanti slot liberi ha la squadra in quel ruolo
    slot_occupati = sum(1 for g in st.session_state.rose[sq_target][ruolo_gioc] if g != "")
    slot_totali = SLOT_CONFIG[ruolo_gioc]
    slot_rimasti = slot_totali - slot_occupati
    
    crediti_miei = st.session_state.crediti[sq_target]
    
    # Calcolo soglia d'affare in base all'andamento dell'asta (se la media crediti degli avversari si abbassa, i prezzi calano)
    soglia_affare = fvm * 0.85
    soglia_max = fvm * 1.25
    
    consiglio_colore = "info"
    testo_consiglio = []
    
    # 1. Analisi di Ruolo e Rosa
    if slot_rimasti <= 0:
        return f"🚨 **Attenzione!** {sq_target} ha già completato tutti gli slot per il ruolo **{ruolo_gioc}**! Non puoi prenderlo a meno di svincolare qualcuno.", "error"
    
    testo_consiglio.append(f"📋 **Slot {ruolo_gioc} liberi per {sq_target}:** {slot_rimasti}/{slot_totali}.")
    
    # 2. Analisi Specifiche per Ruolo & Squadra
    portieri_rosa = [g.split(" (")[0] for g in st.session_state.rose[sq_target]["P"] if g != ""]
    if ruolo_gioc == "P":
        squadre_portieri = [df_listone[df_listone["Nome"] == p].iloc[0]["Squadra"] for p in portieri_rosa if not df_listone[df_listone["Nome"] == p].empty]
        if squadra_ita in squadre_portieri:
            testo_consiglio.append(f"🔥 **COPERTURA PORTA:** Hai già il titolare del **{squadra_ita}**! Prenderlo ti blinda la porta al 100%. Consigliatissimo se preso a basso costo.")
        else:
            testo_consiglio.append(f"🧤 **Portiere singolo ({squadra_ita}).** Valuta la rotazione del calendario con i tuoi attuali portieri.")
            
    elif ruolo_gioc == "D":
        if squadra_ita in ["Inter", "Juventus", "Milan", "Atalanta", "Napoli"]:
            testo_consiglio.append(f"🛡️ **Top Difesa ({squadra_ita}):** Ottimale per il modificatore di difesa. Se pagato entro **{int(fvm * 1.15)} crediti** è un affare solido.")
        else:
            testo_consiglio.append(f"⚽ Difensore da bonus o titolare low-cost per completare il reparto.")
            
    elif ruolo_gioc == "C":
        testo_consiglio.append(f"🎯 Centrocampista da modificatore/bonus. Monitora il budget: ti restano {crediti_miei} crediti.")
        
    elif ruolo_gioc == "A":
        if fvm >= 100:
            testo_consiglio.append(f"👑 **TOP ATTACCO:** Giocatore fondamentale. Gestisci bene il budget residuo ({crediti_miei} cr) perché gli slot avanzati pesano molto.")
        else:
            testo_consiglio.append(f"⚡ Scommessa o titolare di provincia per completare il tridente.")

    # 3. Analisi del Prezzo rispetto all'Andamento dell'Asta
    diff = prezzo_inserito - fvm
    if prezzo_inserito <= soglia_affare:
        testo_consiglio.append(f"💰 **GRANDE AFFARE!** Lo stai pagando {prezzo_inserito} rispetto a un FVM di {fvm} (-{abs(int(diff))} cr). Prendi al volo!")
        consiglio_colore = "success"
    elif prezzo_inserito <= soglia_max:
        testo_consiglio.append(f"👍 **Prezzo onesto e in linea** con l'andamento della lega (FVM: {fvm}).")
        consiglio_colore = "info"
    else:
        testo_consiglio.append(f"⚠️ **OVERPAY!** Lo stai pagando troppo rispetto al valore medio (+{int(diff)} cr). Con una media lega di {int(media_crediti_rimasti)} cr residui per squadra, rischi di rimanere corto.")
        consiglio_colore = "warning"
        
    return " ".join(testo_consiglio), consiglio_colore

# Mostra il consiglio dinamico in tempo reale
if search_name:
    parere, tipo_box = master_analisi_asta(
        squadra_acquirente, 
        search_name, 
        selected_player_row['Ruolo'], 
        selected_player_row['Squadra'], 
        float(selected_player_row['FVM']), 
        prezzo_pagato
    )
    
    if tipo_box == "success":
        st.success(f"🤖 **Master Consulente ({squadra_acquirente}):** {parere}")
    elif tipo_box == "warning":
        st.warning(f"🤖 **Master Consulente ({squadra_acquirente}):** {parere}")
    else:
        st.info(f"🤖 **Master Consulente ({squadra_acquirente}):** {parere}")

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
