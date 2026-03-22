import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")
st.title("KAVČIČ CUTS")

try:
    # Preberemo Secrets kot slovar
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # Popravimo znake za novo vrstico, da jih Google prepozna
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("BarberBooking").get_worksheet(0)
    
    st.header("✂️ Rezervacija termina")
    with st.form("booking"):
        ime = st.text_input("Ime in priimek")
        tel = st.text_input("Telefonska številka")
        datum = st.date_input("Izberi datum", min_value=datetime.today())
        if st.form_submit_button("Potrdi rezervacijo"):
            if ime and tel:
                sheet.append_row([ime, tel, str(datum), "Čaka na uro"])
                st.success("Rezervacija poslana!")
                st.balloons()
            else:
                st.warning("Izpolni vsa polja.")
except Exception as e:
    st.error("Napaka pri povezavi.")
    st.info(f"Podrobnosti: {e}")
