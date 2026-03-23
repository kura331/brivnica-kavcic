import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64

# 1. KONFIGURACIJA
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️", layout="centered")

# --- Funkcija za pretvorbo slike v base64 ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

# Naloži simbol (mora biti v istem mapi kot app.py)
barber_pole = get_base64('barber_pole.png')

# --- IZBOLJŠAN STIL (Manj temno, bolj čisto) ---
st.markdown(f"""
    <style>
    /* Animirano ozadje */
    [data-testid="stAppViewContainer"] {{
        background-color: #f0f2f6; /* Svetlejša osnova namesto črne */
        background-image: url("data:image/png;base64,{barber_pole}");
        background-repeat: repeat;
        background-size: 80px 160px;
        animation: barberSlide 80s linear infinite;
    }}

    @keyframes barberSlide {{
        from {{ background-position: 0 0; }}
        to {{ background-position: 500px 1000px; }}
    }}

    /* Svetlejši in čistejši osrednji del */
    [data-testid="stVerticalBlock"] {{
        background-color: white; /* Bela podlaga za obrazec */
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: #1f1f1f;
    }}

    /* Gumbi */
    .stButton>button {{
        width: auto;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        background-color: #1f1f1f;
        color: white;
        border: none;
        transition: 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: #444;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA
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

# --- KORAK 1 ---
if st.session_state.korak == 1:
    st.subheader("Dobrodošli")
    if st.button("NAROČI SE NA TERMIN"):
        st.session_state.korak = 2
        st.rerun()

# --- KORAK 2 ---
elif st.session_state.korak == 2:
    st.subheader("Vaši podatki")
    ime = st.text_input("Ime in priimek")
    tel = st.text_input("Telefon")
    
    # TRI OPCIJE, KI SI JIH ŽELEL
    storitev = st.selectbox("Kaj želite?", ["Frizura", "Brada", "Oboje"])
    
    datum = st.date_input("Datum", min_value=datetime.today())
    
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("NAZAJ"):
            st.session_state.korak = 1
            st.rerun()
    with col2:
        if st.button("NADALJUJ"): #
            if ime and tel:
                st.session_state.p = {"ime": ime, "tel": tel, "storitev": storitev, "datum": str(datum)}
                st.session_state.korak = 3
                st.rerun()
            else:
                st.warning("Vpiši podatke.")

# --- KORAK 3 ---
elif st.session_state.korak == 3:
    p = st.session_state.p
    st.subheader("Potrditev")
    st.write(f"**Storitev:** {p['storitev']}")
    st.write(f"**Datum:** {p['datum']}")
    
    if st.button("POTRDI"):
        if sheet:
            sheet.append_row([p['ime'], p['tel'], p['storitev'], p['datum']])
            st.success("Rezervirano!")
            if st.button("DOMOV"):
                st.session_state.korak = 1
                st.rerun()

st.markdown("---")
# ADMIN DEL
with st.expander("🔐 Admin"):
    if st.text_input("Geslo", type="password") == "brivnica2026": #
        if sheet:
            st.dataframe(sheet.get_all_records())

st.caption("© 2026 Kavčič Cuts")
