import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. NASTAVITVE STRANI IN IZGLED
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")

# Črna tema in beli gumbi
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .stButton>button { background-color: #111; color: white; border: 1px solid white; border-radius: 5px; }
    input { background-color: #222 !important; color: white !important; border: 1px solid #444 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")

# 2. POVEZAVA Z GOOGLE TABELO
@st.cache_resource
def povezi_tabelo():
    try:
        s = st.secrets["gcp_service_account"]
        
        # Popravek za PEM ključ (rešitev za rdečo napako)
        pk = s["private_key"].replace("\\n", "\n")
        
        credentials_info = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        creds = Credentials.from_service_account_info(
            credentials_info, 
            scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
        # Odpre tabelo BarberBooking
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except Exception as e:
        st.error(f"Povezava ni uspela. Preveri Secrets in deljenje tabele. Napaka: {e}")
        return None

sheet = povezi_tabelo()

# 3. UPORABNIŠKI VMESNIK
st.markdown("---")
if st.button("NAROČI SE NA TERMIN"):
    st.session_state.narocanje = True

if st.session_state.get("narocanje"):
    with st.form("rezervacija_form"):
        ime = st.text_input("Ime in priimek")
        tel = st.text_input("Telefonska številka")
        oddaj = st.form_submit_button("POTRDI REZERVACIJO")
        
        if oddaj:
            if sheet and ime and tel:
                datum = datetime.now().strftime("%d.%m.%Y %H:%M")
                sheet.append_row([ime, tel, "Moško striženje", datum])
                st.success(f"Hvala {ime}! Rezervacija je potrjena.")
                st.session_state.narocanje = False
            else:
                st.error("Prosim izpolni vsa polja.")

# 4. ADMIN DEL
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🔐 Admin"):
    vpisano_geslo = st.text_input("Vnesi geslo", type="password")
    if vpisano_geslo == "kavciccutsadmin0":
        if sheet:
            st.write("Pregled rezervacij:")
            st.table(sheet.get_all_records())
        else:
            st.error("Ni povezave s tabelo.")

# 5. NOGA (FOOTER) - DODANO PO TVOJI ŽELJI
st.markdown("---")
st.caption("© 2026 Kavčič Cuts")
with st.expander("🔐
