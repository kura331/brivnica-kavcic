import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. KONFIGURACIJA
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")

# Stilski popravek za čist videz
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #0e1117; color: white; border: 1px solid #444; }
    .stButton>button:hover { border-color: #fff; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA Z GIP
@st.cache_resource
def povezi_tabelo():
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except:
        return None

sheet = povezi_tabelo()

# 3. LOGIKA KORAKOV (Session State)
if "korak" not in st.session_state:
    st.session_state.korak = 1

# --- KORAK 1: ZAČETNI MENU ---
if st.session_state.korak == 1:
    st.markdown("### Dobrodošli")
    st.write("Za rezervacijo termina kliknite spodnji gumb.")
    if st.button("NAROČI SE NA STRIŽENJE"):
        st.session_state.korak = 2
        st.rerun()

# --- KORAK 2: VNOS PODATKOV ---
elif st.session_state.korak == 2:
    st.markdown("### Podatki za rezervacijo")
    ime = st.text_input("Ime in priimek")
    tel = st.text_input("Telefonska številka")
    datum = st.date_input("Izberite datum", min_value=datetime.today())
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("NAZAJ"):
            st.session_state.korak = 1
            st.rerun()
    with col2:
        if st.button("NADALJUJ"):
            if ime and tel:
                st.session_state.podatki = {"ime": ime, "tel": tel, "datum": str(datum)}
                st.session_state.korak = 3
                st.rerun()
            else:
                st.warning("Prosimo, izpolnite vsa polja.")

# --- KORAK 3: POTRDITEV ---
elif st.session_state.korak == 3:
    p = st.session_state.podatki
    st.markdown("### Potrdite rezervacijo")
    st.write(f"**Ime:** {p['ime']}")
    st.write(f"**Telefon:** {p['tel']}")
    st.write(f"**Datum:** {p['datum']}")
    st.markdown("---")
    
    if st.button("POTRDI REZERVACIJO"):
        if sheet:
            sheet.append_row([p['ime'], p['tel'], p['datum'], "Novo"])
            st.success("Vaša rezervacija je bila uspešno poslana!")
            if st.button("DOMOV"):
                st.session_state.korak = 1
                st.rerun()
        else:
            st.error("Napaka pri povezavi s bazo.")

st.markdown("---")
# ADMIN DEL (Vedno dostopen spodaj)
with st.expander("🔐 Admin"):
    if st.text_input("Geslo", type="password") == "brivnica2026":
        if sheet:
            st.dataframe(sheet.get_all_records())

st.caption("© 2026 Kavčič Cuts")
