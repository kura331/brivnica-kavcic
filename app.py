import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64

# 1. KONFIGURACIJA
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️", layout="centered")

# Funkcija za varno nalaganje slike in pretvorbo v ozadje
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

barber_img = get_base64('barber_pole.png')
# Če slike še nisi naložil, bo ozadje ostalo črno
img_url = f"data:image/png;base64,{barber_img}" if barber_img else ""

# --- CSS ZA ČRNO TEMO, DROBNE POLI IN GUMBE ---
st.markdown(f"""
    <style>
    /* Temno osnovno ozadje */
    .stApp {{
        background-color: #000000 !important;
    }}
    
    /* Animirano ozadje z DROBNIMI simboli */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("{img_url}") !important;
        background-repeat: repeat !important;
        background-size: 40px 80px !important; /* Tukaj jih naredimo drobne! */
        opacity: 0.12 !important; /* Zelo subtilno */
        animation: barberSlide 60s linear infinite !important;
        z-index: -1;
    }}

    @keyframes barberSlide {{
        from {{ background-position: 0 0; }}
        to {{ background-position: 500px 1000px; }}
    }}

    /* Glavni blok obrazca - prosojen, da se vidi ozadje */
    [data-testid="stVerticalBlock"] {{
        background-color: rgba(20, 20, 20, 0.7) !important;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #333;
    }}

    /* VSI GUMBI ČRNI Z BELIM ROBOM */
    .stButton>button {{
        width: 100% !important;
        background-color: #000000 !important;
        color: white !important;
        border: 1px solid #ffffff !important;
        font-weight: bold !important;
        text-transform: uppercase;
        border-radius: 4px;
        transition: 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: #222 !important;
        border-color: #aaa !important;
    }}

    /* Teksti v beli */
    h1, h2, h3, p, label, .stMarkdown {{
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA (Z odpravo PEM napake)
@st.cache_resource
def povezi():
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n") # Popravek za PEM
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except Exception as e:
        return None

sheet = povezi()

# 3. GLAVNA LOGIKA
if "korak" not in st.session_state:
    st.session_state.korak = 1

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
    datum = st.date_input("Datum", min_value=datetime.today())
    
    if st.button("NADALJUJ"): #
        if ime and tel:
            st.session_state.p = {"ime": ime, "tel": tel, "storitev": storitev, "datum": str(datum)}
            st.session_state.korak = 3
            st.rerun()

elif st.session_state.korak == 3:
    p = st.session_state.p
    st.write(f"**Stranka:** {p['ime']} | **Storitev:** {p['storitev']}")
    if st.button("POTRDI REZERVACIJO"):
        if sheet:
            sheet.append_row([p['ime'], p['tel'], p['storitev'], p['datum']])
            st.success("Rezervirano!")
            if st.button("DOMOV"):
                st.session_state.korak = 1
                st.rerun()

st.markdown("---")

# 4. ADMIN DEL Z GUMBOM
with st.expander("🔐 Admin"): #
    geslo = st.text_input("Geslo", type="password") #
    if geslo == "brivnica2026": #
        if sheet:
            st.dataframe(sheet.get_all_records())
            if st.button("OSVEŽI / NADALJUJ"): # Gumb v adminu
                st.rerun()
        else:
            st.error("Napaka pri povezavi s tabelo.")

st.caption("© 2026 Kavčič Cuts")
