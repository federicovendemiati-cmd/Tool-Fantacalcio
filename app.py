# --- MOTORE MASTER DIRETTIVO CON CONTROLLO GERARCHIE E CONCORRENZA ---
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

    # Controllo specifico gerarchie / chiusura reparto nelle big (es. Bonny all'Inter, riserve intoccabili)
    profili_riserva_pesante = ["bonny", "taremi", "arnautovic", "jovic", "simeone", "raspadori", "correa"]
    if any(p in nome_gioc.lower() for p in profili_riserva_pesante):
        testo_consiglio.append(f"⚠️ **ATTENZIONE GERARCHIE:** {nome_gioc} è chiuso da giocatori molto più titolati e rischia di fare panchina fissa con pochissimi voti utili. Valuta se vale la pena occupare uno slot con un profilo a così alto rischio minutaggio.")
        consiglio_colore = "warning"

    # Mappa estesa dei ballottaggi classici
    mappa_ballottaggi = {
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
        "castellanos": "Dia",
        "dia": "Castellanos",
        "abraham": "Morata / Jovic",
        "morata": "Abraham"
    }
    
    rivale_chiave = None
    for k, v in mappa_ballottaggi.items():
        if k in nome_gioc.lower():
            rivale_chiave = v
            break
            
    if rivale_chiave:
        testo_consiglio.append(f"⚔️ **BALLOTTAGGIO APERTO:** Si gioca il posto con **{rivale_chiave}** ({squadra_ita}). **PRENDILO IN COPPIA** per coprire i buchi.")

    soglia_affare = min(fvm * 0.90, limite_assoluto_crediti * 0.6)
    soglia_max_onesta = min(fvm * 1.15, limite_assoluto_crediti * 0.85)

    if prezzo_inserito <= soglia_affare and not any(p in nome_gioc.lower() for p in profili_riserva_pesante):
        testo_consiglio.append(f"💰 **DA COMPRARE SUBITO:** Pagato {prezzo_inserito} (FVM {fvm}). Affare d'oro.")
        consiglio_colore = "success"
    elif prezzo_inserito <= soglia_max_onesta:
        testo_consiglio.append(f"👍 **PREZZO CORRETTO:** A {prezzo_inserito} crediti ci sta (FVM {fvm}).")
        if consiglio_colore != "warning":
            consiglio_colore = "info"
    else:
        testo_consiglio.append(f"⚠️ **STAI SPENDENDO TROPPO:** A {prezzo_inserito} cr stai pagando un sovrapprezzo (FVM {fvm}).")
        consiglio_colore = "warning"
        
    return " ".join(testo_consiglio), consiglio_colore
