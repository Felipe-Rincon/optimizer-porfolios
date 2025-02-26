# import pandas as pd
# import streamlit as st
# import yaml
# from yaml.loader import SafeLoader
# import plotly.express as px
# import bcrypt

# from modules.variables import Variables_user
# from modules.up_data_convert import * 
# from modules import nsga_3

# with open(Variables_user.route_yaml) as file:
#     config = yaml.load(file, Loader=SafeLoader)

# if Variables_user.authentication_status not in st.session_state:
#     st.session_state[Variables_user.authentication_status] = None
# if Variables_user.username not in st.session_state:
#     st.session_state[Variables_user.username] = None

# def login(username, password):
#     if username in config[Variables_user.credentials][Variables_user.usernames]:
#         stored_password = config[Variables_user.credentials][Variables_user.usernames][username][Variables_user.password]
#         if bcrypt.checkpw(password.encode(), stored_password.encode()):
#             st.session_state[Variables_user.authentication_status] = True
#             st.session_state[Variables_user.username] = username
#         else:
#             st.session_state[Variables_user.authentication_status] = False
#     else:
#         st.session_state[Variables_user.authentication_status] = False

# def logout():
#     st.session_state[Variables_user.authentication_status] = None
#     st.session_state[Variables_user.username] = None

# if st.session_state[Variables_user.authentication_status] is None:
#     st.title("Inicio de Sesión")
#     username = st.text_input("Usuario")
#     password = st.text_input("Contraseña", type=Variables_user.password)
#     if st.button("Iniciar Sesión"):
#         login(username, password)

# elif st.session_state[Variables_user.authentication_status]:
#     st.title("Aplicación Principal")
#     st.write(f"Bienvenido, {config[Variables_user.credentials][Variables_user.usernames][st.session_state[Variables_user.username]][Variables_user.name]}!")
    
#     st.subheader("Subir archivo Excel")
#     uploaded_file = st.file_uploader("Sube un archivo Excel con tres hojas", type=["xlsx"])

#     if uploaded_file is not None:
#         try:

#             df_values = pd.read_excel(uploaded_file, sheet_name="values")  # Primera hoja
#             df_singular_contrains = pd.read_excel(uploaded_file, sheet_name="singular_constrains")  # Segunda hoja
#             df_grouped_constrains = pd.read_excel(uploaded_file, sheet_name="grouped_constrains")
#             df_values_constrains = pd.read_excel(uploaded_file, sheet_name="values_constrains")  # Tercera hoja

#             st.subheader("values")
#             st.write(df_values)

#             st.subheader("singular_constrains")
#             st.write(df_singular_contrains)

#             st.subheader("grouped_constrains")
#             st.write(df_grouped_constrains)

#             st.subheader("values_constrains")
#             st.write(df_values_constrains)

#             if st.button("Optimizar"):
#                 with st.spinner("Optimizando..."):  

#                     asset_values = asset_values_generator(df_values)
#                     portfolio_constraints = constrains_generator(df_singular_contrains, df_grouped_constrains, df_values_constrains)

#                     optimum = nsga_3.main(asset_values, portfolio_constraints, 1000, 1)

#                     column_names = df_values.columns.tolist()  
#                     df_pesos = pd.DataFrame(optimum, columns=column_names)
#                     df_pesos.insert(0, 'portfolios', [f'portfolio {i+1}' for i in range(len(df_pesos))])

#                     frontier = nsga_3.evaluate(asset_values, optimum)
#                     column_names_metrics = ["Retorno", "Volatilidad", "DownsideRisk"]
#                     df_metrics = pd.DataFrame(frontier, columns=column_names_metrics)
#                     df_metrics.insert(0, 'portfolios', [f'portfolio {i+1}' for i in range(len(df_metrics))])

#                     st.subheader("Resultados de la Optimización")

#                     st.subheader("Gráfica 2D: Retorno vs Volatilidad")
#                     fig_2d = px.scatter(df_metrics, x='Volatilidad', y='Retorno', 
#                                         color='portfolios', title='Retorno vs Volatilidad',
#                                         labels={'Volatilidad': 'Volatilidad', 'Retorno': 'Retorno'})
#                     st.plotly_chart(fig_2d)

#                     st.subheader("Gráfica 3D: Retorno, Volatilidad y DownsideRisk")
#                     fig_3d = px.scatter_3d(df_metrics, x='Volatilidad', y='DownsideRisk', z='Retorno', 
#                                           color='portfolios', title='Frontera Eficiente 3D')
#                     st.plotly_chart(fig_3d)

#                     st.write("Pesos de los Portafolios:")
#                     st.write(df_pesos)

#                     st.write("Métricas de los Portafolios:")
#                     st.write(df_metrics)


#         except Exception as e:
#             st.error(f"Error al leer el archivo Excel: {e}")
    
#     if st.button("Cerrar Sesión"):
#         logout()
#         st.rerun()

# elif st.session_state[Variables_user.authentication_status] is False:
#     st.error("Usuario o contraseña incorrectos")
#     if st.button("Volver a intentar"):
#         st.session_state[Variables_user.authentication_status] = None
#         st.rerun()