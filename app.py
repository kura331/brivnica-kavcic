import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. DIZAJN (Črna tema in črni gumbi)
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    [data-testid="stVerticalBlock"] {
        background-color: #111111 !important;
        padding: 2.5rem;
        border-radius: 12px;
        border: 1px solid #333;
    }
    .stButton>button {
        width: 100% !important;
        background-color: #000000 !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        font-weight: bold !important;
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

# 2. VARNA POVEZAVA
@st.cache_resource
def povezi():
    try:
        # Prebere Secrets
        s = st.secrets["gcp_service_account"]
        # Ta del popravi PEM napako (InvalidByte), ki si jo imel na sliki
        fixed_key = s["private_key"].replace("\\n", "\n")
        
        info = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": fixed_key,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        # Odpre tabelo BarberBooking
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except Exception as e:
        st.error(f"Povezava ni uspela: {e}")
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
    if st.button("NADALJUJ"):
        if ime and tel:
            st.session_state.p = {"ime": ime, "tel": tel, "storitev": storitev, "datum": str(datum)}
            st.session_state.korak = 3
            st.rerun()

elif st.session_state.korak == 3:
    p = st.session_state.p
    st.write(f"**Storitev:** {p['storitev']} | **Datum:** {p['datum']}")
    if st.button("POTRDI REZERVACIJO"):
        if sheet:
            sheet.append_row([p['ime'], p['tel'], p['storitev'], p['datum']])
            st.success("Rezervirano! Se vidimo!")
            if st.button("DOMOV"):
                st.session_state.korak = 1
                st.rerun()

st.markdown("---")

# 4. ADMIN (Geslo: kavciccutsadmin0)
with st.expander("🔐 Admin"):
    vpisano = st.text_input("Geslo", type="password")
    if vpisano == "kavciccutsadmin0":
        if sheet:
            podatki = sheet.get_all_records()
            if podatki:
                st.dataframe(podatki)
            else:
                st.info("Ni še rezervacij.")
            if st.button("OSVEŽI"):
                st.rerun()
        else:
            st.error("Napaka pri povezavi s tabelo.") #

st.caption("© 2026 Kavčič Cuts")
