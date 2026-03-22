import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# 1. NASTAVITVE STRANI IN DIZAJN
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")

# Logotip (če nimaš slike image_2.png na GitHubu, se ta del preskoči)
try:
    st.image("image_2.png", width=200)
except:
    pass

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA Z GOOGLE TABLES
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    # Prepričaj se, da se tvoja tabela imenuje točno tako!
    sheet = client.open("BarberBooking").get_worksheet(0)
except Exception as e:
    st.error("Napaka pri povezavi z bazo. Preveri creds.json in dostop do tabele.")
    st.stop()

# 3. DEL ZA STRANKE - REZERVACIJA
st.header("✂️ Rezervacija termina")

with st.form("booking_form"):
    ime = st.text_input("Ime in priimek")
    telefon = st.text_input("Telefonska številka")
    datum = st.date_input("Izberi datum", min_value=datetime.today())
    
    submit = st.form_submit_button("Preveri razpoložljive termine")

if submit:
    if ime and telefon:
        # Tukaj bova kasneje dodala še logiko za ure, zaenkrat samo potrdilo
        st.success(f"Hvala {ime}! Preverjamo termine za {datum}. (Tukaj kmalu sledi izbira ur)")
    else:
        st.warning("Prosimo, izpolni vsa polja.")

st.markdown("---")

# 4. ADMIN DEL - POSPRAVLJEN NA DNO
with st.expander("🔐 Admin (samo za lastnika)"):
    geslo = st.text_input("Vnesi geslo", type="password")
    if geslo == "brivnica2026":  # Tukaj si lahko spremeniš geslo
        st.write("### Pregled današnjih rezervacij")
        podatki = sheet.get_all_records()
        if podatki:
            st.table(podatki)
        else:
            st.info("Danes še ni rezervacij.")
