import pandas as pd
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import plotly.express as px
import bcrypt
import pyotp
import qrcode
import plotly.graph_objects as go
import numpy as np

from modules.variables import *
from modules.up_data_convert import *
from modules import nsga_3

st.set_page_config(layout="wide")

logo_path = 'Data/logos/logo.jpg'

st.image(logo_path, width=150)

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

# Formatear solo las columnas numéricas como porcentajes
def format_percentage(df, exclude_column=None):
    # Selecciona solo las columnas numéricas
    numeric_columns = df.select_dtypes(include=[float, int]).columns
    
    # Crea un diccionario de formato excluyendo la columna especificada
    format_dict = {col: "{:.2%}" for col in numeric_columns if col != exclude_column}
    
    # Aplica el formato
    return df.style.format(format_dict)

if st.session_state[Variables_user_management.authentication_status] and st.session_state[Variables_user_management.totp_verified]:
    st.title(Variables_front.name_app)
    st.write(f"{Variables_front.welcome_to}, {config[Variables_user.credentials][Variables_user.usernames][st.session_state[Variables_user_management.username]][Variables_user.name]}!")

    # Crear pestañas para Markowitz y Black-Litterman
    tab1, tab2 = st.tabs(["Strategy Allocation", "Tactical Allocation"])

    with tab1:
        st.subheader("Strategy Allocation Optimization")
        # Aquí va todo el código relacionado con Markowitz
        uploaded_file = st.file_uploader(Variables_front.upload_excel_file, type=["xlsx"], key="strategy_uploader")

        if uploaded_file is not None:
            try:
                df_values = pd.read_excel(uploaded_file, sheet_name=Variables_data_up.values_name_sheet) 
                df_singular_contrains = pd.read_excel(uploaded_file, sheet_name=Variables_data_up.singular_constrains_name_sheet)
                df_grouped_constrains = pd.read_excel(uploaded_file, sheet_name=Variables_data_up.grouped_constrains_name_sheet)
                df_values_constrains = pd.read_excel(uploaded_file, sheet_name=Variables_data_up.values_constrains_name_sheet)
                df_other_info = pd.read_excel(uploaded_file, sheet_name=Variables_data_up.other_info_name_sheet)

                st.subheader(Variables_front.values_title)
                st.write(df_values)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.subheader(Variables_front.singular_constrains_title)
                    st.write(df_singular_contrains)

                with col2:
                    st.subheader(Variables_front.grouped_constrains_title)
                    st.write(df_grouped_constrains)

                with col3:
                    st.subheader(Variables_front.values_constrains_title)
                    st.write(format_percentage(df_values_constrains))

                st.subheader(Variables_front.select_metrics)

                st.write(Variables_front.variable_x)
                var_x_name = st.selectbox(Variables_front.metric_variable_x, options=list(Variables_mapping_optimization.names_to_mapping.keys()), key="strategy_var_x")

                st.write(Variables_front.variable_y)
                var_y_name = st.selectbox(Variables_front.metric_variable_y, options=list(Variables_mapping_optimization.names_to_mapping.keys()), key="strategy_var_y")

                st.write(Variables_front.variable_z)
                var_z_name = st.selectbox(Variables_front.metric_variable_z, options=list(Variables_mapping_optimization.names_to_mapping.keys()), key="strategy_var_z")

                functions_entry = [
                    Variables_mapping_optimization.names_to_mapping[var_x_name],
                    Variables_mapping_optimization.names_to_mapping[var_y_name],
                    Variables_mapping_optimization.names_to_mapping[var_z_name]
                ]

                if st.button(Variables_front.optimize, key="strategy_optimize"):
                    with st.spinner(Variables_front.optimizing):  
                        asset_values = asset_values_generator(df_values, df_other_info)
                        portfolio_constraints = constrains_generator(df_singular_contrains, df_grouped_constrains, df_values_constrains)
                        optimum = nsga_3.main(asset_values, portfolio_constraints, 1000, 1 , functions_entry)

                        column_names = df_values.columns.tolist()  
                        df_pesos = pd.DataFrame(optimum, columns=column_names)
                        df_pesos.insert(0, Variables_asset_values.portfolios, [f'{Variables_asset_values.portfolio} {i+1}' for i in range(len(df_pesos))])
                        
                        frontier = nsga_3.evaluate_portfolios(asset_values, optimum, functions_entry)
                        column_names_metrics = [Variables_front.names_to_front[var_x_name], Variables_front.names_to_front[var_y_name], Variables_front.names_to_front[var_z_name], Variables_front.names_to_front['Duration']]
                        df_metrics = pd.DataFrame(frontier, columns=column_names_metrics)
                        df_metrics.insert(0, Variables_asset_values.portfolios, [f'{Variables_asset_values.portfolio} {i+1}' for i in range(len(df_metrics))])

                        all_metrics = nsga_3.evaluate_all_metrics_strategy(asset_values, optimum)
                        column_names_all_metrics = [Variables_front.names_to_front['Volatility'], Variables_front.names_to_front['Expected Return'], Variables_front.names_to_front['Maximum Drawdown'], Variables_front.names_to_front['Downside Risk'], Variables_front.names_to_front['Sortino Ratio'],Variables_front.names_to_front['Sharpe Ratio'], Variables_front.names_to_front['Duration']]
                        df_all_metrics = pd.DataFrame(all_metrics, columns=column_names_all_metrics)
                        df_all_metrics.insert(0, Variables_asset_values.portfolios, [f'{Variables_asset_values.portfolio} {i+1}' for i in range(len(df_all_metrics))])

                        st.subheader(Variables_front.optimization_results_title)
                        
                        # Gráficas optimizadas
                        df_metrics_plot = df_metrics.copy()

                        # Gráfica 2D optimizada
                        st.subheader(Variables_front.two_dimensions_graphics_title)
                        fig_2d = go.Figure()
                        fig_2d.add_trace(go.Scatter(
                            x=df_metrics_plot[Variables_front.names_to_front[var_x_name]],
                            y=df_metrics_plot[Variables_front.names_to_front[var_y_name]],
                            mode='markers',
                            marker=dict(size=3, color=df_metrics_plot.index, colorscale='Viridis'),
                            text=df_metrics_plot.apply(lambda row: f"Portafolio: {row[Variables_asset_values.portfolios]}<br>{var_x_name}: {row[Variables_front.names_to_front[var_x_name]]:.2%}<br>{var_y_name}: {row[Variables_front.names_to_front[var_y_name]]:.2%}", axis=1), hoverinfo='text'
                        ))
                        fig_2d.update_layout(
                            title=f'{Variables_front.names_to_front[var_x_name]} vs {Variables_front.names_to_front[var_y_name]}',
                            xaxis_title=Variables_front.names_to_front[var_x_name],
                            yaxis_title=Variables_front.names_to_front[var_y_name],
                            xaxis_tickformat='.2%',
                            yaxis_tickformat='.2%',
                            height=700
                        )
                        st.plotly_chart(fig_2d, use_container_width=True)

                        # Gráfica 3D optimizada
                        st.subheader(Variables_front.three_dimensions_graphics_title)
                        fig_3d = go.Figure()
                        fig_3d.add_trace(go.Scatter3d(
                            x=df_metrics_plot[Variables_front.names_to_front[var_x_name]],
                            y=df_metrics_plot[Variables_front.names_to_front[var_y_name]],
                            z=df_metrics_plot[Variables_front.names_to_front[var_z_name]],
                            mode='markers',
                            marker=dict(size=3, color=df_metrics_plot.index, colorscale='Viridis'),
                            text=df_metrics_plot.apply(lambda row: f"Portafolio: {row[Variables_asset_values.portfolios]}<br>{var_x_name}: {row[Variables_front.names_to_front[var_x_name]]:.2%}<br>{var_y_name}: {row[Variables_front.names_to_front[var_y_name]]:.2%}<br>{var_z_name}: {row[Variables_front.names_to_front[var_z_name]]:.2%}", axis=1), hoverinfo='text'
                        ))
                        fig_3d.update_layout(
                            title=f'{Variables_front.names_to_front[var_x_name]} vs {Variables_front.names_to_front[var_y_name]} vs {Variables_front.names_to_front[var_z_name]}',
                            scene=dict(
                                xaxis_title=Variables_front.names_to_front[var_x_name],
                                yaxis_title=Variables_front.names_to_front[var_y_name],
                                zaxis_title=Variables_front.names_to_front[var_z_name],
                                xaxis_tickformat='.2%',
                                yaxis_tickformat='.2%',
                                zaxis_tickformat='.2%'
                            ),
                            height=700
                        )
                        st.plotly_chart(fig_3d, use_container_width=True)

                        # Mostrar df_pesos y df_metrics
                        st.write(Variables_front.portfolio_weights_title)
                        st.write(format_percentage(df_pesos))

                        # st.write(Variables_front.portfolio_metrics_title)
                        # st.write(format_percentage(df_metrics, exclude_column='Duration'))

                        st.write(Variables_front.portfolio_all_metrics_title)
                        st.write(format_percentage(df_all_metrics, exclude_column='Duration'))

            except Exception as e:
                st.error(f"Error al leer el archivo Excel: {e}")

    with tab2:
        st.subheader("Tactical Allocation Optimization")
        # Aquí va todo el código relacionado con Black-Litterman
        uploaded_file = st.file_uploader(Variables_front.upload_excel_file, type=["xlsx"], key="tactical_uploader")

        if uploaded_file is not None:
            try:
                df_values = pd.read_excel(uploaded_file, sheet_name=Variables_data_up.values_name_sheet) 
                df_singular_contrains = pd.read_excel(uploaded_file, sheet_name=Variables_data_up.singular_constrains_name_sheet)
                df_grouped_constrains = pd.read_excel(uploaded_file, sheet_name=Variables_data_up.grouped_constrains_name_sheet)
                df_values_constrains = pd.read_excel(uploaded_file, sheet_name=Variables_data_up.values_constrains_name_sheet)
                df_other_info = pd.read_excel(uploaded_file, sheet_name=Variables_data_up.other_info_name_sheet)

                st.subheader(Variables_front.values_title)
                st.write(df_values)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.subheader(Variables_front.singular_constrains_title)
                    st.write(df_singular_contrains)

                with col2:
                    st.subheader(Variables_front.grouped_constrains_title)
                    st.write(df_grouped_constrains)

                with col3:
                    st.subheader(Variables_front.values_constrains_title)
                    st.write(format_percentage(df_values_constrains))

                st.subheader(Variables_front.select_metrics)

                st.write(Variables_front.variable_x)
                var_x_name = st.selectbox(Variables_front.metric_variable_x, options=list(Variables_mapping_optimization_blacklitterman.names_to_mapping.keys()), key="tactical_var_x")

                st.write(Variables_front.variable_y)
                var_y_name = st.selectbox(Variables_front.metric_variable_y, options=list(Variables_mapping_optimization_blacklitterman.names_to_mapping.keys()), key="tactical_var_y")

                st.write(Variables_front.variable_z)
                var_z_name = st.selectbox(Variables_front.metric_variable_z, options=list(Variables_mapping_optimization_blacklitterman.names_to_mapping.keys()), key="tactical_var_z")

                functions_entry = [
                    Variables_mapping_optimization_blacklitterman.names_to_mapping[var_x_name],
                    Variables_mapping_optimization_blacklitterman.names_to_mapping[var_y_name],
                    Variables_mapping_optimization_blacklitterman.names_to_mapping[var_z_name]
                ]

                if st.button(Variables_front.optimize, key="tactical_optimize"):
                    with st.spinner(Variables_front.optimizing):  
                        asset_values = asset_values_generator(df_values, df_other_info)
                        portfolio_constraints = constrains_generator(df_singular_contrains, df_grouped_constrains, df_values_constrains)
                        optimum = nsga_3.main(asset_values, portfolio_constraints, 1000, 1 , functions_entry)

                        column_names = df_values.columns.tolist()  
                        df_pesos = pd.DataFrame(optimum, columns=column_names)
                        df_pesos.insert(0, Variables_asset_values.portfolios, [f'{Variables_asset_values.portfolio} {i+1}' for i in range(len(df_pesos))])
                        
                        frontier = nsga_3.evaluate_portfolios(asset_values, optimum, functions_entry)
                        column_names_metrics = [Variables_front.names_to_front[var_x_name], Variables_front.names_to_front[var_y_name], Variables_front.names_to_front[var_z_name], Variables_front.names_to_front['Duration']]
                        df_metrics = pd.DataFrame(frontier, columns=column_names_metrics)
                        df_metrics.insert(0, Variables_asset_values.portfolios, [f'{Variables_asset_values.portfolio} {i+1}' for i in range(len(df_metrics))])

                        all_metrics = nsga_3.evaluate_all_metrics_tactical(asset_values, optimum)
                        column_names_all_metrics = [Variables_front.names_to_front['Volatility'], Variables_front.names_to_front['Expected Return Forecast'], Variables_front.names_to_front['Maximum Drawdown'], Variables_front.names_to_front['Downside Risk'], Variables_front.names_to_front['Sortino Ratio'],Variables_front.names_to_front['Sharpe Ratio'], Variables_front.names_to_front['Duration']]
                        df_all_metrics = pd.DataFrame(all_metrics, columns=column_names_all_metrics)
                        df_all_metrics.insert(0, Variables_asset_values.portfolios, [f'{Variables_asset_values.portfolio} {i+1}' for i in range(len(df_all_metrics))])

                        st.subheader(Variables_front.optimization_results_title)
    
                        df_metrics_plot = df_metrics.copy()

                        st.subheader(Variables_front.two_dimensions_graphics_title)
                        fig_2d = go.Figure()
                        fig_2d.add_trace(go.Scatter(
                            x=df_metrics_plot[Variables_front.names_to_front[var_x_name]],
                            y=df_metrics_plot[Variables_front.names_to_front[var_y_name]],
                            mode='markers',
                            marker=dict(size=3, color=df_metrics_plot.index, colorscale='Viridis'),
                            text=df_metrics_plot.apply(lambda row: f"Portafolio: {row[Variables_asset_values.portfolios]}<br>{var_x_name}: {row[Variables_front.names_to_front[var_x_name]]:.2%}<br>{var_y_name}: {row[Variables_front.names_to_front[var_y_name]]:.2%}", axis=1), hoverinfo='text'
                        ))
                        
                        fig_2d.update_layout(
                            title=f'{Variables_front.names_to_front[var_x_name]} vs {Variables_front.names_to_front[var_y_name]}',
                            xaxis_title=Variables_front.names_to_front[var_x_name],
                            yaxis_title=Variables_front.names_to_front[var_y_name],
                            xaxis_tickformat='.2%',
                            yaxis_tickformat='.2%',
                            height=700
                        )
                        st.plotly_chart(fig_2d, use_container_width=True)

                        st.subheader(Variables_front.three_dimensions_graphics_title)
                        fig_3d = go.Figure()
                        fig_3d.add_trace(go.Scatter3d(
                            x=df_metrics_plot[Variables_front.names_to_front[var_x_name]],
                            y=df_metrics_plot[Variables_front.names_to_front[var_y_name]],
                            z=df_metrics_plot[Variables_front.names_to_front[var_z_name]],
                            mode='markers',
                            marker=dict(size=3, color=df_metrics_plot.index, colorscale='Viridis'),
                            text=df_metrics_plot.apply(lambda row: f"Portafolio: {row[Variables_asset_values.portfolios]}<br>{var_x_name}: {row[Variables_front.names_to_front[var_x_name]]:.2%}<br>{var_y_name}: {row[Variables_front.names_to_front[var_y_name]]:.2%}<br>{var_z_name}: {row[Variables_front.names_to_front[var_z_name]]:.2%}", axis=1), hoverinfo='text'
                        ))
                        fig_3d.update_layout(
                            title=f'{Variables_front.names_to_front[var_x_name]} vs {Variables_front.names_to_front[var_y_name]} vs {Variables_front.names_to_front[var_z_name]}',
                            scene=dict(
                                xaxis_title=Variables_front.names_to_front[var_x_name],
                                yaxis_title=Variables_front.names_to_front[var_y_name],
                                zaxis_title=Variables_front.names_to_front[var_z_name],
                                xaxis_tickformat='.2%',
                                yaxis_tickformat='.2%',
                                zaxis_tickformat='.2%'
                            ),
                            height=700
                        )
                        st.plotly_chart(fig_3d, use_container_width=True)

                        st.write(Variables_front.portfolio_weights_title)
                        st.write(format_percentage(df_pesos))

                        # st.write(Variables_front.portfolio_metrics_title)
                        # st.write(format_percentage(df_metrics, exclude_column= 'Duration'))
                        
                        st.write(Variables_front.portfolio_all_metrics_title)
                        st.write(format_percentage(df_all_metrics, exclude_column='Duration'))

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