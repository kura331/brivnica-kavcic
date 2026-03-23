import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")

# CSS za črno temo
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .stButton>button { background-color: #111; color: white; border: 1px solid white; width: 100%; }
    input { background-color: #222 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")

@st.cache_resource
def povezi_tabelo():
    try:
        # Prebere Secrets direktno
        info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            info, 
            scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except Exception as e:
        st.error(f"Povezava še vedno nagaja: {e}")
        return None

sheet = povezi_tabelo()

st.markdown("---")
if st.button("NAROČI SE NA TERMIN"):
    st.session_state.narocanje = True

if st.session_state.get("narocanje"):
    ime = st.text_input("Ime in priimek")
    tel = st.text_input("Telefonska številka")
    if st.button("POTRDI"):
        if sheet and ime and tel:
            datum = datetime.now().strftime("%d.%m.%Y %H:%M")
            sheet.append_row([ime, tel, "Striženje", datum])
            st.success(f"Rezervirano! Se vidimo, {ime}.")
            st.session_state.narocanje = False
        else:
            st.error("Podatki niso popolni ali tabela ni dostopna.")

with st.expander("🔐 Admin"):
    geslo = st.text_input("Geslo", type="password")
    if geslo == "kavciccutsadmin0":
        if sheet:
            st.table(sheet.get_all_records())
        else:
            st.error("Ni povezave s tabelo.")

st.markdown("---")
st.caption("© 2026 Kavčič Cuts")
