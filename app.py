import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. KONFIGURACIJA
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")

# Glavni naslov in lokacija
st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. VARNA POVEZAVA
def poveži_tabelo():
    try:
        # Preberemo Secrets
        info = dict(st.secrets["gcp_service_account"])
        
        # Popravek za PEM napako
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
            
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("BarberBooking").get_worksheet(0)
    except:
        return None

sheet = poveži_tabelo()

if sheet:
    # 3. OBRAZEC ZA STRANKE
    st.markdown("### Rezervacija termina")
    with st.form("rezervacija", clear_on_submit=True):
        ime = st.text_input("Ime in priimek")
        tel = st.text_input("Telefon")
        datum = st.date_input("Datum", min_value=datetime.today())
        
        submit = st.form_submit_button("POTRDI")

        if submit:
            if ime and tel:
                sheet.append_row([ime, tel, str(datum), "Novo"])
                st.success(f"Rezervacija za {ime} je oddana.")
            else:
                st.warning("Prosimo, vnesite vse podatke.")
else:
    # Napaka, če poverilnice niso pravilne
    st.error("Sistem se osvežuje. Poskusite ponovno čez trenutek.")

st.markdown("---")

# 4. ADMIN DEL (Z napisom Admin)
with st.expander("🔐 Admin"):
    koda = st.text_input("Vnesite admin kodo", type="password")
    if koda == "brivnica2026":
        if sheet:
            st.markdown("#### Pregled vseh rezervacij")
            st.dataframe(sheet.get_all_records())

st.caption("© 2026 Kavčič Cuts")
