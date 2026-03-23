import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. KONFIGURACIJA
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")

# Stil za lepše gumbe
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #0e1117; color: white; border: 1px solid #444; }
    .stButton>button:hover { border-color: #fff; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA
@st.cache_resource
def povezi_tabelo():
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except:
        return None

sheet = povezi_tabelo()

# 3. LOGIKA KORAKOV
if "korak" not in st.session_state:
    st.session_state.korak = 1

# --- KORAK 1: ZAČETEK ---
if st.session_state.korak == 1:
    st.markdown("### Dobrodošli")
    if st.button("NAROČI SE NA TERMIN"):
        st.session_state.korak = 2
        st.rerun()

# --- KORAK 2: VNOS IN IZBIRA STORITVE ---
elif st.session_state.korak == 2:
    st.markdown("### Podatki in storitev")
    ime = st.text_input("Ime in priimek")
    tel = st.text_input("Telefonska številka")
    
    # NOVA MOŽNOST: Izbira storitve
    storitev = st.radio("Izberite storitev:", ["Frizura", "Brada", "Oboje"])
    
    datum = st.date_input("Izberite datum", min_value=datetime.today())
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("NAZAJ"):
            st.session_state.korak = 1
            st.rerun()
    with col2:
        if st.button("NADALJUJ"):
            if ime and tel:
                st.session_state.podatki = {
                    "ime": ime, 
                    "tel": tel, 
                    "storitev": storitev, 
                    "datum": str(datum)
                }
                st.session_state.korak = 3
                st.rerun()
            else:
                st.warning("Izpolnite vsa polja.")

# --- KORAK 3: KONČNA POTRDITEV ---
elif st.session_state.korak == 3:
    p = st.session_state.podatki
    st.markdown("### Preverite podatke")
    st.write(f"**Stranka:** {p['ime']}")
    st.write(f"**Telefon:** {p['tel']}")
    st.write(f"**Storitev:** {p['storitev']}")
    st.write(f"**Datum:** {p['datum']}")
    
    if st.button("POTRDI REZERVACIJO"):
        if sheet:
            sheet.append_row([p['ime'], p['tel'], p['storitev'], p['datum'], "Novo"])
            st.success("Rezervacija uspešna!")
            if st.button("NA DOMOV"):
                st.session_state.korak = 1
                st.rerun()
        else:
            st.error("Baza ni dosegljiva.")

st.markdown("---")

# 4. ADMIN DEL (Z gumbom za brisanje)
with st.expander("🔐 Admin"):
    geslo = st.text_input("Geslo", type="password")
    if geslo == "brivnica2026":
        if sheet:
            st.markdown("#### Seznam rezervacij")
            podatki = sheet.get_all_records()
            if podatki:
                st.dataframe(podatki)
                
                # Gumb za brisanje tabele (da lahko sprazniš seznam)
                if st.button("POČISTI CELOTEN SEZNAM (Reset)"):
                    # Pusti prvo vrstico (naslove), ostalo pobriše
                    sheet.resize(rows=1)
                    sheet.resize(rows=100)
                    st.success("Seznam je bil spraznjen.")
                    st.rerun()
            else:
                st.write("Ni novih rezervacij.")

st.caption("© 2026 Kavčič Cuts")
