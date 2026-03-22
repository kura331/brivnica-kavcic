import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. NASTAVITVE STRANI
st.set_page_config(page_title="Kavčič Cuts | Rezervacije", page_icon="✂️")

# Stilski popravek za bolj resen videz (brez odvečnega okraševanja)
st.title("KAVČIČ CUTS")
st.subheader("Moško striženje in urejanje brade")
st.info("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. FUNKCIJA ZA POVEZAVO
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = dict(st.secrets["gcp_service_account"])
    
    # Čiščenje ključa za preprečevanje napak
    raw_key = creds_info["private_key"]
    clean_key = raw_key.replace("\\n", "\n").replace(r"\n", "\n")
    creds_info["private_key"] = clean_key
    
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    sheet = client.open("BarberBooking").get_worksheet(0)
    
    # 3. OBRAZEC ZA REZERVACIJO
    st.markdown("### Rezervacija termina")
    st.write("Prosimo, vnesite svoje podatke za rezervacijo. Kontaktirali vas bomo za potrditev ure.")
    
    with st.form("booking_form", clear_on_submit=True):
        ime = st.text_input("Ime in priimek")
        telefon = st.text_input("Telefonska številka")
        datum = st.date_input("Želeni datum", min_value=datetime.today())
        
        submit = st.form_submit_button("ODDAJ REZERVACIJO")

    if submit:
        if ime and telefon:
            # Zapis v bazo
            sheet.append_row([ime, telefon, str(datum), "Novo naročilo"])
            st.success(f"Sprejeto. Rezervacija na ime {ime} za datum {datum} je bila uspešno oddana.")
            # Baloni so odstranjeni za bolj resen videz
        else:
            st.error("Napaka: Prosimo, izpolnite vsa obvezna polja (ime in telefon).")

    st.markdown("---")
    
    # ADMIN DEL (Diskretno spodaj)
    with st.expander("🔐 Administracija"):
        if st.text_input("Vnesite geslo", type="password") == "brivnica2026":
            podatki = sheet.get_all_records()
            if podatki:
                st.write("Pregled rezervacij:")
                st.dataframe(podatki) # Dataframe izgleda bolj profesionalno kot navadna tabela
            else:
                st.write("Trenutno ni zabeleženih rezervacij.")

except Exception as e:
    st.warning("Povezava s sistemom se vzpostavlja...")
    # Izpis napake samo za admina (v kodi)
    # st.write(str(e))

st.caption("© 2024 Kavčič Cuts. Vse pravice pridržane.")
