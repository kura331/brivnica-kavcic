import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Kavčič Cuts", page_icon="✂️")

# Stil za črno ozadje
st.markdown("<style>.stApp { background-color: #000; color: white; } .stButton>button { background-color: #111; color: white; border: 1px solid white; }</style>", unsafe_allow_html=True)

st.title("KAVČIČ CUTS")
st.write("📍 Šegova ulica 14, Novo mesto")

@st.cache_resource
def povezi_tabelo():
    try:
        # TUKAJ JE FIKS: Ključ varno sestavljen iz koščkov
        key_lines = [
            "-----BEGIN PRIVATE KEY-----",
            "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCylAdHNZrnrK2K",
            "pOoO6DLU/APi4mN1eadtmDcVCE2EY+0dtsdSkg/64yE48OwbeCDMX6611cA0jduo",
            "faMcCv6SePbj7jBppxe0xyoXcx15NpM520GL3tXQ9CuBsu5laNM5DT6voeYVzn5K",
            "TQZhGg2ACxHzc15pKrkjwNLKw0Wu0JCu1KHMu6Sro4ftATIM2mFKmvy13pfKEUzi",
            "G2SYPFYgPHZNirhoAVzv3I0iRjUFPOd+My5o4LTgiT5AEihDiwg2gJsVDgwfexuI",
            "m/BjBPrxsns28ASs6Oc0Gcrbfkuopl3PPFZA4d2fmYjwUkuJQ5oMafS31+MmTRTX",
            "F+tI8AXPAgMBAAECggEACwxgLDuuIHSX2A1pSGV9SkgSmtA+2bRzyLKzgGL0c3hr",
            "NydpIDwBLm3W+bA41go8nT2zkB8atnsAWBBN2HJQWxI41ClBvYek+Sjz+wzC32Oi",
            "VYtcfCGGllhE83qf3Tj7DdCP9vXL8mrFeCYD0Ft4R6+8+z7sBxL+7q4DXKAa3jyB",
            "T/vd4uqUKIJY2jWO/9t6XfY1IllHZyMUZKA9VPFBrxmTi0xyEeuYSTb53suIjITf",
            "zugkWY3zJ2FqetusjJdBRo21XZqA9DXt3VWqyFMJyytzYva2McwlYj0qG0IwwsLY",
            "MZUdYiV0F+nQykIgAU8JzQq8r4ocD3HwGksVQ+ptIQKBgQDgEfHSI+V1t0UOo7bN",
            "QpquH629ai81YcGx4htH2lbEJVDk5XE4zD/JeF1k4EZ/oKhKHgmqEIEdYC2LikqK",
            "uqtp2ro5ZVNh/1108mkk0gQBHgztwDmE7M/g5knswkNCTZ2pJzq++g1Qgn0i7c62",
            "WULHpAqeoIznM/uSnuPJpItzWwKBgQDMBouQWL/ZZfEeVW3XscN5U82mzi87UgOe",
            "N7CFI1eObAZBYLExlwVfTnZKqTPb8gCEOAKWVmBOAo2V0WyRJJ/GOy0W+bvvJwFR",
            "hju2DukaRB7d9VwZA+Kxt84/DOvRvB8qEHqK8s4YmkEkV7D7lu9eOvbBnfoxpCed",
            "OkaC2jSFnQKBgGLsyTyjiHzOKvjpop1AmJXjeoszxB/nRuLIFo9EgCYc63gDLFeN",
            "JWRHdcRBmB5kyaffVxj0LGzRt4nxxjM1ctRLMwiACa4sVhB5rZ4J8qajo8Wbpklf",
            "W+/I/D5BDfzJ05+IqFEEiLhQw/qVzzuGcQs/C0k5TLwOoTT8XUj7Em4dAoGAThFv",
            "E9OxzUjho17DAhbGGkXD2kDo98ThF4htpfQpC5kwJ5ING1GTP62xO85UxqNqKS2Z",
            "Z9czUIZPkPUqmrst29dG4JS8ob0GFyDK9lXsQh2wxfOdwwCmnKQdaijSj1Vxg1H8",
            "4fAYhnd316UqVoqhmyfqxZliY95RPitPUcCW+k0CgYB9VpsUumbINm3URC/SqQfc",
            "aJz0axKSZbAEzOyw2O2AQqbtukEcfyVlkc3yGgVpiVR3b52kYnlcszjDp08xfXyp",
            "e0Sy5Ob779T4bzDKzaT+wf9jtDqxUoBuWiLInEI2V4+AYhiLsiq0p/bvFSwC9vCs",
            "nn9CRY9+zdL7ND8tTqqEfiQ==",
            "-----END PRIVATE KEY-----"
        ]
        full_key = "\n".join(key_lines)
        
        info = {
            "type": "service_account",
            "project_id": "subtle-hangar-453519-c3",
            "private_key_id": "311b6910937461011e00adaa7ae63bbdc95e718b",
            "private_key": full_key,
            "client_email": "brivnica-rezervacije@subtle-hangar-453519-c3.iam.gserviceaccount.com",
            "client_id": "116453271150105083095",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/brivnica-rezervacije%40subtle-hangar-453519-c3.iam.gserviceaccount.com"
        }
        
        creds = Credentials.from_service_account_info(info, scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds).open("BarberBooking").get_worksheet(0)
    except Exception as e:
        st.error(f"Napaka pri povezavi: {e}")
        return None

sheet = povezi_tabelo()

if st.button("NAROČI SE NA TERMIN"):
    st.session_state.narocanje = True

if st.session_state.get("narocanje"):
    ime = st.text_input("Ime in priimek")
    tel = st.text_input("Telefon")
    if st.button("POTRDI"):
        if sheet and ime and tel:
            sheet.append_row([ime, tel, "Striženje", datetime.now().strftime("%d.%m.%Y %H:%M")])
            st.success("Rezervirano!")
            st.session_state.narocanje = False

with st.expander("🔐 Admin"):
    if st.text_input("Geslo", type="password") == "kavciccutsadmin0":
        if sheet: st.table(sheet.get_all_records())

st.markdown("---")
st.caption("© 2026 Kavčič Cuts")
