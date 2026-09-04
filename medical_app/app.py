import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import os

st.set_page_config(
    page_title="Sistema Gestionale Clinico",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = os.path.join(os.path.dirname(__file__), "clinica.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS medici (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            specializzazione TEXT,
            codice_fiscale TEXT UNIQUE,
            telefono TEXT,
            email TEXT,
            data_assunzione DATE,
            ruolo TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS pazienti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            data_nascita DATE,
            sesso TEXT,
            codice_fiscale TEXT UNIQUE,
            telefono TEXT,
            email TEXT,
            indirizzo TEXT,
            citta TEXT,
            gruppo_sanguigno TEXT,
            allergie TEXT,
            patologie_pregresse TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS ammissioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paziente_id INTEGER NOT NULL,
            medico_id INTEGER,
            data_ingresso DATE NOT NULL,
            data_uscita DATE,
            reparto TEXT,
            stanza TEXT,
            motivo_ricovero TEXT,
            stato TEXT DEFAULT 'In corso',
            note TEXT,
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id),
            FOREIGN KEY (medico_id) REFERENCES medici(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS diagnosi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paziente_id INTEGER NOT NULL,
            medico_id INTEGER,
            ammissione_id INTEGER,
            data_diagnosi DATE NOT NULL,
            codice_icd TEXT,
            descrizione TEXT NOT NULL,
            tipo TEXT,
            gravita TEXT,
            note TEXT,
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id),
            FOREIGN KEY (medico_id) REFERENCES medici(id),
            FOREIGN KEY (ammissione_id) REFERENCES ammissioni(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS prognosi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paziente_id INTEGER NOT NULL,
            diagnosi_id INTEGER,
            medico_id INTEGER,
            data_prognosi DATE NOT NULL,
            descrizione TEXT NOT NULL,
            esito_previsto TEXT,
            durata_stimata TEXT,
            note TEXT,
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id),
            FOREIGN KEY (diagnosi_id) REFERENCES diagnosi(id),
            FOREIGN KEY (medico_id) REFERENCES medici(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS terapie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paziente_id INTEGER NOT NULL,
            medico_id INTEGER,
            data_inizio DATE,
            data_fine DATE,
            farmaco_o_trattamento TEXT NOT NULL,
            dosaggio TEXT,
            frequenza TEXT,
            note TEXT,
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id),
            FOREIGN KEY (medico_id) REFERENCES medici(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_pazienti_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM pazienti ORDER BY cognome, nome", conn)
    conn.close()
    return df

def get_medici_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM medici ORDER BY cognome, nome", conn)
    conn.close()
    return df

def get_paziente_options():
    df = get_pazienti_df()
    if df.empty:
        return {}
    return {f"{row['cognome']} {row['nome']} (ID:{row['id']})": row['id'] for _, row in df.iterrows()}

def get_medico_options():
    df = get_medici_df()
    if df.empty:
        return {}
    return {f"{row['cognome']} {row['nome']} - {row['specializzazione'] or 'N/D'} (ID:{row['id']})": row['id'] for _, row in df.iterrows()}

init_db()

st.title("🏥 Sistema Gestionale Clinico")
st.caption("**PROTOTIPO DEMO** – Non utilizzare per dati reali di pazienti.")

st.sidebar.title("Menu")
pagina = st.sidebar.radio(
    "Seleziona sezione",
    [
        "Dashboard",
        "Pazienti",
        "Medici / Operatori",
        "Ammissioni / Degenza",
        "Diagnosi",
        "Prognosi",
        "Terapie",
        "Ricerca / Report"
    ]
)

if pagina == "Dashboard":
    st.header("📊 Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    conn = get_connection()
    n_pazienti = pd.read_sql_query("SELECT COUNT(*) as c FROM pazienti", conn).iloc[0]['c']
    n_medici = pd.read_sql_query("SELECT COUNT(*) as c FROM medici", conn).iloc[0]['c']
    n_amm_in_corso = pd.read_sql_query("SELECT COUNT(*) as c FROM ammissioni WHERE stato = 'In corso'", conn).iloc[0]['c']
    n_diagnosi = pd.read_sql_query("SELECT COUNT(*) as c FROM diagnosi", conn).iloc[0]['c']
    conn.close()
    col1.metric("Pazienti registrati", n_pazienti)
    col2.metric("Medici / Operatori", n_medici)
    col3.metric("Ammissioni in corso", n_amm_in_corso)
    col4.metric("Diagnosi totali", n_diagnosi)
    
    st.subheader("Ultime ammissioni")
    conn = get_connection()
    df_amm = pd.read_sql_query('''
        SELECT a.id, p.cognome || ' ' || p.nome as paziente, 
               m.cognome || ' ' || m.nome as medico,
               a.data_ingresso, a.data_uscita, a.reparto, a.stato
        FROM ammissioni a
        LEFT JOIN pazienti p ON a.paziente_id = p.id
        LEFT JOIN medici m ON a.medico_id = m.id
        ORDER BY a.data_ingresso DESC LIMIT 10
    ''', conn)
    conn.close()
    st.dataframe(df_amm, use_container_width=True)

elif pagina == "Pazienti":
    st.header("👤 Gestione Pazienti")
    tab1, tab2 = st.tabs(["Elenco Pazienti", "Nuovo Paziente"])
    
    with tab1:
        df = get_pazienti_df()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            with st.expander("Elimina paziente"):
                id_del = st.number_input("ID paziente da eliminare", min_value=1, step=1, key="del_paz")
                if st.button("Elimina", key="btn_del_paz"):
                    conn = get_connection()
                    conn.execute("DELETE FROM pazienti WHERE id = ?", (id_del,))
                    conn.commit()
                    conn.close()
                    st.success(f"Paziente {id_del} eliminato.")
                    st.rerun()
        else:
            st.info("Nessun paziente registrato.")
    
    with tab2:
        with st.form("form_paziente"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome *")
                cognome = st.text_input("Cognome *")
                data_nascita = st.date_input("Data di nascita", value=None)
                sesso = st.selectbox("Sesso", ["", "M", "F", "Altro"])
                codice_fiscale = st.text_input("Codice Fiscale")
            with col2:
                telefono = st.text_input("Telefono")
                email = st.text_input("Email")
                indirizzo = st.text_input("Indirizzo")
                citta = st.text_input("Città")
                gruppo_sanguigno = st.selectbox("Gruppo sanguigno", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-"])
            allergie = st.text_area("Allergie")
            patologie = st.text_area("Patologie pregresse")
            note = st.text_area("Note")
            submitted = st.form_submit_button("Salva Paziente")
            if submitted:
                if not nome or not cognome:
                    st.error("Nome e Cognome sono obbligatori.")
                else:
                    try:
                        conn = get_connection()
                        conn.execute('''
                            INSERT INTO pazienti (nome, cognome, data_nascita, sesso, codice_fiscale, telefono, email, indirizzo, citta, gruppo_sanguigno, allergie, patologie_pregresse, note)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (nome, cognome, data_nascita, sesso or None, codice_fiscale or None, telefono or None, email or None, indirizzo or None, citta or None, gruppo_sanguigno or None, allergie or None, patologie or None, note or None))
                        conn.commit()
                        conn.close()
                        st.success("Paziente salvato con successo!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Codice fiscale già presente.")

elif pagina == "Medici / Operatori":
    st.header("👨‍⚕️ Gestione Medici e Operatori")
    tab1, tab2 = st.tabs(["Elenco", "Nuovo Medico/Operatore"])
    
    with tab1:
        df = get_medici_df()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            with st.expander("Elimina medico"):
                id_del = st.number_input("ID da eliminare", min_value=1, step=1, key="del_med")
                if st.button("Elimina", key="btn_del_med"):
                    conn = get_connection()
                    conn.execute("DELETE FROM medici WHERE id = ?", (id_del,))
                    conn.commit()
                    conn.close()
                    st.success("Eliminato.")
                    st.rerun()
        else:
            st.info("Nessun medico registrato.")
    
    with tab2:
        with st.form("form_medico"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome *")
                cognome = st.text_input("Cognome *")
                specializzazione = st.text_input("Specializzazione")
                codice_fiscale = st.text_input("Codice Fiscale")
            with col2:
                telefono = st.text_input("Telefono")
                email = st.text_input("Email")
                data_assunzione = st.date_input("Data assunzione", value=None)
                ruolo = st.selectbox("Ruolo", ["", "Medico", "Infermiere", "Tecnico", "Specialista", "Altro"])
            note = st.text_area("Note")
            if st.form_submit_button("Salva"):
                if not nome or not cognome:
                    st.error("Nome e Cognome obbligatori.")
                else:
                    try:
                        conn = get_connection()
                        conn.execute('''
                            INSERT INTO medici (nome, cognome, specializzazione, codice_fiscale, telefono, email, data_assunzione, ruolo, note)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (nome, cognome, specializzazione or None, codice_fiscale or None, telefono or None, email or None, data_assunzione, ruolo or None, note or None))
                        conn.commit()
                        conn.close()
                        st.success("Medico/Operatore salvato!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Codice fiscale già presente.")

elif pagina == "Ammissioni / Degenza":
    st.header("🛏️ Ammissioni e Degenza")
    tab1, tab2 = st.tabs(["Elenco Ammissioni", "Nuova Ammissione"])
    
    with tab1:
        conn = get_connection()
        df = pd.read_sql_query('''
            SELECT a.*, p.cognome || ' ' || p.nome as paziente, 
                   m.cognome || ' ' || m.nome as medico
            FROM ammissioni a
            LEFT JOIN pazienti p ON a.paziente_id = p.id
            LEFT JOIN medici m ON a.medico_id = m.id
            ORDER BY a.data_ingresso DESC
        ''', conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            with st.expander("Aggiorna data uscita / stato"):
                id_amm = st.number_input("ID Ammissione", min_value=1, step=1)
                nuova_data = st.date_input("Data uscita", value=None)
                nuovo_stato = st.selectbox("Stato", ["In corso", "Dimesso", "Trasferito", "Deceduto"])
                if st.button("Aggiorna"):
                    conn = get_connection()
                    conn.execute("UPDATE ammissioni SET data_uscita = ?, stato = ? WHERE id = ?", (nuova_data, nuovo_stato, id_amm))
                    conn.commit()
                    conn.close()
                    st.success("Aggiornato.")
                    st.rerun()
        else:
            st.info("Nessuna ammissione.")
    
    with tab2:
        paz_opts = get_paziente_options()
        med_opts = get_medico_options()
        if not paz_opts:
            st.warning("Inserisci prima almeno un paziente.")
        else:
            with st.form("form_amm"):
                paziente = st.selectbox("Paziente *", list(paz_opts.keys()))
                medico = st.selectbox("Medico responsabile", [""] + list(med_opts.keys()))
                data_ingresso = st.date_input("Data ingresso *", value=date.today())
                data_uscita = st.date_input("Data uscita (se già dimesso)", value=None)
                reparto = st.text_input("Reparto")
                stanza = st.text_input("Stanza")
                motivo = st.text_area("Motivo ricovero")
                stato = st.selectbox("Stato", ["In corso", "Dimesso", "Trasferito"])
                note = st.text_area("Note")
                if st.form_submit_button("Salva Ammissione"):
                    pid = paz_opts[paziente]
                    mid = med_opts.get(medico) if medico else None
                    conn = get_connection()
                    conn.execute('''
                        INSERT INTO ammissioni (paziente_id, medico_id, data_ingresso, data_uscita, reparto, stanza, motivo_ricovero, stato, note)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (pid, mid, data_ingresso, data_uscita, reparto or None, stanza or None, motivo or None, stato, note or None))
                    conn.commit()
                    conn.close()
                    st.success("Ammissione registrata!")
                    st.rerun()

elif pagina == "Diagnosi":
    st.header("🩺 Diagnosi")
    tab1, tab2 = st.tabs(["Elenco Diagnosi", "Nuova Diagnosi"])
    
    with tab1:
        conn = get_connection()
        df = pd.read_sql_query('''
            SELECT d.*, p.cognome || ' ' || p.nome as paziente,
                   m.cognome || ' ' || m.nome as medico
            FROM diagnosi d
            LEFT JOIN pazienti p ON d.paziente_id = p.id
            LEFT JOIN medici m ON d.medico_id = m.id
            ORDER BY d.data_diagnosi DESC
        ''', conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nessuna diagnosi registrata.")
    
    with tab2:
        paz_opts = get_paziente_options()
        med_opts = get_medico_options()
        if not paz_opts:
            st.warning("Inserisci prima un paziente.")
        else:
            with st.form("form_diag"):
                paziente = st.selectbox("Paziente *", list(paz_opts.keys()))
                medico = st.selectbox("Medico", [""] + list(med_opts.keys()))
                data_diag = st.date_input("Data diagnosi *", value=date.today())
                codice_icd = st.text_input("Codice ICD-10 (opzionale)")
                descrizione = st.text_area("Descrizione diagnosi *")
                tipo = st.selectbox("Tipo", ["", "Principale", "Secondaria", "Sospetta", "Confermata"])
                gravita = st.selectbox("Gravità", ["", "Lieve", "Moderata", "Grave", "Critica"])
                note = st.text_area("Note")
                if st.form_submit_button("Salva Diagnosi"):
                    if not descrizione:
                        st.error("La descrizione è obbligatoria.")
                    else:
                        pid = paz_opts[paziente]
                        mid = med_opts.get(medico) if medico else None
                        conn = get_connection()
                        conn.execute('''
                            INSERT INTO diagnosi (paziente_id, medico_id, data_diagnosi, codice_icd, descrizione, tipo, gravita, note)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (pid, mid, data_diag, codice_icd or None, descrizione, tipo or None, gravita or None, note or None))
                        conn.commit()
                        conn.close()
                        st.success("Diagnosi salvata!")
                        st.rerun()

elif pagina == "Prognosi":
    st.header("📈 Prognosi")
    tab1, tab2 = st.tabs(["Elenco Prognosi", "Nuova Prognosi"])
    
    with tab1:
        conn = get_connection()
        df = pd.read_sql_query('''
            SELECT pr.*, p.cognome || ' ' || p.nome as paziente,
                   m.cognome || ' ' || m.nome as medico
            FROM prognosi pr
            LEFT JOIN pazienti p ON pr.paziente_id = p.id
            LEFT JOIN medici m ON pr.medico_id = m.id
            ORDER BY pr.data_prognosi DESC
        ''', conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nessuna prognosi registrata.")
    
    with tab2:
        paz_opts = get_paziente_options()
        med_opts = get_medico_options()
        if not paz_opts:
            st.warning("Inserisci prima un paziente.")
        else:
            with st.form("form_prog"):
                paziente = st.selectbox("Paziente *", list(paz_opts.keys()))
                medico = st.selectbox("Medico", [""] + list(med_opts.keys()))
                data_prog = st.date_input("Data prognosi *", value=date.today())
                descrizione = st.text_area("Descrizione prognosi *")
                esito = st.selectbox("Esito previsto", ["", "Favorevole", "Riservato", "Incerto", "Infustato"])
                durata = st.text_input("Durata stimata (es. 15 giorni)")
                note = st.text_area("Note")
                if st.form_submit_button("Salva Prognosi"):
                    if not descrizione:
                        st.error("Descrizione obbligatoria.")
                    else:
                        pid = paz_opts[paziente]
                        mid = med_opts.get(medico) if medico else None
                        conn = get_connection()
                        conn.execute('''
                            INSERT INTO prognosi (paziente_id, medico_id, data_prognosi, descrizione, esito_previsto, durata_stimata, note)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (pid, mid, data_prog, descrizione, esito or None, durata or None, note or None))
                        conn.commit()
                        conn.close()
                        st.success("Prognosi salvata!")
                        st.rerun()

elif pagina == "Terapie":
    st.header("💊 Terapie e Trattamenti")
    tab1, tab2 = st.tabs(["Elenco", "Nuova Terapia"])
    
    with tab1:
        conn = get_connection()
        df = pd.read_sql_query('''
            SELECT t.*, p.cognome || ' ' || p.nome as paziente,
                   m.cognome || ' ' || m.nome as medico
            FROM terapie t
            LEFT JOIN pazienti p ON t.paziente_id = p.id
            LEFT JOIN medici m ON t.medico_id = m.id
            ORDER BY t.data_inizio DESC
        ''', conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nessuna terapia registrata.")
    
    with tab2:
        paz_opts = get_paziente_options()
        med_opts = get_medico_options()
        if not paz_opts:
            st.warning("Inserisci prima un paziente.")
        else:
            with st.form("form_ter"):
                paziente = st.selectbox("Paziente *", list(paz_opts.keys()))
                medico = st.selectbox("Medico", [""] + list(med_opts.keys()))
                data_inizio = st.date_input("Data inizio", value=date.today())
                data_fine = st.date_input("Data fine", value=None)
                trattamento = st.text_input("Farmaco / Trattamento *")
                dosaggio = st.text_input("Dosaggio")
                frequenza = st.text_input("Frequenza")
                note = st.text_area("Note")
                if st.form_submit_button("Salva Terapia"):
                    if not trattamento:
                        st.error("Campo trattamento obbligatorio.")
                    else:
                        pid = paz_opts[paziente]
                        mid = med_opts.get(medico) if medico else None
                        conn = get_connection()
                        conn.execute('''
                            INSERT INTO terapie (paziente_id, medico_id, data_inizio, data_fine, farmaco_o_trattamento, dosaggio, frequenza, note)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (pid, mid, data_inizio, data_fine, trattamento, dosaggio or None, frequenza or None, note or None))
                        conn.commit()
                        conn.close()
                        st.success("Terapia salvata!")
                        st.rerun()

elif pagina == "Ricerca / Report":
    st.header("🔍 Ricerca e Report")
    ricerca = st.text_input("Cerca paziente per nome, cognome o codice fiscale")
    if ricerca:
        conn = get_connection()
        df = pd.read_sql_query('''
            SELECT * FROM pazienti 
            WHERE nome LIKE ? OR cognome LIKE ? OR codice_fiscale LIKE ?
        ''', conn, params=(f"%{ricerca}%", f"%{ricerca}%", f"%{ricerca}%"))
        conn.close()
        if not df.empty:
            st.subheader("Pazienti trovati")
            st.dataframe(df, use_container_width=True)
            paz_id = st.selectbox("Seleziona paziente per cartella clinica completa", df['id'].tolist())
            if paz_id:
                conn = get_connection()
                st.markdown("### Dati anagrafici")
                st.dataframe(pd.read_sql_query("SELECT * FROM pazienti WHERE id = ?", conn, params=(paz_id,)))
                st.markdown("### Ammissioni")
                st.dataframe(pd.read_sql_query("SELECT * FROM ammissioni WHERE paziente_id = ?", conn, params=(paz_id,)))
                st.markdown("### Diagnosi")
                st.dataframe(pd.read_sql_query("SELECT * FROM diagnosi WHERE paziente_id = ?", conn, params=(paz_id,)))
                st.markdown("### Prognosi")
                st.dataframe(pd.read_sql_query("SELECT * FROM prognosi WHERE paziente_id = ?", conn, params=(paz_id,)))
                st.markdown("### Terapie")
                st.dataframe(pd.read_sql_query("SELECT * FROM terapie WHERE paziente_id = ?", conn, params=(paz_id,)))
                conn.close()
        else:
            st.warning("Nessun risultato.")

st.markdown("---")
st.caption("Sistema Gestionale Clinico – Prototipo")
