import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64

# 1. KONFIGURACIJA
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️", layout="centered")

# --- Funkcija za ozadje ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        # Če tvoje slike ni, uporabi tole privzeto (rezervni plan)
        return ""

barber_img = get_base64('barber_pole.png')
# Če nimaš svoje slike, uporabi URL do simbola
img_url = f"data:image/png;base64,{barber_img}" if barber_img else "https://cdn-icons-png.flaticon.com/512/1010/1010775.png"

# --- CSS ZA ČRNO TEMO IN ANIMACIJO ---
st.markdown(f"""
    <style>
    /* Črno glavno ozadje */
    [data-testid="stAppViewContainer"] {{
        background-color: #000000;
    }}

    /* Animirana plast z barber simboli */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("{img_url}");
        background-repeat: repeat;
        background-size: 70px 140px;
        opacity: 0.15; /* Subtilno vidni simboli */
        animation: barberSlide 50s linear infinite;
        pointer-events: none;
    }}

    @keyframes barberSlide {{
        from {{ background-position: 0 0; }}
        to {{ background-position: 500px 1000px; }}
    }}

    /* Sredinski del - zdaj TEMEN z robom */
    [data-testid="stVerticalBlock"] {{
        background-color: rgba(20, 20, 20, 0.8); /* Skoraj črna, rahlo prosojna */
        padding: 2.5rem;
        border-radius: 15px;
        border: 1px solid #333;
        color: white;
    }}

    /* Naslovi in teksti v beli */
    h1, h2, h3, p, label, .stMarkdown {{
        color: white !important;
    }}

    /* Gumbi */
    .stButton>button {{
        width: auto;
        padding: 0.4rem 1.5rem;
        border-radius: 4px;
        background-color: #ffffff;
        color: #000000;
        border: none;
        font-weight: bold;
    }}
    
    .stButton>button:hover {{
        background-color: #cccccc;
    }}

    /* Input polja naj bodo temna */
    input, select, .stSelectbox {{
        background-color: #111 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA (GIP)
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

# --- LOGIKA KORAKOV ---
if st.session_state.korak == 1:
    st.subheader("Dobrodošli")
    if st.button("NAROČI SE NA TERMIN"):
        st.session_state.korak = 2
        st.rerun()

elif st.session_state.korak == 2:
    st.subheader("Vpišite podatke")
    ime = st.text_input("Ime in priimek")
    tel = st.text_input("Telefon")
    storitev = st.selectbox("Izberite storitev:", ["Frizura", "Brada", "Oboje"])
    datum = st.date_input("Izberite datum", min_value=datetime.today())
    
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("NAZAJ"):
            st.session_state.korak = 1
            st.rerun()
    with col2:
        if st.button("NADALJUJ"):
            if ime and tel:
                st.session_state.p = {"ime": ime, "tel": tel, "storitev": storitev, "datum": str(datum)}
                st.session_state.korak = 3
                st.rerun()
            else:
                st.warning("Manjkajo podatki!")

elif st.session_state.korak == 3:
    p = st.session_state.p
    st.subheader("Potrditev")
    st.write(f"**Stranka:** {p['ime']}")
    st.write(f"**Storitev:** {p['storitev']}")
    st.write(f"**Datum:** {p['datum']}")
    
    if st.button("POTRDI REZERVACIJO"):
        if sheet:
            sheet.append_row([p['ime'], p['tel'], p['storitev'], p['datum']])
            st.success("Uspešno rezervirano!")
            if st.button("NAZAJ NA DOMOV"):
                st.session_state.korak = 1
                st.rerun()

st.markdown("---")
# ADMIN
with st.expander("🔐 Admin"):
    if st.text_input("Geslo", type="password") == "brivnica2026":
        if sheet:
            st.dataframe(sheet.get_all_records())

st.caption("© 2026 Kavčič Cuts")
