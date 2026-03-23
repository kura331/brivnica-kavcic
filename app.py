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
        return ""

barber_img = get_base64('barber_pole.png')
# Če nimaš svoje slike, koda uporabi ta spletni simbol, da vidiš efekt
img_url = f"data:image/png;base64,{barber_img}" if barber_img else "https://cdn-icons-png.flaticon.com/512/1010/1010775.png"

# --- CSS ZA ČRNO TEMO, ČRNE GUMBE IN VIDNO ANIMACIJO ---
st.markdown(f"""
    <style>
    /* Črno glavno ozadje */
    [data-testid="stAppViewContainer"] {{
        background-color: #000000 !important;
    }}

    /* Animirana plast v ozadju - nujno pred vsem ostalim */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("{img_url}");
        background-repeat: repeat;
        background-size: 80px 160px;
        opacity: 0.2; /* Tukaj nastaviš, kako močno se vidijo simboli */
        animation: barberSlide 40s linear infinite;
        z-index: 0;
    }}

    @keyframes barberSlide {{
        from {{ background-position: 0 0; }}
        to {{ background-position: 500px 1000px; }}
    }}

    /* Sredinski del - narejen prosojno, da se vidi ozadje! */
    [data-testid="stVerticalBlock"] {{
        background-color: rgba(30, 30, 30, 0.6) !important; /* Prosojna črna */
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #444;
        z-index: 1;
    }}

    /* GUMB NAREJEN ČRNO (z belim robom, da se vidi) */
    .stButton>button {{
        width: 100%;
        padding: 0.6rem;
        border-radius: 5px;
        background-color: #000000 !important; /* Črn gumb */
        color: white !important;
        border: 1px solid #ffffff !important; /* Bel rob za kontrast */
        font-weight: bold;
        text-transform: uppercase;
    }}
    
    .stButton>button:hover {{
        background-color: #222222 !important;
        border-color: #cccccc !important;
    }}

    /* Teksti v beli barvi */
    h1, h2, h3, p, label {{
        color: white !important;
    }}
    
    /* Popravek za vnosna polja */
    input, select, .stSelectbox div {{
        background-color: #111 !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA Z GOOGLE SHEETS
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
    st.markdown("### Dobrodošli")
    # Gumb je zdaj črn z belim robom
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
            st.warning("Izpolni vse.")

elif st.session_state.korak == 3:
    p = st.session_state.p
    st.markdown("### Potrditev")
    st.write(f"Stranka: {p['ime']}")
    st.write(f"Storitev: {p['storitev']}")
    
    if st.button("POTRDI"):
        if sheet:
            sheet.append_row([p['ime'], p['tel'], p['storitev'], p['datum']])
            st.success("Rezervirano!")
            if st.button("DOMOV"):
                st.session_state.korak = 1
                st.rerun()

st.markdown("---")
with st.expander("🔐 Admin"): #
    if st.text_input("Geslo", type="password") == "brivnica2026": #
        if sheet:
            st.dataframe(sheet.get_all_records())

st.caption("© 2026 Kavčič Cuts")
