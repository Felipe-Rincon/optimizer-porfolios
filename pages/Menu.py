import streamlit as st
import yaml
from yaml.loader import SafeLoader


from modules.variables import *

#Cargar configuración de usuarios
with open(Variables_user.route_yaml) as file:
    config = yaml.load(file, Loader=SafeLoader)

st.title("Asset Optimizer")
st.write(f"{Variables_front.welcome_to}, {config[Variables_user.credentials][Variables_user.usernames][st.session_state[Variables_user_management.username]][Variables_user.name]}!")

