import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import os

# ============================================================
# CONFIGURAZIONE
# ============================================================

st.set_page_config(
    page_title="Sistema Gestionale Clinico",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = os.path.join(os.path.dirname(__file__), "clinica.db")


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id) ON DELETE CASCADE,
            FOREIGN KEY (medico_id) REFERENCES medici(id) ON DELETE SET NULL
        )
    """)

    c.execute("""
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
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id) ON DELETE CASCADE,
            FOREIGN KEY (medico_id) REFERENCES medici(id) ON DELETE SET NULL,
            FOREIGN KEY (ammissione_id) REFERENCES ammissioni(id) ON DELETE SET NULL
        )
    """)

    c.execute("""
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
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id) ON DELETE CASCADE,
            FOREIGN KEY (diagnosi_id) REFERENCES diagnosi(id) ON DELETE SET NULL,
            FOREIGN KEY (medico_id) REFERENCES medici(id) ON DELETE SET NULL
        )
    """)

    c.execute("""
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
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id) ON DELETE CASCADE,
            FOREIGN KEY (medico_id) REFERENCES medici(id) ON DELETE SET NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ============================================================
# FUNZIONI UTILI
# ============================================================

def query_df(query, params=()):
    conn = get_connection()
    try:
        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()


def execute_query(query, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_pazienti():
    return query_df("""
        SELECT *
        FROM pazienti
        ORDER BY cognome COLLATE NOCASE, nome COLLATE NOCASE
    """)


def get_medici():
    return query_df("""
        SELECT *
        FROM medici
        ORDER BY cognome COLLATE NOCASE, nome COLLATE NOCASE
    """)


def get_paziente_options():
    df = get_pazienti()

    if df.empty:
        return {}

    return {
        f"{row['cognome']} {row['nome']} — ID {row['id']}":
        int(row["id"])
        for _, row in df.iterrows()
    }


def get_medico_options():
    df = get_medici()

    if df.empty:
        return {}

    return {
        f"{row['cognome']} {row['nome']} — {row['specializzazione'] or 'Nessuna specializzazione'}":
        int(row["id"])
        for _, row in df.iterrows()
    }


def format_date(value):
    if not value or pd.isna(value):
        return "—"

    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return str(value)


# ============================================================
# HEADER
# ============================================================

st.title("🏥 Sistema Gestionale Clinico")
st.caption("Gestione pazienti, personale, ricoveri e documentazione clinica")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Navigazione")

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
        "Ricerca / Cartelle"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if pagina == "Dashboard":

    st.header("📊 Dashboard")

    pazienti = query_df("SELECT COUNT(*) AS totale FROM pazienti").iloc[0]["totale"]
    medici = query_df("SELECT COUNT(*) AS totale FROM medici").iloc[0]["totale"]
    ricoveri = query_df("""
        SELECT COUNT(*) AS totale
        FROM ammissioni
        WHERE stato = 'In corso'
    """).iloc[0]["totale"]
    diagnosi = query_df("SELECT COUNT(*) AS totale FROM diagnosi").iloc[0]["totale"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👤 Pazienti", int(pazienti))
    col2.metric("👨‍⚕️ Medici / Operatori", int(medici))
    col3.metric("🛏️ Ricoveri in corso", int(ricoveri))
    col4.metric("🩺 Diagnosi", int(diagnosi))

    st.divider()

    st.subheader("Ultime ammissioni")

    df = query_df("""
        SELECT
            a.id AS ID,
            p.cognome || ' ' || p.nome AS Paziente,
            m.cognome || ' ' || m.nome AS Medico,
            a.data_ingresso AS "Data ingresso",
            a.data_uscita AS "Data uscita",
            a.reparto AS Reparto,
            a.stanza AS Stanza,
            a.stato AS Stato
        FROM ammissioni a
        LEFT JOIN pazienti p ON a.paziente_id = p.id
        LEFT JOIN medici m ON a.medico_id = m.id
        ORDER BY a.data_ingresso DESC
        LIMIT 10
    """)

    if df.empty:
        st.info("Non sono presenti ammissioni.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================
# PAZIENTI
# ============================================================

elif pagina == "Pazienti":

    st.header("👤 Gestione Pazienti")

    tab_elenco, tab_nuovo, tab_modifica = st.tabs(
        ["📋 Elenco pazienti", "➕ Nuovo paziente", "✏️ Modifica paziente"]
    )

    # --------------------------------------------------------
    # ELENCO
    # --------------------------------------------------------

    with tab_elenco:

        df = get_pazienti()

        if df.empty:
            st.info("Nessun paziente registrato.")
        else:

            ricerca = st.text_input(
                "🔎 Cerca paziente",
                placeholder="Nome, cognome o codice fiscale..."
            )

            if ricerca:
                mask = (
                    df["nome"].fillna("").str.contains(ricerca, case=False, na=False)
                    |
                    df["cognome"].fillna("").str.contains(ricerca, case=False, na=False)
                    |
                    df["codice_fiscale"].fillna("").str.contains(ricerca, case=False, na=False)
                )

                df = df[mask]

            colonne = [
                "id",
                "nome",
                "cognome",
                "data_nascita",
                "sesso",
                "codice_fiscale",
                "telefono",
                "citta"
            ]

            colonne = [c for c in colonne if c in df.columns]

            st.dataframe(
                df[colonne],
                use_container_width=True,
                hide_index=True
            )

            st.caption(f"Pazienti visualizzati: {len(df)}")

    # --------------------------------------------------------
    # NUOVO PAZIENTE
    # --------------------------------------------------------

    with tab_nuovo:

        st.subheader("Registrazione nuovo paziente")

        with st.form("nuovo_paziente_form", clear_on_submit=True):

            col1, col2 = st.columns(2)

            with col1:

                nome = st.text_input("Nome *")
                cognome = st.text_input("Cognome *")

                data_nascita = st.date_input(
                    "Data di nascita",
                    value=date.today(),
                    format="DD/MM/YYYY"
                )

                sesso = st.selectbox(
                    "Sesso",
                    ["Non specificato", "M", "F", "Altro"]
                )

                codice_fiscale = st.text_input(
                    "Codice fiscale"
                )

            with col2:

                telefono = st.text_input("Telefono")
                email = st.text_input("Email")
                indirizzo = st.text_input("Indirizzo")
                citta = st.text_input("Città")

                gruppo_sanguigno = st.selectbox(
                    "Gruppo sanguigno",
                    [
                        "Non specificato",
                        "A+",
                        "A-",
                        "B+",
                        "B-",
                        "AB+",
                        "AB-",
                        "0+",
                        "0-"
                    ]
                )

            st.subheader("Informazioni cliniche")

            allergie = st.text_area(
                "Allergie",
                placeholder="Indicare eventuali allergie conosciute..."
            )

            patologie = st.text_area(
                "Patologie pregresse",
                placeholder="Indicare patologie o condizioni cliniche rilevanti..."
            )

            note = st.text_area("Note")

            salva = st.form_submit_button(
                "💾 Salva nuovo paziente",
                use_container_width=True
            )

        if salva:

            nome = nome.strip()
            cognome = cognome.strip()

            if not nome or not cognome:
                st.error("Nome e cognome sono obbligatori.")

            else:

                try:

                    execute_query(
                        """
                        INSERT INTO pazienti (
                            nome,
                            cognome,
                            data_nascita,
                            sesso,
                            codice_fiscale,
                            telefono,
                            email,
                            indirizzo,
                            citta,
                            gruppo_sanguigno,
                            allergie,
                            patologie_pregresse,
                            note
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            nome,
                            cognome,
                            data_nascita.isoformat(),
                            None if sesso == "Non specificato" else sesso,
                            codice_fiscale.strip().upper() or None,
                            telefono.strip() or None,
                            email.strip() or None,
                            indirizzo.strip() or None,
                            citta.strip() or None,
                            None if gruppo_sanguigno == "Non specificato" else gruppo_sanguigno,
                            allergie.strip() or None,
                            patologie.strip() or None,
                            note.strip() or None
                        )
                    )

                    st.success(
                        f"✅ Paziente {nome} {cognome} registrato correttamente."
                    )

                    st.rerun()

                except sqlite3.IntegrityError as e:

                    if "codice_fiscale" in str(e):
                        st.error(
                            "Esiste già un paziente con questo codice fiscale."
                        )
                    else:
                        st.error(f"Errore durante il salvataggio: {e}")

    # --------------------------------------------------------
    # MODIFICA PAZIENTE
    # --------------------------------------------------------

    with tab_modifica:

        pazienti = get_pazienti()

        if pazienti.empty:

            st.info("Non ci sono pazienti da modificare.")

        else:

            options = {
                f"{r['cognome']} {r['nome']} — ID {r['id']}":
                int(r["id"])
                for _, r in pazienti.iterrows()
            }

            scelta = st.selectbox(
                "Seleziona paziente",
                list(options.keys())
            )

            paziente_id = options[scelta]

            p = query_df(
                "SELECT * FROM pazienti WHERE id = ?",
                (paziente_id,)
            ).iloc[0]

            with st.form("modifica_paziente_form"):

                col1, col2 = st.columns(2)

                with col1:

                    nome_m = st.text_input(
                        "Nome *",
                        value=p["nome"] or ""
                    )

                    cognome_m = st.text_input(
                        "Cognome *",
                        value=p["cognome"] or ""
                    )

                    try:
                        data_default = datetime.strptime(
                            str(p["data_nascita"])[:10],
                            "%Y-%m-%d"
                        ).date()
                    except Exception:
                        data_default = date.today()

                    data_nascita_m = st.date_input(
                        "Data di nascita",
                        value=data_default,
                        format="DD/MM/YYYY"
                    )

                    sesso_valori = [
                        "Non specificato",
                        "M",
                        "F",
                        "Altro"
                    ]

                    sesso_attuale = p["sesso"] or "Non specificato"

                    sesso_m = st.selectbox(
                        "Sesso",
                        sesso_valori,
                        index=(
                            sesso_valori.index(sesso_attuale)
                            if sesso_attuale in sesso_valori
                            else 0
                        )
                    )

                    cf_m = st.text_input(
                        "Codice fiscale",
                        value=p["codice_fiscale"] or ""
                    )

                with col2:

                    telefono_m = st.text_input(
                        "Telefono",
                        value=p["telefono"] or ""
                    )

                    email_m = st.text_input(
                        "Email",
                        value=p["email"] or ""
                    )

                    indirizzo_m = st.text_input(
                        "Indirizzo",
                        value=p["indirizzo"] or ""
                    )

                    citta_m = st.text_input(
                        "Città",
                        value=p["citta"] or ""
                    )

                    gruppi = [
                        "Non specificato",
                        "A+",
                        "A-",
                        "B+",
                        "B-",
                        "AB+",
                        "AB-",
                        "0+",
                        "0-"
                    ]

                    gruppo_attuale = p["gruppo_sanguigno"] or "Non specificato"

                    gruppo_m = st.selectbox(
                        "Gruppo sanguigno",
                        gruppi,
                        index=(
                            gruppi.index(gruppo_attuale)
                            if gruppo_attuale in gruppi
                            else 0
                        )
                    )

                allergie_m = st.text_area(
                    "Allergie",
                    value=p["allergie"] or ""
                )

                patologie_m = st.text_area(
                    "Patologie pregresse",
                    value=p["patologie_pregresse"] or ""
                )

                note_m = st.text_area(
                    "Note",
                    value=p["note"] or ""
                )

                aggiorna = st.form_submit_button(
                    "💾 Salva modifiche",
                    use_container_width=True
                )

            if aggiorna:

                if not nome_m.strip() or not cognome_m.strip():

                    st.error("Nome e cognome sono obbligatori.")

                else:

                    try:

                        execute_query(
                            """
                            UPDATE pazienti
                            SET
                                nome = ?,
                                cognome = ?,
                                data_nascita = ?,
                                sesso = ?,
                                codice_fiscale = ?,
                                telefono = ?,
                                email = ?,
                                indirizzo = ?,
                                citta = ?,
                                gruppo_sanguigno = ?,
                                allergie = ?,
                                patologie_pregresse = ?,
                                note = ?
                            WHERE id = ?
                            """,
                            (
                                nome_m.strip(),
                                cognome_m.strip(),
                                data_nascita_m.isoformat(),
                                None if sesso_m == "Non specificato" else sesso_m,
                                cf_m.strip().upper() or None,
                                telefono_m.strip() or None,
                                email_m.strip() or None,
                                indirizzo_m.strip() or None,
                                citta_m.strip() or None,
                                None if gruppo_m == "Non specificato" else gruppo_m,
                                allergie_m.strip() or None,
                                patologie_m.strip() or None,
                                note_m.strip() or None,
                                paziente_id
                            )
                        )

                        st.success("✅ Dati del paziente aggiornati.")
                        st.rerun()

                    except sqlite3.IntegrityError:

                        st.error(
                            "Il codice fiscale inserito appartiene già a un altro paziente."
                        )

            st.divider()

            with st.expander("⚠️ Elimina definitivamente questo paziente"):

                st.warning(
                    "L'eliminazione rimuoverà anche le informazioni cliniche collegate."
                )

                conferma = st.checkbox(
                    "Confermo di voler eliminare questo paziente."
                )

                if st.button(
                    "Elimina paziente",
                    type="secondary"
                ):

                    if not conferma:

                        st.error(
                            "Conferma l'eliminazione prima di procedere."
                        )

                    else:

                        execute_query(
                            "DELETE FROM pazienti WHERE id = ?",
                            (paziente_id,)
                        )

                        st.success("Paziente eliminato.")
                        st.rerun()


# ============================================================
# MEDICI / OPERATORI
# ============================================================

elif pagina == "Medici / Operatori":

    st.header("👨‍⚕️ Medici e Operatori")

    tab1, tab2 = st.tabs(
        ["📋 Elenco", "➕ Nuovo medico / operatore"]
    )

    with tab1:

        df = get_medici()

        if df.empty:

            st.info("Nessun medico o operatore registrato.")

        else:

            colonne = [
                "id",
                "nome",
                "cognome",
                "specializzazione",
                "ruolo",
                "telefono",
                "email"
            ]

            st.dataframe(
                df[colonne],
                use_container_width=True,
                hide_index=True
            )

    with tab2:

        with st.form("nuovo_medico"):

            col1, col2 = st.columns(2)

            with col1:

                nome = st.text_input("Nome *")
                cognome = st.text_input("Cognome *")
                specializzazione = st.text_input("Specializzazione")
                codice_fiscale = st.text_input("Codice fiscale")

            with col2:

                telefono = st.text_input("Telefono")
                email = st.text_input("Email")

                data_assunzione = st.date_input(
                    "Data assunzione",
                    value=date.today(),
                    format="DD/MM/YYYY"
                )

                ruolo = st.selectbox(
                    "Ruolo",
                    [
                        "Non specificato",
                        "Medico",
                        "Infermiere",
                        "Tecnico",
                        "Specialista",
                        "Altro"
                    ]
                )

            note = st.text_area("Note")

            salva = st.form_submit_button(
                "💾 Salva",
                use_container_width=True
            )

        if salva:

            if not nome.strip() or not cognome.strip():

                st.error("Nome e cognome sono obbligatori.")

            else:

                try:

                    execute_query(
                        """
                        INSERT INTO medici (
                            nome,
                            cognome,
                            specializzazione,
                            codice_fiscale,
                            telefono,
                            email,
                            data_assunzione,
                            ruolo,
                            note
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            nome.strip(),
                            cognome.strip(),
                            specializzazione.strip() or None,
                            codice_fiscale.strip().upper() or None,
                            telefono.strip() or None,
                            email.strip() or None,
                            data_assunzione.isoformat(),
                            None if ruolo == "Non specificato" else ruolo,
                            note.strip() or None
                        )
                    )

                    st.success("Medico / operatore salvato.")
                    st.rerun()

                except sqlite3.IntegrityError:

                    st.error("Codice fiscale già presente.")


# ============================================================
# AMMISSIONI
# ============================================================

elif pagina == "Ammissioni / Degenza":

    st.header("🛏️ Ammissioni e Degenza")

    tab1, tab2 = st.tabs(
        ["📋 Ammissioni", "➕ Nuova ammissione"]
    )

    with tab1:

        df = query_df("""
            SELECT
                a.id AS ID,
                p.cognome || ' ' || p.nome AS Paziente,
                m.cognome || ' ' || m.nome AS Medico,
                a.data_ingresso AS "Data ingresso",
                a.data_uscita AS "Data uscita",
                a.reparto AS Reparto,
                a.stanza AS Stanza,
                a.motivo_ricovero AS "Motivo ricovero",
                a.stato AS Stato
            FROM ammissioni a
            LEFT JOIN pazienti p ON a.paziente_id = p.id
            LEFT JOIN medici m ON a.medico_id = m.id
            ORDER BY a.data_ingresso DESC
        """)

        if df.empty:
            st.info("Nessuna ammissione registrata.")
        else:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

    with tab2:

        pazienti = get_paziente_options()
        medici = get_medico_options()

        if not pazienti:

            st.warning("Devi registrare almeno un paziente prima di creare un'ammissione.")

        else:

            with st.form("nuova_ammissione"):

                paziente_label = st.selectbox(
                    "Paziente *",
                    list(pazienti.keys())
                )

                medico_label = st.selectbox(
                    "Medico responsabile",
                    ["Nessuno"] + list(medici.keys())
                )

                col1, col2 = st.columns(2)

                with col1:

                    data_ingresso = st.date_input(
                        "Data ingresso *",
                        value=date.today(),
                        format="DD/MM/YYYY"
                    )

                    reparto = st.text_input("Reparto")
                    stanza = st.text_input("Stanza")

                with col2:

                    stato = st.selectbox(
                        "Stato",
                        [
                            "In corso",
                            "Dimesso",
                            "Trasferito"
                        ]
                    )

                    data_uscita = st.date_input(
                        "Data uscita",
                        value=None,
                        format="DD/MM/YYYY"
                    )

                motivo = st.text_area("Motivo del ricovero")
                note = st.text_area("Note")

                salva = st.form_submit_button(
                    "💾 Registra ammissione",
                    use_container_width=True
                )

            if salva:

                pid = pazienti[paziente_label]

                mid = None

                if medico_label != "Nessuno":
                    mid = medici[medico_label]

                execute_query(
                    """
                    INSERT INTO ammissioni (
                        paziente_id,
                        medico_id,
                        data_ingresso,
                        data_uscita,
                        reparto,
                        stanza,
                        motivo_ricovero,
                        stato,
                        note
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        pid,
                        mid,
                        data_ingresso.isoformat(),
                        data_uscita.isoformat() if data_uscita else None,
                        reparto.strip() or None,
                        stanza.strip() or None,
                        motivo.strip() or None,
                        stato,
                        note.strip() or None
                    )
                )

                st.success("Ammissione registrata.")
                st.rerun()


# ============================================================
# DIAGNOSI
# ============================================================

elif pagina == "Diagnosi":

    st.header("🩺 Diagnosi")

    tab1, tab2 = st.tabs(
        ["📋 Elenco diagnosi", "➕ Nuova diagnosi"]
    )

    with tab1:

        df = query_df("""
            SELECT
                d.id AS ID,
                p.cognome || ' ' || p.nome AS Paziente,
                m.cognome || ' ' || m.nome AS Medico,
                d.data_diagnosi AS "Data",
                d.codice_icd AS "ICD-10",
                d.descrizione AS Descrizione,
                d.tipo AS Tipo,
                d.gravita AS Gravità
            FROM diagnosi d
            LEFT JOIN pazienti p ON d.paziente_id = p.id
            LEFT JOIN medici m ON d.medico_id = m.id
            ORDER BY d.data_diagnosi DESC
        """)

        if df.empty:
            st.info("Nessuna diagnosi registrata.")
        else:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

    with tab2:

        pazienti = get_paziente_options()
        medici = get_medico_options()

        if not pazienti:

            st.warning("Inserisci prima almeno un paziente.")

        else:

            with st.form("nuova_diagnosi"):

                paziente_label = st.selectbox(
                    "Paziente *",
                    list(pazienti.keys())
                )

                medico_label = st.selectbox(
                    "Medico",
                    ["Nessuno"] + list(medici.keys())
                )

                data_diagnosi = st.date_input(
                    "Data diagnosi",
                    value=date.today(),
                    format="DD/MM/YYYY"
                )

                codice_icd = st.text_input(
                    "Codice ICD-10"
                )

                descrizione = st.text_area(
                    "Descrizione diagnosi *"
                )

                col1, col2 = st.columns(2)

                with col1:

                    tipo = st.selectbox(
                        "Tipo",
                        [
                            "Non specificato",
                            "Principale",
                            "Secondaria",
                            "Sospetta",
                            "Confermata"
                        ]
                    )

                with col2:

                    gravita = st.selectbox(
                        "Gravità",
                        [
                            "Non specificata",
                            "Lieve",
                            "Moderata",
                            "Grave",
                            "Critica"
                        ]
                    )

                note = st.text_area("Note")

                salva = st.form_submit_button(
                    "💾 Salva diagnosi",
                    use_container_width=True
                )

            if salva:

                if not descrizione.strip():

                    st.error("La descrizione della diagnosi è obbligatoria.")

                else:

                    pid = pazienti[paziente_label]

                    mid = None

                    if medico_label != "Nessuno":
                        mid = medici[medico_label]

                    execute_query(
                        """
                        INSERT INTO diagnosi (
                            paziente_id,
                            medico_id,
                            data_diagnosi,
                            codice_icd,
                            descrizione,
                            tipo,
                            gravita,
                            note
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            pid,
                            mid,
                            data_diagnosi.isoformat(),
                            codice_icd.strip() or None,
                            descrizione.strip(),
                            None if tipo == "Non specificato" else tipo,
                            None if gravita == "Non specificata" else gravita,
                            note.strip() or None
                        )
                    )

                    st.success("Diagnosi salvata.")
                    st.rerun()


# ============================================================
# PROGNOSI
# ============================================================

elif pagina == "Prognosi":

    st.header("📈 Prognosi")

    tab1, tab2 = st.tabs(
        ["📋 Elenco prognosi", "➕ Nuova prognosi"]
    )

    with tab1:

        df = query_df("""
            SELECT
                pr.id AS ID,
                p.cognome || ' ' || p.nome AS Paziente,
                m.cognome || ' ' || m.nome AS Medico,
                pr.data_prognosi AS Data,
                pr.descrizione AS Descrizione,
                pr.esito_previsto AS "Esito previsto",
                pr.durata_stimata AS Durata
            FROM prognosi pr
            LEFT JOIN pazienti p ON pr.paziente_id = p.id
            LEFT JOIN medici m ON pr.medico_id = m.id
            ORDER BY pr.data_prognosi DESC
        """)

        if df.empty:
            st.info("Nessuna prognosi registrata.")
        else:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

    with tab2:

        pazienti = get_paziente_options()
        medici = get_medico_options()

        if not pazienti:

            st.warning("Inserisci prima un paziente.")

        else:

            with st.form("nuova_prognosi"):

                paziente_label = st.selectbox(
                    "Paziente *",
                    list(pazienti.keys())
                )

                medico_label = st.selectbox(
                    "Medico",
                    ["Nessuno"] + list(medici.keys())
                )

                data_prognosi = st.date_input(
                    "Data prognosi",
                    value=date.today(),
                    format="DD/MM/YYYY"
                )

                descrizione = st.text_area(
                    "Descrizione prognosi *"
                )

                esito = st.selectbox(
                    "Esito previsto",
                    [
                        "Non specificato",
                        "Favorevole",
                        "Riservato",
                        "Incerto",
                        "Sfavorevole"
                    ]
                )

                durata = st.text_input(
                    "Durata stimata"
                )

                note = st.text_area("Note")

                salva = st.form_submit_button(
                    "💾 Salva prognosi",
                    use_container_width=True
                )

            if salva:

                if not descrizione.strip():

                    st.error("La descrizione è obbligatoria.")

                else:

                    pid = pazienti[paziente_label]

                    mid = None

                    if medico_label != "Nessuno":
                        mid = medici[medico_label]

                    execute_query(
                        """
                        INSERT INTO prognosi (
                            paziente_id,
                            medico_id,
                            data_prognosi,
                            descrizione,
                            esito_previsto,
                            durata_stimata,
                            note
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            pid,
                            mid,
                            data_prognosi.isoformat(),
                            descrizione.strip(),
                            None if esito == "Non specificato" else esito,
                            durata.strip() or None,
                            note.strip() or None
                        )
                    )

                    st.success("Prognosi salvata.")
                    st.rerun()


# ============================================================
# TERAPIE
# ============================================================

elif pagina == "Terapie":

    st.header("💊 Terapie e Trattamenti")

    tab1, tab2 = st.tabs(
        ["📋 Elenco terapie", "➕ Nuova terapia"]
    )

    with tab1:

        df = query_df("""
            SELECT
                t.id AS ID,
                p.cognome || ' ' || p.nome AS Paziente,
                m.cognome || ' ' || m.nome AS Medico,
                t.data_inizio AS "Data inizio",
                t.data_fine AS "Data fine",
                t.farmaco_o_trattamento AS Trattamento,
                t.dosaggio AS Dosaggio,
                t.frequenza AS Frequenza
            FROM terapie t
            LEFT JOIN pazienti p ON t.paziente_id = p.id
            LEFT JOIN medici m ON t.medico_id = m.id
            ORDER BY t.data_inizio DESC
        """)

        if df.empty:
            st.info("Nessuna terapia registrata.")
        else:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

    with tab2:

        pazienti = get_paziente_options()
        medici = get_medico_options()

        if not pazienti:

            st.warning("Inserisci prima un paziente.")

        else:

            with st.form("nuova_terapia"):

                paziente_label = st.selectbox(
                    "Paziente *",
                    list(pazienti.keys())
                )

                medico_label = st.selectbox(
                    "Medico",
                    ["Nessuno"] + list(medici.keys())
                )

                col1, col2 = st.columns(2)

                with col1:

                    data_inizio = st.date_input(
                        "Data inizio",
                        value=date.today(),
                        format="DD/MM/YYYY"
                    )

                with col2:

                    data_fine = st.date_input(
                        "Data fine",
                        value=None,
                        format="DD/MM/YYYY"
                    )

                trattamento = st.text_input(
                    "Farmaco / Trattamento *"
                )

                col1, col2 = st.columns(2)

                with col1:
                    dosaggio = st.text_input("Dosaggio")

                with col2:
                    frequenza = st.text_input("Frequenza")

                note = st.text_area("Note")

                salva = st.form_submit_button(
                    "💾 Salva terapia",
                    use_container_width=True
                )

            if salva:

                if not trattamento.strip():

                    st.error("Il trattamento è obbligatorio.")

                else:

                    pid = pazienti[paziente_label]

                    mid = None

                    if medico_label != "Nessuno":
                        mid = medici[medico_label]

                    execute_query(
                        """
                        INSERT INTO terapie (
                            paziente_id,
                            medico_id,
                            data_inizio,
                            data_fine,
                            farmaco_o_trattamento,
                            dosaggio,
                            frequenza,
                            note
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            pid,
                            mid,
                            data_inizio.isoformat(),
                            data_fine.isoformat() if data_fine else None,
                            trattamento.strip(),
                            dosaggio.strip() or None,
                            frequenza.strip() or None,
                            note.strip() or None
                        )
                    )

                    st.success("Terapia salvata.")
                    st.rerun()


# ============================================================
# RICERCA / CARTELLE CLINICHE
# ============================================================

elif pagina == "Ricerca / Cartelle":

    st.header("🔎 Ricerca e Cartelle Cliniche")

    ricerca = st.text_input(
        "Cerca paziente",
        placeholder="Nome, cognome o codice fiscale..."
    )

    if ricerca:

        df = query_df(
            """
            SELECT *
            FROM pazienti
            WHERE
                nome LIKE ?
                OR cognome LIKE ?
                OR codice_fiscale LIKE ?
            ORDER BY cognome, nome
            """,
            (
                f"%{ricerca}%",
                f"%{ricerca}%",
                f"%{ricerca.upper()}%"
            )
        )

        if df.empty:

            st.warning("Nessun paziente trovato.")

        else:

            st.success(
                f"Trovati {len(df)} pazienti."
            )

            options = {
                f"{r['cognome']} {r['nome']} — ID {r['id']}":
                int(r["id"])
                for _, r in df.iterrows()
            }

            scelta = st.selectbox(
                "Seleziona paziente",
                list(options.keys())
            )

            paziente_id = options[scelta]

            paziente = query_df(
                "SELECT * FROM pazienti WHERE id = ?",
                (paziente_id,)
            ).iloc[0]

            st.divider()

            st.subheader(
                f"👤 {paziente['nome']} {paziente['cognome']}"
            )

            # ------------------------------------------------
            # ANAGRAFICA
            # ------------------------------------------------

            st.markdown("### 📋 Dati anagrafici")

            c1, c2, c3 = st.columns(3)

            c1.write(
                f"**Data di nascita:** {format_date(paziente['data_nascita'])}"
            )

            c2.write(
                f"**Sesso:** {paziente['sesso'] or '—'}"
            )

            c3.write(
                f"**Codice fiscale:** {paziente['codice_fiscale'] or '—'}"
            )

            c1, c2, c3 = st.columns(3)

            c1.write(
                f"**Telefono:** {paziente['telefono'] or '—'}"
            )

            c2.write(
                f"**Email:** {paziente['email'] or '—'}"
            )

            c3.write(
                f"**Città:** {paziente['citta'] or '—'}"
            )

            st.write(
                f"**Indirizzo:** {paziente['indirizzo'] or '—'}"
            )

            st.markdown("### 🩸 Informazioni cliniche")

            st.write(
                f"**Gruppo sanguigno:** {paziente['gruppo_sanguigno'] or '—'}"
            )

            st.write(
                f"**Allergie:** {paziente['allergie'] or 'Nessuna informazione'}"
            )

            st.write(
                f"**Patologie pregresse:** {paziente['patologie_pregresse'] or 'Nessuna informazione'}"
            )

            st.write(
                f"**Note:** {paziente['note'] or '—'}"
            )

            st.divider()

            # ------------------------------------------------
            # AMMISSIONI
            # ------------------------------------------------

            st.markdown("### 🛏️ Ammissioni / Degenza")

            ammissioni = query_df(
                """
                SELECT
                    a.id AS ID,
                    a.data_ingresso AS "Ingresso",
                    a.data_uscita AS "Uscita",
                    a.reparto AS Reparto,
                    a.stanza AS Stanza,
                    a.motivo_ricovero AS "Motivo",
                    a.stato AS Stato,
                    m.cognome || ' ' || m.nome AS Medico
                FROM ammissioni a
                LEFT JOIN medici m ON a.medico_id = m.id
                WHERE a.paziente_id = ?
                ORDER BY a.data_ingresso DESC
                """,
                (paziente_id,)
            )

            if ammissioni.empty:
                st.info("Nessuna ammissione.")
            else:
                st.dataframe(
                    ammissioni,
                    use_container_width=True,
                    hide_index=True
                )

            # ------------------------------------------------
            # DIAGNOSI
            # ------------------------------------------------

            st.markdown("### 🩺 Diagnosi")

            diagnosi = query_df(
                """
                SELECT
                    d.id AS ID,
                    d.data_diagnosi AS Data,
                    d.codice_icd AS "ICD-10",
                    d.descrizione AS Descrizione,
                    d.tipo AS Tipo,
                    d.gravita AS Gravità,
                    m.cognome || ' ' || m.nome AS Medico
                FROM diagnosi d
                LEFT JOIN medici m ON d.medico_id = m.id
                WHERE d.paziente_id = ?
                ORDER BY d.data_diagnosi DESC
                """,
                (paziente_id,)
            )

            if diagnosi.empty:
                st.info("Nessuna diagnosi.")
            else:
                st.dataframe(
                    diagnosi,
                    use_container_width=True,
                    hide_index=True
                )

            # ------------------------------------------------
            # PROGNOSI
            # ------------------------------------------------

            st.markdown("### 📈 Prognosi")

            prognosi = query_df(
                """
                SELECT
                    pr.id AS ID,
                    pr.data_prognosi AS Data,
                    pr.descrizione AS Descrizione,
                    pr.esito_previsto AS "Esito previsto",
                    pr.durata_stimata AS Durata,
                    m.cognome || ' ' || m.nome AS Medico
                FROM prognosi pr
                LEFT JOIN medici m ON pr.medico_id = m.id
                WHERE pr.paziente_id = ?
                ORDER BY pr.data_prognosi DESC
                """,
                (paziente_id,)
            )

            if prognosi.empty:
                st.info("Nessuna prognosi.")
            else:
                st.dataframe(
                    prognosi,
                    use_container_width=True,
                    hide_index=True
                )

            # ------------------------------------------------
            # TERAPIE
            # ------------------------------------------------

            st.markdown("### 💊 Terapie")

            terapie = query_df(
                """
                SELECT
                    t.id AS ID,
                    t.data_inizio AS "Inizio",
                    t.data_fine AS "Fine",
                    t.farmaco_o_trattamento AS Trattamento,
                    t.dosaggio AS Dosaggio,
                    t.frequenza AS Frequenza,
                    m.cognome || ' ' || m.nome AS Medico
                FROM terapie t
                LEFT JOIN medici m ON t.medico_id = m.id
                WHERE t.paziente_id = ?
                ORDER BY t.data_inizio DESC
                """,
                (paziente_id,)
            )

            if terapie.empty:
                st.info("Nessuna terapia.")
            else:
                st.dataframe(
                    terapie,
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Sistema Gestionale Clinico"
)
