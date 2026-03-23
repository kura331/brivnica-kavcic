import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. DIZAJN: Črna tema in gumbi z belim robom
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    [data-testid="stVerticalBlock"] {
        background-color: #111111 !important;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #333;
    }
    /* Stil gumba: Črn z belim robom */
    .stButton>button {
        width: 100% !important;
        background-color: #000000 !important;
        color: white !important;
        border: 1px solid #ffffff !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }
    h1, h2, h3, p, label { color: white !important; }
    input, select, .stSelectbox div {
        background-color: #000000 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA: Popravek za PEM napako
@st.cache_resource
def povezi():
    try:
        # Prebere celoten "service account" iz Streamlit Secrets
        info = dict(st.secrets["gcp_service_account"])
        
        # Ključni popravek za "Unable to load PEM file"
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
            
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        
        # Odpre tabelo z imenom BarberBooking
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except Exception as e:
        st.error(f"Povezava ni uspela: {e}")
        return None

sheet = povezi()

if "korak" not in st.session_state:
    st.session_state.korak = 1

# 3. KORAKI NAROČANJA
if st.session_state.korak == 1:
    st.markdown("### Dobrodošli")
    if st.button("NAROČI SE NA TERMIN"):
        st.session_state.korak = 2
        st.rerun()

elif st.session_state.korak == 2:
    st.markdown("### Podatki za termin")
    ime = st.text_input("Ime in priimek")
    tel = st.text_input("Telefon")
    storitev = st.selectbox("Izberite storitev:", ["Frizura", "Brada", "Oboje"])
    datum = st.date_input("Datum", min_value=datetime.today())
    
    if st.button("NADALJUJ"):
        if ime and tel:
            st.session_state.p = {"ime": ime, "tel": tel, "storitev": storitev, "datum": str(datum)}
            st.session_state.korak = 3
            st.rerun()
        else:
            st.warning("Prosimo, izpolni vsa polja.")

elif st.session_state.korak == 3:
    p = st.session_state.p
    st.write(f"**Stranka:** {p['ime']} | **Storitev:** {p['storitev']}")
    if st.button("POTRDI REZERVACIJO"):
        if sheet:
            sheet.append_row([p['ime'], p['tel'], p['storitev'], p['datum']])
            st.success("Rezervacija uspešna!")
            if st.button("DOMOV"):
                st.session_state.korak = 1
                st.rerun()

st.markdown("---")

# 4. ADMIN: Novo geslo kavciccutsadmin0
with st.expander("🔐 Admin"):
    vpisano = st.text_input("Geslo", type="password")
    if vpisano == "kavciccutsadmin0": #
        if sheet:
            st.dataframe(sheet.get_all_records())
            if st.button("OSVEŽI (NADALJUJ)"):
                st.rerun()
        else:
            st.error("Ni povezave s tabelo.") #

st.caption("© 2026 Kavčič Cuts")
