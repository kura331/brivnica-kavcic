import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import base64

# --- KONFIGURACIJA ---
ADMIN_PASSWORD = "kavciccutsadmin" 
SHEET_NAME = "BarberBooking"

def get_google_sheet():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds = Credentials.from_service_account_file("creds.json", scopes=scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except:
        return None

st.set_page_config(page_title="Kavcic Cuts", page_icon="✂️", layout="centered")

# Nalaganje slike za ozadje
encoded_string = ""
try:
    with open("image_2.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
except:
    pass

# --- POPRAVLJEN CSS ---
st.markdown(f"""
    <style>
    .stApp {{ 
        background-color: #000000; 
        color: #ffffff;
        background-image: url("data:image/png;base64,{encoded_string}");
        background-repeat: no-repeat;
        background-position: center 20%;
        background-size: 60%;
        background-blend-mode: overlay;
    }}
    .block-container {{ background-color: rgba(0,0,0, 0.7); padding: 20px; border-radius: 10px; }}
    h1 {{ color: #ffffff; text-align: center; letter-spacing: 2px; }}
    .address-box {{ border-bottom: 1px solid #333; padding: 20px; text-align: center; margin-bottom: 30px; color: #888; }}
    .service-item {{ border-bottom: 1px solid #333; padding: 15px 0; display: flex; justify-content: space-between; align-items: center; }}
    .service-info {{ font-size: 18px; font-weight: bold; }}
    .service-details {{ font-size: 14px; color: #888; font-weight: normal; }}
    div[data-testid="stHorizontalBlock"] button {{ background-color: transparent; color: white; border: 1px solid #333; border-radius: 5px; height: 3em; margin-bottom: 10px; }}
    .stButton>button {{ width: 100%; background-color: #ffffff; color: #000000; font-weight: bold; border-radius: 5px; height: 3.5em; margin-top: 20px; }}
    </style>
    """, unsafe_allow_html=True)

st.title("KAVCIC CUTS")
st.markdown('<div class="address-box">📍 Šegova ulica 14, Novo mesto</div>', unsafe_allow_html=True)

sheet = get_google_sheet()

if sheet:
    try:
        data = sheet.get_all_values()
        booked_slots = [f"{row[1]} {row[2]}" for row in data[1:]] 

        st.write("### Izberite storitev")
        st.markdown('<div class="service-item"><div class="service-info">Frizura<br><span class="service-details">45 minut • 20,00 €</span></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="service-item"><div class="service-info">Brada<br><span class="service-details">30 minut • 15,00 €</span></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="service-item"><div class="service-info">Komplet (Frizura & Brada)<br><span class="service-details">1 ura, 15 minut • 35,00 €</span></div></div>', unsafe_allow_html=True)
        
        storitev = st.radio("Potrdi izbiro:", ["Frizura", "Brada", "Komplet"], label_visibility="collapsed")

        st.write("---")
        st.write("### Izberite termin")
        datum = st.date_input("Datum:", min_value=datetime.today())
        
        all_slots = ["14:05", "14:50"]
        available_slots = [u for u in all_slots if f"{str(datum)} {u}" not in booked_slots]

        if not available_slots:
            st.warning("Zasedeno.")
        else:
            col1, col2 = st.columns(2)
            if 'selected_time' not in st.session_state: st.session_state.selected_time = None

            with col1:
                if "14:05" in available_slots:
                    if st.button("14:05"): st.session_state.selected_time = "14:05"
                else: st.button("14:05 (X)", disabled=True)
            with col2:
                if "14:50" in available_slots:
                    if st.button("14:50"): st.session_state.selected_time = "14:50"
                else: st.button("14:50 (X)", disabled=True)

        if st.session_state.selected_time:
            st.write(f"Izbrano: **{st.session_state.selected_time}**")
            ime = st.text_input("Ime:")
            tel = st.text_input("Telefon:")
            if st.button("NAROČITE SE"):
                if ime and tel:
                    sheet.append_row([ime, str(datum), st.session_state.selected_time, tel, storitev])
                    st.success("Potrjeno!")
                    st.session_state.selected_time = None
                    st.balloons()
    except Exception as e:
        st.error(f"Napaka: {e}")

with st.expander("Admin"):
    if st.text_input("Geslo", type="password") == ADMIN_PASSWORD:
        st.write(pd.DataFrame(sheet.get_all_records()))