import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Tool Fantacalcio - Live Auction Master", page_icon="⚽", layout="wide")

st.title("⚽ Tabellone Asta in Tempo Reale + Master Consulente Diretto")
st.markdown("Consigli tattici secchi, gestione slot, crediti dinamici e indicazioni precise sui ballottaggi per ogni reparto.")

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

# Inizializzazione e recupero persistente da file locale per non perdere i dati
if "rose" not in st.session_state:
    st.session_state.rose = {}
if "crediti" not in st.session_state:
    st.session_state.crediti = {}

if "caricato_da_file" not in st.session_state:
    if os.path.exists("backup_automatico.json"):
        try:
            with open("backup_automatico.json", "r") as f:
                dati = json.load(f)
                st.session_state.rose = dati.get("rose", {})
                st.session_state.crediti = dati.get("crediti", {})
        except:
            pass
    st.session_state.caricato_da_file = True

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

def salva_stato_locale():
    dati_salvataggio = {
        "rose": st.session_state.rose,
        "crediti": st.session_state.crediti
    }
    with open("backup_automatico.json", "w") as f:
        json.dump(dati_salvataggio, f)

for sq_esistente in list(st.session_state.rose.keys()):
    if sq_esistente not in squadre:
        del st.session_state.rose[sq_esistente]
        if sq_esistente in st.session_state.crediti:
            del st.session_state.crediti[sq_esistente]

salva_stato_locale()

# --- PANNELLO CREDITI E ANDAMENTO ASTA NELLA SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.header("💰 Situazione Crediti & Asta")

crediti_totali_lega = sum(st.session_state.crediti.values())
budget_iniziale_totale = num_squadre * budget_iniziale
crediti_spesi_totale = budget_iniziale_totale - crediti_totali_lega
media_crediti_rimasti = crediti_totali_lega / num_squadre if num_squadre > 0 else 0

st.sidebar.markdown(f"**Media crediti residui per squadra:** `{int(media_crediti_rimasti)} cr`")
st.sidebar.markdown(f"**Totale crediti spesi nella lega:** `{crediti_spesi_totale} cr`")
st.sidebar.markdown("---")

for sq in squadre:
    crediti_attuali = st.session_state.crediti.get(sq, budget_iniziale)
    spesi = budget_iniziale - crediti_attuali
    st.sidebar.text(f"{sq}: {crediti_attuali} cr (Spesi: {spesi})")

# --- SEZIONE ASTA / ASSEGNAZIONE + MASTER CONSULENTE ---
st.subheader("🛒 Assegnazione Giocatore & Master Consulente Diretto")
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

# --- MOTORE MASTER DIRETTIVO ESTESO A TUTTI I RUOLI (INCLUSI ATTACCANTI) ---
def master_analisi_diretta(sq_target, nome_gioc, ruolo_gioc, squadra_ita, fvm, prezzo_inserito):
    slot_occupati = sum(1 for g in st.session_state.rose[sq_target][ruolo_gioc] if g != "")
    slot_totali = SLOT_CONFIG[ruolo_gioc]
    slot_rimasti = slot_totali - slot_occupati
    
    LIMITI_MASSIMI_PERCENTUALI = {
        "P": 0.12,
        "D": 0.16,
        "C": 0.25,
        "A": 0.45
    }
    limite_assoluto_crediti = budget_iniziale * LIMITI_MASSIMI_PERCENTUALI.get(ruolo_gioc, 0.20)
    
    consiglio_colore = "info"
    testo_consiglio = []
    
    if slot_rimasti <= 0:
        return f"🚨 **ALT!** {sq_target} ha già chiuso il reparto **{ruolo_gioc}** ({slot_totali}/{slot_totali}). Non puoi prenderlo!", "error"
    
    testo_consiglio.append(f"📋 **Situazione {ruolo_gioc} per {sq_target}:** Hai {slot_rimasti} slot liberi su {slot_totali}.")
    
    # Controllo Overpay
    if prezzo_inserito > limite_assoluto_crediti:
        return (f"🚨 **FOLLIA PURA!** Stai offrendo {prezzo_inserito} crediti per un {ruolo_gioc} ({int((prezzo_inserito/budget_iniziale)*100)}% del budget). "
                f"Prezzo fuori da ogni logica, bloccati subito!"), "warning"

    # Mappa estesa dei ballottaggi (Centrocampo e Attacco)
    mappa_ballottaggi = {
        # Centrocampisti
        "isaksen": "Zaccagni / Pedro / Tchaouna",
        "zaccagni": "Isaksen / Tchaouna",
        "frattesi": "Barella / Mkhitaryan / Zielinski",
        "bove": "Cataldi / Guendouzi / Rovella",
        "colpani": "Maldini / Pessina",
        "fazzini": "Henderson / Zurkowski",
        "ndoye": "Orsolini / Karlsson",
        "pulisic": "Chukwueze / Okafor",
        "leao": "Okafor",
        "yildiz": "Conceicao / Weah",
        "soule": "Dybala / Baldanzi",
        "de ketelaere": "Lookman / Retegui / Samardzic",
        "samardzic": "Ederson / De Roon / Pasalic",
        # Attaccanti
        "simeone": "Lukaku / Raspadori",
        "raspadori": "Lukaku / Simeone",
        "taremi": "Lautaro / Thuram",
        "arnautovic": "Lautaro / Thuram",
        "jovic": "Abraham / Morata",
        "abraham": "Morata / Jovic",
        "morata": "Abraham / Jovic",
        "castellanos": "Dia",
        "dia": "Castellanos",
        "caprari": "Djuric / Mota",
        "mosquera": "Tengstedt / Livramento",
        "lucca": "Davis / Brenner",
        "sanabria": "Zapata / Adams",
        "adams": "Zapata / Sanabria",
        "chwueze": "Pulisic"
    }
    
    rivale_chiave = None
    for k, v in mappa_ballottaggi.items():
        if k in nome_gioc.lower():
            rivale_chiave = v
            break
            
    if rivale_chiave:
        testo_consiglio.append(f"⚔️ **ATTENZIONE BALLOTTAGGIO:** {nome_gioc} si gioca il posto ininterrottamente con **{rivale_chiave}** ({squadra_ita}). **PRENDILO IN COPPIA** con lui per evitare buchi a voto, altrimenti rischi malus continui.")
    else:
        if ruolo_gioc in ["D", "C"] and fvm < 18:
            testo_consiglio.append(f"🔄 **GESTIONE ROTAZIONE:** Giocatore da alternare. Controlla di avere già i titolari fissi coperti prima di prenderlo.")

    soglia_affare = min(fvm * 0.90, limite_assoluto_crediti * 0.6)
    soglia_max_onesta = min(fvm * 1.15, limite_assoluto_crediti * 0.85)

    if prezzo_inserito <= soglia_affare:
        testo_consiglio.append(f"💰 **DA COMPRARE SUBITO:** Pagato {prezzo_inserito} (FVM {fvm}). Affare d'oro per la tua rosa, prendilo al volo.")
        consiglio_colore = "success"
    elif prezzo_inserito <= soglia_max_onesta:
        testo_consiglio.append(f"👍 **PREZZO CORRETTO:** A {prezzo_inserito} crediti ci sta tutto (FVM {fvm}). Acquisto sensato per completare i ranghi.")
        consiglio_colore = "info"
    else:
        testo_consiglio.append(f"⚠️ **STAI SPENDENDO TROPPO:** A {prezzo_inserito} cr stai pagando un sovrapprezzo rispetto al FVM ({fvm}). Fermati se puoi.")
        consiglio_colore = "warning"
        
    return " ".join(testo_consiglio), consiglio_colore

if search_name:
    parere, tipo_box = master_analisi_diretta(
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
                    salva_stato_locale()
                    st.success(f"Assegnato {search_name} a {squadra_acquirente} per {prezzo_pagato} crediti!")
                    break
            if not slot_trovato:
                st.error(f"Tutti gli slot per il ruolo {ruolo} di {squadra_acquirente} sono pieni!")

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
            salva_stato_locale()
            st.success(f"Rimosso {gioc_sel} da {sq_err} e rimborsati {prezzo_estratto} crediti!")
            st.rerun()

st.markdown("---")

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
