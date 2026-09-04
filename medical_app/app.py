import streamlit as st
import sqlite3
import os
from datetime import date

# ============================================================
# CONFIGURAZIONE
# ============================================================

st.set_page_config(
    page_title="Gestione Clinica",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = os.path.join(os.path.dirname(__file__), "clinica.db")


# ============================================================
# STILE PROFESSIONALE
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #F4F6F9;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* HEADER */

.app-header {
    background: white;
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 25px;
    border: 1px solid #E1E6ED;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.app-header-title {
    font-size: 30px;
    font-weight: 700;
    color: #0B2A52;
    margin-bottom: 4px;
}

.app-header-subtitle {
    color: #667085;
    font-size: 15px;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background-color: #0B2A52;
}

section[data-testid="stSidebar"] * {
    color: white;
}

.sidebar-brand {
    padding: 15px 10px 30px 10px;
}

.sidebar-brand-title {
    font-size: 25px;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: 0.5px;
}

.sidebar-brand-subtitle {
    margin-top: 8px;
    font-size: 12px;
    color: #BFD2EA !important;
}

/* TITOLI */

h1, h2, h3 {
    color: #0B2A52 !important;
}

h1 {
    font-weight: 700 !important;
}

h2 {
    font-weight: 650 !important;
}

h3 {
    font-weight: 600 !important;
}

/* METRICHE */

.metric-card {
    background: white;
    border: 1px solid #E1E6ED;
    border-radius: 12px;
    padding: 20px;
    min-height: 125px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.035);
}

.metric-title {
    color: #667085;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 10px;
}

.metric-value {
    color: #0B2A52;
    font-size: 30px;
    font-weight: 750;
}

/* CARD */

.clinical-card {
    background: white;
    border: 1px solid #E1E6ED;
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.035);
}

/* INPUT */

.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 8px !important;
}

/* BUTTON */

.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    min-height: 42px;
}

/* TABS */

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 600;
}

/* TABLE */

[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* ALERT */

.stAlert {
    border-radius: 10px;
}

/* FOOTER */

.footer {
    text-align: center;
    color: #98A2B3;
    font-size: 12px;
    padding: 30px 0 10px 0;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medici (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            specializzazione TEXT,
            telefono TEXT,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pazienti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            data_nascita TEXT,
            codice_fiscale TEXT,
            telefono TEXT,
            email TEXT,
            indirizzo TEXT,
            citta TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ammissioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paziente_id INTEGER NOT NULL,
            medico_id INTEGER,
            data_ingresso TEXT NOT NULL,
            data_uscita TEXT,
            reparto TEXT,
            motivo TEXT,
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id) ON DELETE CASCADE,
            FOREIGN KEY (medico_id) REFERENCES medici(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnosi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paziente_id INTEGER NOT NULL,
            medico_id INTEGER,
            data_diagnosi TEXT,
            diagnosi TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id) ON DELETE CASCADE,
            FOREIGN KEY (medico_id) REFERENCES medici(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prognosi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paziente_id INTEGER NOT NULL,
            medico_id INTEGER,
            data_prognosi TEXT,
            prognosi TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id) ON DELETE CASCADE,
            FOREIGN KEY (medico_id) REFERENCES medici(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS terapie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paziente_id INTEGER NOT NULL,
            medico_id INTEGER,
            data_inizio TEXT,
            data_fine TEXT,
            terapia TEXT NOT NULL,
            dosaggio TEXT,
            note TEXT,
            FOREIGN KEY (paziente_id) REFERENCES pazienti(id) ON DELETE CASCADE,
            FOREIGN KEY (medico_id) REFERENCES medici(id) ON DELETE SET NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ============================================================
# FUNZIONI DATABASE
# ============================================================

def fetch_all(query, params=()):
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def fetch_one(query, params=()):
    conn = get_connection()
    row = conn.execute(query, params).fetchone()
    conn.close()
    return row


def execute_query(query, params=()):
    conn = get_connection()
    cursor = conn.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="app-header">
    <div class="app-header-title">Gestione Clinica</div>
    <div class="app-header-subtitle">
        Gestione pazienti, personale, ricoveri e documentazione clinica
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-brand-title">GESTIONE<br>CLINICA</div>
    <div class="sidebar-brand-subtitle">
        Sistema informativo clinico
    </div>
</div>
""", unsafe_allow_html=True)

pagina = st.sidebar.radio(
    "Navigazione",
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

    st.title("Dashboard")

    pazienti_count = fetch_one(
        "SELECT COUNT(*) AS c FROM pazienti"
    )["c"]

    medici_count = fetch_one(
        "SELECT COUNT(*) AS c FROM medici"
    )["c"]

    ricoveri_count = fetch_one(
        """
        SELECT COUNT(*) AS c
        FROM ammissioni
        WHERE data_uscita IS NULL OR data_uscita = ''
        """
    )["c"]

    diagnosi_count = fetch_one(
        "SELECT COUNT(*) AS c FROM diagnosi"
    )["c"]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Pazienti registrati</div>
            <div class="metric-value">{pazienti_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Medici / Operatori</div>
            <div class="metric-value">{medici_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Ricoveri in corso</div>
            <div class="metric-value">{ricoveri_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Diagnosi registrate</div>
            <div class="metric-value">{diagnosi_count}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    st.markdown("""
    <div class="clinical-card">
        <h3>Ultime ammissioni</h3>
    </div>
    """, unsafe_allow_html=True)

    ultime = fetch_all("""
        SELECT
            a.id,
            p.nome || ' ' || p.cognome AS paziente,
            m.nome || ' ' || m.cognome AS medico,
            a.data_ingresso,
            a.data_uscita,
            a.reparto,
            a.motivo
        FROM ammissioni a
        JOIN pazienti p ON p.id = a.paziente_id
        LEFT JOIN medici m ON m.id = a.medico_id
        ORDER BY a.id DESC
        LIMIT 10
    """)

    if ultime:
        import pandas as pd

        df = pd.DataFrame([dict(row) for row in ultime])

        df.columns = [
            "ID",
            "Paziente",
            "Medico",
            "Ingresso",
            "Uscita",
            "Reparto",
            "Motivo"
        ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Non sono ancora presenti ammissioni.")


# ============================================================
# PAZIENTI
# ============================================================

elif pagina == "Pazienti":

    st.title("Pazienti")

    tab1, tab2 = st.tabs([
        "Elenco pazienti",
        "Nuovo paziente"
    ])

    with tab1:

        pazienti = fetch_all("""
            SELECT
                id,
                nome,
                cognome,
                data_nascita,
                codice_fiscale,
                telefono,
                email,
                citta
            FROM pazienti
            ORDER BY cognome, nome
        """)

        if pazienti:

            import pandas as pd

            df = pd.DataFrame([dict(row) for row in pazienti])

            df.columns = [
                "ID",
                "Nome",
                "Cognome",
                "Data nascita",
                "Codice fiscale",
                "Telefono",
                "Email",
                "Città"
            ]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("Modifica paziente")

            id_modifica = st.number_input(
                "ID paziente",
                min_value=1,
                step=1
            )

            paziente = fetch_one(
                "SELECT * FROM pazienti WHERE id = ?",
                (id_modifica,)
            )

            if paziente:

                nome = st.text_input(
                    "Nome",
                    value=paziente["nome"] or ""
                )

                cognome = st.text_input(
                    "Cognome",
                    value=paziente["cognome"] or ""
                )

                data_nascita = st.text_input(
                    "Data di nascita",
                    value=paziente["data_nascita"] or ""
                )

                codice_fiscale = st.text_input(
                    "Codice fiscale",
                    value=paziente["codice_fiscale"] or ""
                )

                telefono = st.text_input(
                    "Telefono",
                    value=paziente["telefono"] or ""
                )

                email = st.text_input(
                    "Email",
                    value=paziente["email"] or ""
                )

                indirizzo = st.text_input(
                    "Indirizzo",
                    value=paziente["indirizzo"] or ""
                )

                citta = st.text_input(
                    "Città",
                    value=paziente["citta"] or ""
                )

                c1, c2 = st.columns(2)

                with c1:
                    if st.button(
                        "Salva modifiche",
                        type="primary",
                        use_container_width=True
                    ):
                        execute_query("""
                            UPDATE pazienti
                            SET
                                nome = ?,
                                cognome = ?,
                                data_nascita = ?,
                                codice_fiscale = ?,
                                telefono = ?,
                                email = ?,
                                indirizzo = ?,
                                citta = ?
                            WHERE id = ?
                        """, (
                            nome,
                            cognome,
                            data_nascita,
                            codice_fiscale,
                            telefono,
                            email,
                            indirizzo,
                            citta,
                            id_modifica
                        ))

                        st.success("Paziente aggiornato.")
                        st.rerun()

                with c2:
                    if st.button(
                        "Elimina paziente",
                        use_container_width=True
                    ):
                        execute_query(
                            "DELETE FROM pazienti WHERE id = ?",
                            (id_modifica,)
                        )

                        st.success("Paziente eliminato.")
                        st.rerun()

        else:
            st.info("Non sono presenti pazienti.")

    with tab2:

        st.subheader("Inserimento nuovo paziente")

        c1, c2 = st.columns(2)

        with c1:
            nome = st.text_input("Nome *")
            cognome = st.text_input("Cognome *")
            data_nascita = st.text_input(
                "Data di nascita",
                placeholder="GG/MM/AAAA"
            )
            codice_fiscale = st.text_input(
                "Codice fiscale"
            )

        with c2:
            telefono = st.text_input("Telefono")
            email = st.text_input("Email")
            indirizzo = st.text_input("Indirizzo")
            citta = st.text_input("Città")

        if st.button(
            "Registra paziente",
            type="primary",
            use_container_width=True
        ):

            if not nome or not cognome:
                st.error("Nome e cognome sono obbligatori.")
            else:

                execute_query("""
                    INSERT INTO pazienti (
                        nome,
                        cognome,
                        data_nascita,
                        codice_fiscale,
                        telefono,
                        email,
                        indirizzo,
                        citta
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    nome,
                    cognome,
                    data_nascita,
                    codice_fiscale,
                    telefono,
                    email,
                    indirizzo,
                    citta
                ))

                st.success("Paziente registrato correttamente.")
                st.rerun()


# ============================================================
# MEDICI
# ============================================================

elif pagina == "Medici / Operatori":

    st.title("Medici / Operatori")

    tab1, tab2 = st.tabs([
        "Elenco",
        "Nuovo medico / operatore"
    ])

    with tab1:

        medici = fetch_all("""
            SELECT
                id,
                nome,
                cognome,
                specializzazione,
                telefono,
                email
            FROM medici
            ORDER BY cognome, nome
        """)

        if medici:

            import pandas as pd

            df = pd.DataFrame([dict(row) for row in medici])

            df.columns = [
                "ID",
                "Nome",
                "Cognome",
                "Specializzazione",
                "Telefono",
                "Email"
            ]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("Non sono presenti medici o operatori.")

    with tab2:

        st.subheader("Nuovo medico / operatore")

        nome = st.text_input("Nome *")
        cognome = st.text_input("Cognome *")
        specializzazione = st.text_input(
            "Specializzazione"
        )
        telefono = st.text_input("Telefono")
        email = st.text_input("Email")

        if st.button(
            "Registra medico / operatore",
            type="primary",
            use_container_width=True
        ):

            if not nome or not cognome:
                st.error("Nome e cognome sono obbligatori.")
            else:

                execute_query("""
                    INSERT INTO medici (
                        nome,
                        cognome,
                        specializzazione,
                        telefono,
                        email
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    nome,
                    cognome,
                    specializzazione,
                    telefono,
                    email
                ))

                st.success("Medico / operatore registrato.")
                st.rerun()


# ============================================================
# AMMISSIONI
# ============================================================

elif pagina == "Ammissioni / Degenza":

    st.title("Ammissioni / Degenza")

    pazienti = fetch_all("""
        SELECT id, nome, cognome
        FROM pazienti
        ORDER BY cognome, nome
    """)

    medici = fetch_all("""
        SELECT id, nome, cognome
        FROM medici
        ORDER BY cognome, nome
    """)

    if not pazienti:
        st.warning(
            "Devi prima registrare almeno un paziente."
        )
    else:

        pazienti_dict = {
            f"{p['cognome']} {p['nome']} — ID {p['id']}": p["id"]
            for p in pazienti
        }

        medici_dict = {
            f"{m['cognome']} {m['nome']} — ID {m['id']}": m["id"]
            for m in medici
        }

        paziente_selezionato = st.selectbox(
            "Paziente",
            list(pazienti_dict.keys())
        )

        medico_options = ["Nessun medico"] + list(
            medici_dict.keys()
        )

        medico_selezionato = st.selectbox(
            "Medico / Operatore",
            medico_options
        )

        c1, c2 = st.columns(2)

        with c1:
            data_ingresso = st.date_input(
                "Data ingresso",
                value=date.today(),
                format="DD/MM/YYYY"
            )

        with c2:
            data_uscita = st.date_input(
                "Data uscita",
                value=None,
                format="DD/MM/YYYY"
            )

        reparto = st.text_input("Reparto")
        motivo = st.text_area("Motivo del ricovero")

        if st.button(
            "Registra ammissione",
            type="primary",
            use_container_width=True
        ):

            paziente_id = pazienti_dict[
                paziente_selezionato
            ]

            medico_id = None

            if medico_selezionato != "Nessun medico":
                medico_id = medici_dict[
                    medico_selezionato
                ]

            data_ingresso_str = data_ingresso.strftime(
                "%Y-%m-%d"
            )

            data_uscita_str = None

            if data_uscita:
                data_uscita_str = data_uscita.strftime(
                    "%Y-%m-%d"
                )

            execute_query("""
                INSERT INTO ammissioni (
                    paziente_id,
                    medico_id,
                    data_ingresso,
                    data_uscita,
                    reparto,
                    motivo
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                paziente_id,
                medico_id,
                data_ingresso_str,
                data_uscita_str,
                reparto,
                motivo
            ))

            st.success("Ammissione registrata.")
            st.rerun()

    st.divider()

    st.subheader("Ammissioni registrate")

    ammissioni = fetch_all("""
        SELECT
            a.id,
            p.nome || ' ' || p.cognome AS paziente,
            m.nome || ' ' || m.cognome AS medico,
            a.data_ingresso,
            a.data_uscita,
            a.reparto,
            a.motivo
        FROM ammissioni a
        JOIN pazienti p ON p.id = a.paziente_id
        LEFT JOIN medici m ON m.id = a.medico_id
        ORDER BY a.id DESC
    """)

    if ammissioni:

        import pandas as pd

        df = pd.DataFrame(
            [dict(row) for row in ammissioni]
        )

        df.columns = [
            "ID",
            "Paziente",
            "Medico",
            "Ingresso",
            "Uscita",
            "Reparto",
            "Motivo"
        ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Nessuna ammissione registrata.")


# ============================================================
# DIAGNOSI
# ============================================================

elif pagina == "Diagnosi":

    st.title("Diagnosi")

    pazienti = fetch_all("""
        SELECT id, nome, cognome
        FROM pazienti
        ORDER BY cognome, nome
    """)

    medici = fetch_all("""
        SELECT id, nome, cognome
        FROM medici
        ORDER BY cognome, nome
    """)

    if not pazienti:
        st.warning(
            "Devi prima registrare almeno un paziente."
        )
    else:

        pazienti_dict = {
            f"{p['cognome']} {p['nome']} — ID {p['id']}": p["id"]
            for p in pazienti
        }

        medici_dict = {
            f"{m['cognome']} {m['nome']} — ID {m['id']}": m["id"]
            for m in medici
        }

        paziente_selezionato = st.selectbox(
            "Paziente",
            list(pazienti_dict.keys()),
            key="diagnosi_paziente"
        )

        medico_options = ["Nessun medico"] + list(
            medici_dict.keys()
        )

        medico_selezionato = st.selectbox(
            "Medico / Operatore",
            medico_options,
            key="diagnosi_medico"
        )

        data_diagnosi = st.date_input(
            "Data diagnosi",
            value=date.today(),
            format="DD/MM/YYYY"
        )

        diagnosi = st.text_area(
            "Diagnosi *",
            height=120
        )

        note = st.text_area(
            "Note",
            height=100
        )

        if st.button(
            "Registra diagnosi",
            type="primary",
            use_container_width=True
        ):

            if not diagnosi:
                st.error("Inserisci la diagnosi.")
            else:

                medico_id = None

                if medico_selezionato != "Nessun medico":
                    medico_id = medici_dict[
                        medico_selezionato
                    ]

                execute_query("""
                    INSERT INTO diagnosi (
                        paziente_id,
                        medico_id,
                        data_diagnosi,
                        diagnosi,
                        note
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    pazienti_dict[paziente_selezionato],
                    medico_id,
                    data_diagnosi.strftime("%Y-%m-%d"),
                    diagnosi,
                    note
                ))

                st.success("Diagnosi registrata.")
                st.rerun()

    st.divider()

    st.subheader("Diagnosi registrate")

    diagnosi_rows = fetch_all("""
        SELECT
            d.id,
            p.nome || ' ' || p.cognome AS paziente,
            m.nome || ' ' || m.cognome AS medico,
            d.data_diagnosi,
            d.diagnosi,
            d.note
        FROM diagnosi d
        JOIN pazienti p ON p.id = d.paziente_id
        LEFT JOIN medici m ON m.id = d.medico_id
        ORDER BY d.id DESC
    """)

    if diagnosi_rows:

        import pandas as pd

        df = pd.DataFrame(
            [dict(row) for row in diagnosi_rows]
        )

        df.columns = [
            "ID",
            "Paziente",
            "Medico",
            "Data",
            "Diagnosi",
            "Note"
        ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Nessuna diagnosi registrata.")


# ============================================================
# PROGNOSI
# ============================================================

elif pagina == "Prognosi":

    st.title("Prognosi")

    pazienti = fetch_all("""
        SELECT id, nome, cognome
        FROM pazienti
        ORDER BY cognome, nome
    """)

    medici = fetch_all("""
        SELECT id, nome, cognome
        FROM medici
        ORDER BY cognome, nome
    """)

    if not pazienti:
        st.warning(
            "Devi prima registrare almeno un paziente."
        )
    else:

        pazienti_dict = {
            f"{p['cognome']} {p['nome']} — ID {p['id']}": p["id"]
            for p in pazienti
        }

        medici_dict = {
            f"{m['cognome']} {m['nome']} — ID {m['id']}": m["id"]
            for m in medici
        }

        paziente_selezionato = st.selectbox(
            "Paziente",
            list(pazienti_dict.keys()),
            key="prognosi_paziente"
        )

        medico_options = ["Nessun medico"] + list(
            medici_dict.keys()
        )

        medico_selezionato = st.selectbox(
            "Medico / Operatore",
            medico_options,
            key="prognosi_medico"
        )

        data_prognosi = st.date_input(
            "Data prognosi",
            value=date.today(),
            format="DD/MM/YYYY"
        )

        prognosi = st.text_area(
            "Prognosi *",
            height=120
        )

        note = st.text_area(
            "Note",
            height=100
        )

        if st.button(
            "Registra prognosi",
            type="primary",
            use_container_width=True
        ):

            if not prognosi:
                st.error("Inserisci la prognosi.")
            else:

                medico_id = None

                if medico_selezionato != "Nessun medico":
                    medico_id = medici_dict[
                        medico_selezionato
                    ]

                execute_query("""
                    INSERT INTO prognosi (
                        paziente_id,
                        medico_id,
                        data_prognosi,
                        prognosi,
                        note
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    pazienti_dict[paziente_selezionato],
                    medico_id,
                    data_prognosi.strftime("%Y-%m-%d"),
                    prognosi,
                    note
                ))

                st.success("Prognosi registrata.")
                st.rerun()

    st.divider()

    st.subheader("Prognosi registrate")

    prognosi_rows = fetch_all("""
        SELECT
            pr.id,
            p.nome || ' ' || p.cognome AS paziente,
            m.nome || ' ' || m.cognome AS medico,
            pr.data_prognosi,
            pr.prognosi,
            pr.note
        FROM prognosi pr
        JOIN pazienti p ON p.id = pr.paziente_id
        LEFT JOIN medici m ON m.id = pr.medico_id
        ORDER BY pr.id DESC
    """)

    if prognosi_rows:

        import pandas as pd

        df = pd.DataFrame(
            [dict(row) for row in prognosi_rows]
        )

        df.columns = [
            "ID",
            "Paziente",
            "Medico",
            "Data",
            "Prognosi",
            "Note"
        ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Nessuna prognosi registrata.")


# ============================================================
# TERAPIE
# ============================================================

elif pagina == "Terapie":

    st.title("Terapie")

    pazienti = fetch_all("""
        SELECT id, nome, cognome
        FROM pazienti
        ORDER BY cognome, nome
    """)

    medici = fetch_all("""
        SELECT id, nome, cognome
        FROM medici
        ORDER BY cognome, nome
    """)

    if not pazienti:
        st.warning(
            "Devi prima registrare almeno un paziente."
        )
    else:

        pazienti_dict = {
            f"{p['cognome']} {p['nome']} — ID {p['id']}": p["id"]
            for p in pazienti
        }

        medici_dict = {
            f"{m['cognome']} {m['nome']} — ID {m['id']}": m["id"]
            for m in medici
        }

        paziente_selezionato = st.selectbox(
            "Paziente",
            list(pazienti_dict.keys()),
            key="terapia_paziente"
        )

        medico_options = ["Nessun medico"] + list(
            medici_dict.keys()
        )

        medico_selezionato = st.selectbox(
            "Medico / Operatore",
            medico_options,
            key="terapia_medico"
        )

        c1, c2 = st.columns(2)

        with c1:
            data_inizio = st.date_input(
                "Data inizio",
                value=date.today(),
                format="DD/MM/YYYY"
            )

        with c2:
            data_fine = st.date_input(
                "Data fine",
                value=None,
                format="DD/MM/YYYY"
            )

        terapia = st.text_area(
            "Terapia *",
            height=120
        )

        dosaggio = st.text_input(
            "Dosaggio"
        )

        note = st.text_area(
            "Note",
            height=100
        )

        if st.button(
            "Registra terapia",
            type="primary",
            use_container_width=True
        ):

            if not terapia:
                st.error("Inserisci la terapia.")
            else:

                medico_id = None

                if medico_selezionato != "Nessun medico":
                    medico_id = medici_dict[
                        medico_selezionato
                    ]

                data_inizio_str = data_inizio.strftime(
                    "%Y-%m-%d"
                )

                data_fine_str = None

                if data_fine:
                    data_fine_str = data_fine.strftime(
                        "%Y-%m-%d"
                    )

                execute_query("""
                    INSERT INTO terapie (
                        paziente_id,
                        medico_id,
                        data_inizio,
                        data_fine,
                        terapia,
                        dosaggio,
                        note
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    pazienti_dict[paziente_selezionato],
                    medico_id,
                    data_inizio_str,
                    data_fine_str,
                    terapia,
                    dosaggio,
                    note
                ))

                st.success("Terapia registrata.")
                st.rerun()

    st.divider()

    st.subheader("Terapie registrate")

    terapie_rows = fetch_all("""
        SELECT
            t.id,
            p.nome || ' ' || p.cognome AS paziente,
            m.nome || ' ' || m.cognome AS medico,
            t.data_inizio,
            t.data_fine,
            t.terapia,
            t.dosaggio,
            t.note
        FROM terapie t
        JOIN pazienti p ON p.id = t.paziente_id
        LEFT JOIN medici m ON m.id = t.medico_id
        ORDER BY t.id DESC
    """)

    if terapie_rows:

        import pandas as pd

        df = pd.DataFrame(
            [dict(row) for row in terapie_rows]
        )

        df.columns = [
            "ID",
            "Paziente",
            "Medico",
            "Inizio",
            "Fine",
            "Terapia",
            "Dosaggio",
            "Note"
        ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Nessuna terapia registrata.")


# ============================================================
# RICERCA / CARTELLE
# ============================================================

elif pagina == "Ricerca / Cartelle":

    st.title("Ricerca / Cartelle cliniche")

    ricerca = st.text_input(
        "Cerca paziente",
        placeholder="Nome, cognome o codice fiscale..."
    )

    if ricerca:

        pazienti = fetch_all("""
            SELECT *
            FROM pazienti
            WHERE
                nome LIKE ?
                OR cognome LIKE ?
                OR codice_fiscale LIKE ?
            ORDER BY cognome, nome
        """, (
            f"%{ricerca}%",
            f"%{ricerca}%",
            f"%{ricerca}%"
        ))

        if not pazienti:
            st.warning(
                "Nessun paziente trovato."
            )

        for paziente in pazienti:

            st.markdown(
                f"""
                <div class="clinical-card">
                    <h3>
                        {paziente["nome"]} {paziente["cognome"]}
                    </h3>
                    <p>
                        <strong>ID:</strong> {paziente["id"]}
                    </p>
                    <p>
                        <strong>Codice fiscale:</strong>
                        {paziente["codice_fiscale"] or "-"}
                    </p>
                    <p>
                        <strong>Data di nascita:</strong>
                        {paziente["data_nascita"] or "-"}
                    </p>
                    <p>
                        <strong>Telefono:</strong>
                        {paziente["telefono"] or "-"}
                    </p>
                    <p>
                        <strong>Email:</strong>
                        {paziente["email"] or "-"}
                    </p>
                    <p>
                        <strong>Indirizzo:</strong>
                        {paziente["indirizzo"] or "-"}
                    </p>
                    <p>
                        <strong>Città:</strong>
                        {paziente["citta"] or "-"}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            paziente_id = paziente["id"]

            # AMMISSIONI

            st.subheader("Ammissioni")

            ammissioni = fetch_all("""
                SELECT
                    a.id,
                    a.data_ingresso,
                    a.data_uscita,
                    a.reparto,
                    a.motivo,
                    m.nome || ' ' || m.cognome AS medico
                FROM ammissioni a
                LEFT JOIN medici m ON m.id = a.medico_id
                WHERE a.paziente_id = ?
                ORDER BY a.id DESC
            """, (paziente_id,))

            if ammissioni:

                import pandas as pd

                df = pd.DataFrame(
                    [dict(row) for row in ammissioni]
                )

                df.columns = [
                    "ID",
                    "Ingresso",
                    "Uscita",
                    "Reparto",
                    "Motivo",
                    "Medico"
                ]

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.caption(
                    "Nessuna ammissione registrata."
                )

            # DIAGNOSI

            st.subheader("Diagnosi")

            diagnosi = fetch_all("""
                SELECT
                    d.id,
                    d.data_diagnosi,
                    d.diagnosi,
                    d.note,
                    m.nome || ' ' || m.cognome AS medico
                FROM diagnosi d
                LEFT JOIN medici m ON m.id = d.medico_id
                WHERE d.paziente_id = ?
                ORDER BY d.id DESC
            """, (paziente_id,))

            if diagnosi:

                import pandas as pd

                df = pd.DataFrame(
                    [dict(row) for row in diagnosi]
                )

                df.columns = [
                    "ID",
                    "Data",
                    "Diagnosi",
                    "Note",
                    "Medico"
                ]

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.caption(
                    "Nessuna diagnosi registrata."
                )

            # PROGNOSI

            st.subheader("Prognosi")

            prognosi = fetch_all("""
                SELECT
                    pr.id,
                    pr.data_prognosi,
                    pr.prognosi,
                    pr.note,
                    m.nome || ' ' || m.cognome AS medico
                FROM prognosi pr
                LEFT JOIN medici m ON m.id = pr.medico_id
                WHERE pr.paziente_id = ?
                ORDER BY pr.id DESC
            """, (paziente_id,))

            if prognosi:

                import pandas as pd

                df = pd.DataFrame(
                    [dict(row) for row in prognosi]
                )

                df.columns = [
                    "ID",
                    "Data",
                    "Prognosi",
                    "Note",
                    "Medico"
                ]

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.caption(
                    "Nessuna prognosi registrata."
                )

            # TERAPIE

            st.subheader("Terapie")

            terapie = fetch_all("""
                SELECT
                    t.id,
                    t.data_inizio,
                    t.data_fine,
                    t.terapia,
                    t.dosaggio,
                    t.note,
                    m.nome || ' ' || m.cognome AS medico
                FROM terapie t
                LEFT JOIN medici m ON m.id = t.medico_id
                WHERE t.paziente_id = ?
                ORDER BY t.id DESC
            """, (paziente_id,))

            if terapie:

                import pandas as pd

                df = pd.DataFrame(
                    [dict(row) for row in terapie]
                )

                df.columns = [
                    "ID",
                    "Inizio",
                    "Fine",
                    "Terapia",
                    "Dosaggio",
                    "Note",
                    "Medico"
                ]

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.caption(
                    "Nessuna terapia registrata."
                )

            st.divider()


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
    Gestione Clinica · Sistema informativo clinico · v1.0
</div>
""", unsafe_allow_html=True)
