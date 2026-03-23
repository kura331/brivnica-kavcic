import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. DIZAJN
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️", layout="centered")
st.markdown("<style>.stApp { background-color: #000000; color: white; }</style>", unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")

# 2. FUNKCIJA KI POPRAVI KLJUČ
@st.cache_resource
def povezi_brez_napak():
    try:
        s = st.secrets["gcp_service_account"]
        
        # Ta del "pobere" ključ in ga sčisti vseh smeti
        pk = s["private_key"].replace("\\n", "\n").strip()
        
        info = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        creds = Credentials.from_service_account_info(info, scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except Exception as e:
        st.error(f"Povezava še vedno nagaja: {e}")
        return None

sheet = povezi_brez_napak()

# 3. GLAVNI MENU
if st.button("NAROČI SE NA TERMIN"):
    st.session_state.v_delu = True

if st.session_state.get("v_delu"):
    ime = st.text_input("Ime")
    tel = st.text_input("Telefon")
    if st.button("POTRDI"):
        if sheet and ime and tel:
            sheet.append_row([ime, tel, "Frizura", str(datetime.now().date())])
            st.success("Rezervirano!")
            st.session_state.v_delu = False
        else:
            st.warning("Izpolni podatke ali preveri povezavo.")

# 4. ADMIN
with st.expander("🔐 Admin"):
    geslo = st.text_input("Geslo", type="password")
    if geslo == "kavciccutsadmin0":
        if sheet:
            st.table(sheet.get_all_records())
        else:
            st.error("Ni povezave s tabelo.")

st.caption("© 2026 Kavčič Cuts")
