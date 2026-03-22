import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")

# Čist videz
st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

def vzpostavi_povezavo():
    try:
        # Preberemo Secrets kot slovar
        info = dict(st.secrets["gcp_service_account"])
        # Popravimo poševnice za Google API
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("BarberBooking").get_worksheet(0)
    except Exception as e:
        st.error(f"Napaka pri povezavi: {e}")
        return None

sheet = vzpostavi_povezavo()

if sheet:
    with st.form("booking", clear_on_submit=True):
        st.markdown("### Rezervacija termina")
        ime = st.text_input("Ime in priimek")
        tel = st.text_input("Telefon")
        datum = st.date_input("Datum", min_value=datetime.today())
        
        if st.form_submit_button("POTRDI"):
            if ime and tel:
                sheet.append_row([ime, tel, str(datum), "Novo"])
                st.success("Rezervacija je bila uspešno oddana.")
            else:
                st.warning("Izpolnite vsa polja.")

st.markdown("---")
with st.expander("🔐"):
    if st.text_input("Koda", type="password") == "brivnica2026":
        if sheet:
            st.dataframe(sheet.get_all_records())
