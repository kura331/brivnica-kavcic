import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. NASTAVITVE STRANI
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")
st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA PREKO SECRETS (Brez creds.json datoteke)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Program zdaj gleda v Streamlit Settings -> Secrets
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    
    # Odpre prvo tabelo v datoteki BarberBooking
    sheet = client.open("BarberBooking").get_worksheet(0)
    
    # 3. OBRAZEC ZA STRANKE
    st.header("✂️ Rezervacija termina")
    with st.form("booking_form"):
        ime = st.text_input("Ime in priimek")
        telefon = st.text_input("Telefonska številka")
        datum = st.date_input("Izberi datum", min_value=datetime.today())
        submit = st.form_submit_button("Potrdi rezervacijo")

    if submit:
        if ime and telefon:
            # Zapiše podatke v Google Tabelo
            sheet.append_row([ime, telefon, str(datum), "Čaka na uro"])
            st.success(f"Hvala {ime}! Rezervacija za {datum} je poslana. Pokličemo vas za potrditev ure.")
        else:
            st.warning("Prosimo, izpolni vsa polja.")

except Exception as e:
    st.error("Povezava še ni vzpostavljena. Preveri 'Secrets' v Streamlit nastavitvah.")
    # Za razvijalca (tebe), da vidiš točno napako:
    st.write(f"DEBUG INFO: {e}")

st.markdown("---")
with st.expander("🔐 Admin"):
    if st.text_input("Geslo", type="password") == "brivnica2026":
        st.table(sheet.get_all_records())
