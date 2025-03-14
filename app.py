import streamlit as st
import yaml
from yaml.loader import SafeLoader
import bcrypt
import pyotp
import qrcode
from modules.variables import *

st.set_page_config(layout="wide")

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    hide_sidebar_css = """
    <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        button[title="Toggle sidebar"] {
            display: none !important;
        }
    </style>
    """
    st.markdown(hide_sidebar_css, unsafe_allow_html=True)

with open(Variables_user.route_yaml) as file:
    config = yaml.load(file, Loader=SafeLoader)

if Variables_user_management.authentication_status not in st.session_state:
    st.session_state[Variables_user_management.authentication_status] = None
if Variables_user_management.username not in st.session_state:
    st.session_state[Variables_user_management.username] = None
if Variables_user_management.totp_verified not in st.session_state:
    st.session_state[Variables_user_management.totp_verified] = False

def generar_qr(usuario, secret_key):
    uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name=usuario, issuer_name=Variables_front.name_app)
    img = qrcode.make(uri)
    img.save(Variables_user_management.qr_png)
    st.image(Variables_user_management.qr_png, caption=Variables_front.scan_qr)

def login(username, password):
    if username in config[Variables_user.credentials][Variables_user.usernames]:
        stored_password = config[Variables_user.credentials][Variables_user.usernames][username][Variables_user.password]
        if bcrypt.checkpw(password.encode(), stored_password.encode()):
            st.session_state[Variables_user_management.authentication_status] = True
            st.session_state[Variables_user_management.username] = username
        else:
            st.session_state[Variables_user_management.authentication_status] = False
    else:
        st.session_state[Variables_user_management.authentication_status] = False

def logout():
    st.session_state[Variables_user_management.authentication_status] = None
    st.session_state[Variables_user_management.username] = None
    st.session_state[Variables_user_management.totp_verified] = False

if st.session_state[Variables_user_management.authentication_status] is None:

    logo_path = 'Data/logos/logo.jpg'
    st.image(logo_path, width=150)

    st.title(Variables_front.name_app)
    username = st.text_input(Variables_front.user)
    password = st.text_input(Variables_front.password, type="password")
    if st.button(Variables_front.login):
        login(username, password)
        if st.session_state[Variables_user_management.authentication_status]:
            if config[Variables_user.credentials][Variables_user.usernames][username].get(Variables_user_management.totp_secret) is None:
                secret_key = pyotp.random_base32()
                config[Variables_user.credentials][Variables_user.usernames][username][Variables_user_management.totp_secret] = secret_key
                with open(Variables_user.route_yaml, "w") as file:
                    yaml.dump(config, file)
                st.session_state[Variables_user_management.secret_key] = secret_key
                st.session_state[Variables_user_management.show_qr] = True
            else:
                st.session_state[Variables_user_management.show_qr] = False

if st.session_state.get(Variables_user_management.show_qr, False):
    st.write(Variables_front.firt_loging_qr)
    generar_qr(st.session_state[Variables_user_management.username], st.session_state[Variables_user_management.secret_key])
    st.session_state[Variables_user_management.show_qr] = False

if st.session_state[Variables_user_management.authentication_status] and not st.session_state[Variables_user_management.totp_verified]:
    st.write(Variables_front.enter_code)
    codigo_verificacion = st.text_input(Variables_front.verification_code)
    if st.button(Variables_front.verify_code):
        secret_key = config[Variables_user.credentials][Variables_user.usernames][st.session_state[Variables_user_management.username]][Variables_user_management.totp_secret]
        totp = pyotp.TOTP(secret_key)
        if totp.verify(codigo_verificacion):
            st.session_state[Variables_user_management.totp_verified] = True
            st.success(Variables_front.valid_totp)
            st.rerun()
        else:
            st.error(Variables_front.invalid_totp)
            st.session_state[Variables_user_management.totp_verified] = False

if st.session_state[Variables_user_management.authentication_status] and st.session_state[Variables_user_management.totp_verified]:

    logo_path = 'Data/logos/logo.jpg'
    st.image(logo_path, width=150)

    menu_page = st.Page("pages/Menu.py", title="Menú", icon=":material/menu:")
    strategy_allocation = st.Page("pages/1_Strategy_Allocation.py", title="Strategy Allocation", icon=":material/app_registration:")
    tactical_allocation = st.Page("pages/2_Tactical_Allocation.py", title="Tactical Allocation", icon=":material/model_training:")
    backtesting = st.Page("pages/3_Backtesting.py", title="Backtesting", icon=":material/history:")

    pg = st.navigation(
        {
            "Menú": [menu_page],
            "Optimización": [strategy_allocation, tactical_allocation, backtesting],
        }
    )

    pg.run()

    if st.button(Variables_front.logout):
        logout()
        st.rerun()

elif st.session_state[Variables_user_management.authentication_status] is False:
    st.error(Variables_front.incorrect_credentials)
    if st.button(Variables_front.try_again):
        st.session_state[Variables_user_management.authentication_status] = None
        st.rerun()
