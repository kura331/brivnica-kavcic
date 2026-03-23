import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64

# 1. KONFIGURACIJA IN STILIZACIJA
st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️", layout="centered")

# --- Funkcija za pretvorbo slike v base64 ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- Naloži brivski simbol ---
# Predpostavljamo, da je slika barber stebra shranjena kot 'barber_pole.png'
try:
    barber_pole_base64 = get_base64_of_bin_file('barber_pole.png') #
except FileNotFoundError:
    # Če slike ni, uporabimo prazen placeholder, da koda ne crkne
    barber_pole_base64 = ""
    st.warning("Datoteka 'barber_pole.png' ni najdena. Ozadje bo prazno.")

# --- CSS za animirano ozadje in gumb ---
st.markdown(f"""
    <style>
    /* Animirano ozadje z barber simboli */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{barber_pole_base64}");
        background-repeat: repeat;
        background-size: 100px 200px; /* Prilagodi velikost vzorca */
        opacity: 0.1; /* Zelo prosojno, da ne moti branja */
        animation: barberSlide 60s linear infinite; /* Zelo počasi */
    }}

    @keyframes barberSlide {{
        from {{ background-position: 0 0; }}
        to {{ background-position: 500px 1000px; }} /* Smer diagonale pod ~45° */
    }}

    /* Stilizacija glavnega vsebnika za boljšo berljivost */
    [data-testid="stVerticalBlock"] {{
        background-color: rgba(14, 17, 23, 0.85); /* Temno ozadje z malo prosojnosti */
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #333;
    }}

    /* Stilizacija gumba NADALJUJ (manjši, umeščen) */
    .stButton>button {{
        width: auto; /* Ni več čez celo širino */
        padding: 0.5rem 2rem;
        border-radius: 5px;
        background-color: transparent;
        color: #fff;
        border: 1px solid #444;
        font-family: inherit;
        transition: all 0.3s ease;
        display: block;
        margin-left: auto; /* Poravna desno znotraj kolone */
        margin-right: 0;
    }}
    
    .stButton>button:hover {{
        border-color: #fff;
        color: #fff;
        background-color: rgba(255, 255, 255, 0.1);
    }}

    /* Popravek za napis NADALJUJ */
    .stButton>button div p {{
        color: #fff !important;
        font-weight: normal !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Glavni naslov
st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")
st.markdown("---")

# 2. POVEZAVA Z GIP
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
    
    # Uporabimo form za boljšo kontrolo nad gumbi
    with st.form("booking_form"):
        ime = st.text_input("Ime in priimek")
        tel = st.text_input("Telefonska številka")
        storitev = st.radio("Izberite storitev:", ["Frizura", "Brada", "Oboje"], horizontal=True)
        datum = st.date_input("Izberite datum", min_value=datetime.today())
        
        # Ustvarimo kolone za gumbe NAZAJ in NADALJUJ
        col_nazaj, col_prostor, col_nadaljuj = st.columns([1, 2, 1])
        
        with col_nazaj:
            # Gumb NAZAJ v formi ne deluje s session_state direktno, 
            # zato ga pustimo zunaj ali pa uporabimo submit
            submit_nazaj = st.form_submit_button("NAZAJ")
            
        with col_nadaljuj:
            # Stiliziran gumb NADALJUJ znotraj forme
            submit_nadaljuj = st.form_submit_button("NADALJUJ") #

    # Logika po pritisku gumbov v formi
    if submit_nazaj:
        st.session_state.korak = 1
        st.rerun()
        
    if submit_nadaljuj:
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
            st.warning("Prosimo, izpolnite vsa polja.")

# --- KORAK 3: KONČNA POTRDITEV ---
elif st.session_state.korak == 3:
    p = st.session_state.podatki
    st.markdown("### Preverite podatke")
    st.write(f"**Stranka:** {p['ime']}")
    st.write(f"**Telefon:** {p['tel']}")
    st.write(f"**Storitev:** {p['storitev']}")
    st.write(f"**Datum:** {p['datum']}")
    st.markdown("---")
    
    col_potrdi_nazaj, col_potrdi = st.columns([1, 1])
    with col_potrdi_nazaj:
        if st.button("UREDI"):
            st.session_state.korak = 2
            st.rerun()
            
    with col_potrdi:
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

# 4. ADMIN DEL
with st.expander("🔐 Admin"): #
    geslo = st.text_input("Geslo", type="password") #
    if geslo == "brivnica2026": #
        if sheet:
            st.markdown("#### Seznam rezervacij")
            podatki = sheet.get_all_records()
            if podatki:
                st.dataframe(podatki)
            else:
                st.write("Ni novih rezervacij.")
