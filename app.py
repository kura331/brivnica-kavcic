import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. IZGLED STRANI
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .stButton>button { background-color: #111; color: white; border: 1px solid white; width: 100%; }
    input { background-color: #222 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")

# 2. POVEZAVA Z GOOGLE SHEETS
@st.cache_resource
def povezi_tabelo():
    try:
        # Prebere vse direktno iz Secrets
        info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(
            info, 
            scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
        # Odpre tvojo tabelo BarberBooking
        client = gspread.authorize(creds)
        return client.open("BarberBooking").get_worksheet(0)
    except Exception as e:
        st.error(f"Povezava še vedno nagaja: {e}")
        return None

sheet = povezi_tabelo()

# 3. UPORABNIŠKI VMESNIK
st.markdown("---")
if st.button("NAROČI SE NA TERMIN"):
    st.session_state.narocanje = True

if st.session_state.get("narocanje"):
    ime = st.text_input("Ime in priimek")
    tel = st.text_input("Telefonska številka")
    if st.button("POTRDI REZERVACIJO"):
        if sheet and ime and tel:
            datum = datetime.now().strftime("%d.%m.%Y %H:%M")
            sheet.append_row([ime, tel, "Moško striženje", datum])
            st.success(f"Rezervirano! Se vidimo, {ime}.")
            st.session_state.narocanje = False
        else:
            st.error("Nekaj manjka (ime, telefon ali tabela).")

# 4. ADMIN DEL
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🔐 Admin"):
    geslo = st.text_input("Vnesi geslo", type="password")
    if geslo == "kavciccutsadmin0":
        if sheet:
            st.write("Seznam rezervacij:")
            st.table(sheet.get_all_records())
        else:
            st.error("Ni povezave s tabelo.")

# 5. NOGA
st.markdown("---")
st.caption("© 2026 Kavčič Cuts")
