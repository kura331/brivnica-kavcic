import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. NASTAVITVE STRANI
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")
st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA PREKO SECRETS
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Ta del kode zdaj varno prebere tvoj dolgi ključ iz Streamlit nastavitev
    creds_dict = st.secrets["gcp_service_account"]
    
    # POPRAVEK: Streamlit včasih napačno prebere \n, zato jih tukaj popravimo
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
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
            sheet.append_row([ime, telefon, str(datum), "Čaka na uro"])
            st.success(f"Hvala {ime}! Rezervacija za {datum} je poslana.")
        else:
            st.warning("Prosimo, izpolni vsa polja.")

except Exception as e:
    st.error("Napaka pri povezavi.")
    st.info(f"Podrobnosti napake: {e}")

st.markdown("---")
