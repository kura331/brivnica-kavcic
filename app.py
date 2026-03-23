import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. KONFIGURACIJA (Črna tema in gumbi z belim robom)
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    [data-testid="stVerticalBlock"] {
        background-color: #111111 !important;
        padding: 2.5rem;
        border-radius: 15px;
        border: 1px solid #333;
    }
    /* Gumbi: Črni z močnim belim robom */
    .stButton>button {
        width: 100% !important;
        background-color: #000000 !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    h1, h2, h3, p, label { color: white !important; }
    input, select, .stSelectbox div {
        background-color: #000000 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA (Vrstica, ki jo moraš preveriti)
@st.cache_resource
def povezi():
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        # TUKAJ JE IME TABELE: BarberBooking
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except Exception as e:
        st.error(f"Napaka pri povezavi: {e}")
        return None

sheet = povezi()

if "korak" not in st.session_state:
    st.session_state.korak = 1

# 3. KORAKI NAROČANJA
if st.session_state.korak == 1:
    st.markdown("### Dobrodošli")
    if st.button("NAROČI SE NA TERMIN"):
        st.session_state.korak = 2
        st.rerun()

elif st.session_state.korak == 2:
    st.markdown("### Vpišite podatke")
    ime = st.text_input("Ime in priimek")
    tel = st.text_input("Telefon")
    storitev = st.selectbox("Izberite storitev:", ["Frizura", "Brada", "Oboje"])
    datum = st.date_input("Datum", min_value=datetime.today())
    
    # Gumb nadaljuj za stranko
    if st.button("NADALJUJ"):
        if ime and tel:
            st.session_state.p = {"ime": ime, "tel": tel, "storitev": storitev, "datum": str(datum)}
            st.session_state.korak = 3
            st.rerun()

elif st.session_state.korak == 3:
    p = st.session_state.p
    st.write(f"**Stranka:** {p['ime']} | **Storitev:** {p['storitev']}")
    if st.button("POTRDI REZERVACIJO"):
        if sheet:
            sheet.append_row([p['ime'], p['tel'], p['storitev'], p['datum']])
            st.success("Rezervirano!")
            if st.button("DOMOV"):
                st.session_state.korak = 1
                st.rerun()

st.markdown("---")

# 4. ADMIN Z NOVIM GESLOM
with st.expander("🔐 Admin"):
    vpisano = st.text_input("Geslo", type="password")
    if vpisano == "kavciccutsadmin0": # Tvoje novo geslo
        if sheet:
            st.dataframe(sheet.get_all_records())
            # Gumb nadaljuj v adminu za osvežitev
            if st.button("NADALJUJ (OSVEŽI)"):
                st.rerun()
