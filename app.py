import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64

# 1. KONFIGURACIJA
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️", layout="centered")

# Funkcija za pretvorbo slike v base64 (za ozadje)
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

# Tvoj logotip na GitHubu
barber_img = get_base64('logo.png')
img_url = f"data:image/png;base64,{barber_img}" if barber_img else ""

# --- CSS ZA ČRNO TEMO, ANIMACIJO LOGOTOPOV IN GUMBE ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #000000 !important;
    }}
    
    /* Animirano ozadje s TVOJIMI LOGOTIPI */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("{img_url}") !important;
        background-repeat: repeat !important;
        background-size: 60px 120px !important; /* Drobni logotipi */
        opacity: 0.15 !important;
        animation: barberSlide 60s linear infinite !important;
        z-index: -1;
    }}

    @keyframes barberSlide {{
        from {{ background-position: 0 0; }}
        to {{ background-position: 500px 1000px; }}
    }}

    /* Osrednji blok obrazca */
    [data-testid="stVerticalBlock"] {{
        background-color: rgba(20, 20, 20, 0.8) !important;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #444;
    }}

    /* ČRNI GUMBI Z BELIM ROBOM */
    .stButton>button {{
        width: 100% !important;
        background-color: #000000 !important;
        color: white !important;
        border: 1px solid #ffffff !important;
        font-weight: bold !important;
        text-transform: uppercase;
        margin-top: 10px;
    }}
    
    .stButton>button:hover {{
        background-color: #222 !important;
        border-color: #aaa !important;
    }}

    h1, h2, h3, p, label {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA Z GOOGLE TABELO
@st.cache_resource
def povezi():
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except:
        return None

sheet = povezi()

if "korak" not in st.session_state:
    st.session_state.korak = 1

# 3. KORAKI REZERVACIJE
if st.session_state.korak == 1:
    st.markdown("### Dobrodošli")
    if st.button("NAROČI SE NA TERMIN"):
        st.session_state.korak = 2
        st.rerun()

elif st.session_state.korak == 2:
    st.markdown("### Podatki")
    ime = st.text_input("Ime in priimek")
    tel = st.text_input("Telefon")
    storitev = st.selectbox("Izberite storitev:", ["Frizura", "Brada", "Oboje"])
    datum = st.date_input("Izberite datum", min_value=datetime.today())
    
    if st.button("NADALJUJ"):
        if ime and tel:
            st.session_state.p = {"ime": ime, "tel": tel, "storitev": storitev, "datum": str(datum)}
            st.session_state.korak = 3
            st.rerun()
        else:
            st.warning("Prosimo, izpolnite vsa polja.")

elif st.session_state.korak == 3:
    p = st.session_state.p
    st.write(f"**Stranka:** {p['ime']} | **Storitev:** {p['storitev']}")
    if st.button("POTRDI REZERVACIJO"):
        if sheet:
            sheet.append_row([p['ime'], p['tel'], p['storitev'], p['datum']])
            st.success("Rezervacija uspešna!")
            if st.button("NAZAJ NA DOMOV"):
                st.session_state.korak = 1
                st.rerun()

st.markdown("---")

# 4. ADMIN DEL Z GUMBOM NADALJUJ
with st.expander("🔐 Admin"):
    geslo = st.text_input("Geslo", type="password")
    if geslo == "brivnica2026": #
        if sheet:
            st.markdown("#### Seznam rezervacij")
            podatki = sheet.get_all_records()
            if podatki:
                st.dataframe(podatki)
                # GUMB NADALJUJ V ADMINU
                if st.button("NADALJUJ (OSVEŽI)"):
                    st.rerun()
            else:
                st.write("Ni novih rezervacij.")
        else:
            st.error("Napaka pri povezavi s tabelo.")

st.caption("© 2026 Kavčič Cuts")
