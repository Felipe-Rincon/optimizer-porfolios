import pandas as pd
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import plotly.express as px
import bcrypt
import pyotp
import qrcode

from modules.variables import Variables_user, Variables_user_management, Variables_front, Variables_data_up
from modules.up_data_convert import *
from modules import nsga_3


with open(Variables_user.route_yaml) as file:
    config = yaml.load(file, Loader=SafeLoader)

if Variables_user_management.authentication_status not in st.session_state:
    st.session_state[Variables_user_management.authentication_status] = None
if Variables_user_management.username not in st.session_state:
    st.session_state[Variables_user_management.username] = None
if Variables_user_management.totp_verified not in st.session_state:
    st.session_state[Variables_user_management.totp_verified] = False

def generar_qr(usuario, secret_key):
    uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name = usuario, issuer_name = Variables_front.name_app)
    img = qrcode.make(uri)
    img.save(Variables_user_management.qr_png)
    st.image(Variables_user_management.qr_png, caption = Variables_front.scan_qr)

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

    st.title(Variables_front.name_app)
    st.write(f"{Variables_front.welcome_to}, {config[Variables_user.credentials][Variables_user.usernames][st.session_state[Variables_user_management.username]][Variables_user.name]}!")
    
    st.subheader(Variables_front.upload_data)
    uploaded_file = st.file_uploader(Variables_front.upload_excel_file, type=["xlsx"])

    if uploaded_file is not None:
        try:
            df_values = pd.read_excel(uploaded_file, sheet_name = Variables_data_up.values_name_sheet) 
            df_singular_contrains = pd.read_excel(uploaded_file, sheet_name = Variables_data_up.singular_constrains_name_sheet)
            df_grouped_constrains = pd.read_excel(uploaded_file, sheet_name = Variables_data_up.grouped_constrains_name_sheet)
            df_values_constrains = pd.read_excel(uploaded_file, sheet_name = Variables_data_up.values_constrains_name_sheet)

            st.subheader(Variables_front.values_title)
            st.write(df_values)

            st.subheader(Variables_front.singular_constrains_title)
            st.write(df_singular_contrains)

            st.subheader(Variables_front.grouped_constrains_title)
            st.write(df_grouped_constrains)

            st.subheader(Variables_front.values_constrains_title)
            st.write(df_values_constrains)

            if st.button(Variables_front.optimize):
                with st.spinner(Variables_front.optimizing):  
                    asset_values = asset_values_generator(df_values)
                    portfolio_constraints = constrains_generator(df_singular_contrains, df_grouped_constrains, df_values_constrains)
                    optimum = nsga_3.main(asset_values, portfolio_constraints, 1000, 1)

                    column_names = df_values.columns.tolist()  
                    df_pesos = pd.DataFrame(optimum, columns=column_names)
                    df_pesos.insert(0, Variables_asset_values.portfolios, [f'{Variables_asset_values.portfolio} {i+1}' for i in range(len(df_pesos))])

                    frontier = nsga_3.evaluate(asset_values, optimum)
                    column_names_metrics = [Variables_asset_values.performance, Variables_asset_values.volatility, Variables_asset_values.downside_risk]
                    df_metrics = pd.DataFrame(frontier, columns=column_names_metrics)
                    df_metrics.insert(0, Variables_asset_values.portfolios, [f'{Variables_asset_values.portfolio} {i+1}' for i in range(len(df_metrics))])

                    st.subheader(Variables_front.optimization_results_title)

                    st.subheader(Variables_front.two_dimensions_graphics_title)
                    fig_2d = px.scatter(df_metrics, x = Variables_asset_values.volatility, y = Variables_asset_values.performance, 
                                        color = Variables_asset_values.portfolios, title = f'{Variables_asset_values.performance} vs {Variables_asset_values.volatility}',
                                        labels = {Variables_asset_values.volatility: Variables_asset_values.volatility, Variables_asset_values.performance: Variables_asset_values.performance})
                    st.plotly_chart(fig_2d)

                    st.subheader(Variables_front.three_dimensions_graphics_title)
                    fig_3d = px.scatter_3d(df_metrics, x = Variables_asset_values.volatility, y = Variables_asset_values.downside_risk, z = Variables_asset_values.performance, 
                                          color = Variables_asset_values.portfolios, title = f'{Variables_asset_values.performance} vs {Variables_asset_values.volatility} vs { Variables_asset_values.downside_risk}')
                    st.plotly_chart(fig_3d)

                    st.write(Variables_front.portfolio_weights_title)
                    st.write(df_pesos)

                    st.write(Variables_front.portfolio_metrics_title)
                    st.write(df_metrics)

        except Exception as e:
            st.error(f"Error al leer el archivo Excel: {e}")

    if st.button(Variables_front.logout):
        logout()
        st.rerun()

elif st.session_state[Variables_user_management.authentication_status] is False:
    st.error(Variables_front.incorrect_credentials)
    if st.button(Variables_front.try_again):
        st.session_state[Variables_user_management.authentication_status] = None
        st.rerun()