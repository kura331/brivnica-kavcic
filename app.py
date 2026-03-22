import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")
st.title("KAVČIČ CUTS")

try:
    # Spremenimo v navaden slovar, da preprečimo tisto napako
    creds_dict = dict(st.secrets["gcp_service_account"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Odpremo tabelo BarberBooking
    sheet = client.open("BarberBooking").get_worksheet(0)
    
    st.header("✂️ Rezervacija termina")
    with st.form("booking"):
        ime = st.text_input("Ime in priimek")
        tel = st.text_input("Telefon")
        datum = st.date_input("Izberi datum", min_value=datetime.today())
        poslji = st.form_submit_button("Potrdi")
        
        if poslji:
            if ime and tel:
                sheet.append_row([ime, tel, str(datum)])
                st.success(f"Uspelo! Se vidimo {datum}!")
                st.balloons()
            else:
                st.warning("Izpolni vse!")

except Exception as e:
    st.error("Napaka pri povezavi.")
    st.info(f"Podrobnosti: {e}")
