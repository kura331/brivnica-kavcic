import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. KONFIGURACIJA
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")

# Glavni naslov brez nepotrebnih podnapisov
st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA (Očiščena vseh napak iz prejšnjih slik)
def poveži_tabelo():
    try:
        # Preberemo Secrets kot slovar
        info = dict(st.secrets["gcp_service_account"])
        
        # Popravek za PEM napako (MalformedFraming)
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
            
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("BarberBooking").get_worksheet(0)
    except:
        return None

# Izvedba povezave
sheet = poveži_tabelo()

if sheet:
    # 3. REZERVACIJSKI OBRAZEC
    with st.form("rezervacija", clear_on_submit=True):
        st.markdown("### Rezervacija termina")
        ime = st.text_input("Ime in priimek")
        tel = st.text_input("Telefon")
        datum = st.date_input("Datum", min_value=datetime.today())
        
        submit = st.form_submit_button("POTRDI")

        if submit:
            if ime and tel:
                sheet.append_row([ime, tel, str(datum), "Novo"])
                st.success(f"Termin za {ime} je zabeležen.")
            else:
                st.warning("Vnesite podatke.")
else:
    # Prikaz napake, če ključi niso pravi
    st.error("Sistem trenutno ni dosegljiv. Preveri Secrets.")

st.markdown("---")

# 4. ADMIN (Skrit spodaj)
with st.expander("🔐"):
    if st.text_input("Koda", type="password") == "brivnica2026":
        if sheet:
            st.dataframe(sheet.get_all_records())

st.caption("© 2026 Kavčič Cuts")
