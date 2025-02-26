import pandas as pd
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import plotly.express as px
import bcrypt
import pyotp
import qrcode

from modules.variables import Variables_user
from modules.up_data_convert import *
from modules import nsga_3

# Cargar configuración desde el archivo YAML
with open(Variables_user.route_yaml) as file:
    config = yaml.load(file, Loader=SafeLoader)

# Inicializar el estado de la sesión
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "totp_verified" not in st.session_state:  # Nuevo estado para verificar TOTP
    st.session_state["totp_verified"] = False

# Función para generar y mostrar el código QR
def generar_qr(usuario, secret_key):
    uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name=usuario, issuer_name="MiAppStreamlit")
    img = qrcode.make(uri)
    img.save("qr.png")
    st.image("qr.png", caption="Escanee este código QR con Google Authenticator")

# Función de inicio de sesión
def login(username, password):
    print(f"Intentando iniciar sesión con usuario: {username}")  # Depuración
    if username in config[Variables_user.credentials][Variables_user.usernames]:
        stored_password = config[Variables_user.credentials][Variables_user.usernames][username][Variables_user.password]
        if bcrypt.checkpw(password.encode(), stored_password.encode()):
            print("Contraseña válida.")  # Depuración
            st.session_state["authentication_status"] = True
            st.session_state["username"] = username
        else:
            print("Contraseña inválida.")  # Depuración
            st.session_state["authentication_status"] = False
    else:
        print("Usuario no encontrado.")  # Depuración
        st.session_state["authentication_status"] = False

# Función para cerrar sesión
def logout():
    print("Cerrando sesión...")  # Depuración
    st.session_state["authentication_status"] = None
    st.session_state["username"] = None
    st.session_state["totp_verified"] = False  # Reiniciar la verificación TOTP

# Interfaz de inicio de sesión
# Interfaz de inicio de sesión
# Interfaz de inicio de sesión
if st.session_state["authentication_status"] is None:
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        login(username, password)
        if st.session_state["authentication_status"]:
            print("Inicio de sesión exitoso. Verificando TOTP...")  # Depuración
            # Verificar si el usuario ya tiene una clave secreta TOTP
            if config[Variables_user.credentials][Variables_user.usernames][username].get("totp_secret") is None:
                # Generar una clave secreta si no existe
                secret_key = pyotp.random_base32()
                config[Variables_user.credentials][Variables_user.usernames][username]["totp_secret"] = secret_key
                with open(Variables_user.route_yaml, "w") as file:
                    yaml.dump(config, file)
                print("Clave secreta generada.")  # Depuración
                st.session_state["secret_key"] = secret_key  # Guardar la clave secreta en el estado de la sesión
                st.session_state["show_qr"] = True  # Mostrar el código QR
            else:
                st.session_state["show_qr"] = False  # No mostrar el código QR

# Mostrar el código QR si es necesario
if st.session_state.get("show_qr", False):
    st.write("Es la primera vez que inicias sesión. Escanea el código QR con Google Authenticator.")
    generar_qr(st.session_state["username"], st.session_state["secret_key"])
    st.session_state["show_qr"] = False  # Ocultar el código QR después de mostrarlo

# Solicitar el código TOTP si el usuario ha iniciado sesión
if st.session_state["authentication_status"]:
    st.write("Por favor, ingresa el código de Google Authenticator.")
    codigo_verificacion = st.text_input("Código de verificación:")
    if st.button("Verificar Código"):
        print(f"Código ingresado: {codigo_verificacion}")  # Depuración
        secret_key = config[Variables_user.credentials][Variables_user.usernames][st.session_state["username"]]["totp_secret"]
        totp = pyotp.TOTP(secret_key)
        if totp.verify(codigo_verificacion):
            print("Código TOTP válido.")  # Depuración
            st.session_state["totp_verified"] = True  # Marcar como verificado
            st.success("Código válido. Inicio de sesión exitoso!")
            st.rerun()  # Recargar la página para actualizar el estado
        else:
            print("Código TOTP inválido.")  # Depuración
            st.error("Código inválido.")
            st.session_state["totp_verified"] = False  # Marcar como no verificado

# Interfaz de la aplicación principal
elif st.session_state["authentication_status"] and st.session_state["totp_verified"]:
    print("Acceso concedido a la aplicación principal.")  # Depuración
    st.title("Aplicación Principal")
    st.write(f"Bienvenido, {config[Variables_user.credentials][Variables_user.usernames][st.session_state['username']][Variables_user.name]}!")
    
    st.subheader("Subir archivo Excel")
    uploaded_file = st.file_uploader("Sube un archivo Excel con tres hojas", type=["xlsx"])

    if uploaded_file is not None:
        try:
            df_values = pd.read_excel(uploaded_file, sheet_name="values")  # Primera hoja
            df_singular_contrains = pd.read_excel(uploaded_file, sheet_name="singular_constrains")  # Segunda hoja
            df_grouped_constrains = pd.read_excel(uploaded_file, sheet_name="grouped_constrains")
            df_values_constrains = pd.read_excel(uploaded_file, sheet_name="values_constrains")  # Tercera hoja

            st.subheader("values")
            st.write(df_values)

            st.subheader("singular_constrains")
            st.write(df_singular_contrains)

            st.subheader("grouped_constrains")
            st.write(df_grouped_constrains)

            st.subheader("values_constrains")
            st.write(df_values_constrains)

            if st.button("Optimizar"):
                with st.spinner("Optimizando..."):  
                    asset_values = asset_values_generator(df_values)
                    portfolio_constraints = constrains_generator(df_singular_contrains, df_grouped_constrains, df_values_constrains)
                    optimum = nsga_3.main(asset_values, portfolio_constraints, 1000, 1)

                    column_names = df_values.columns.tolist()  
                    df_pesos = pd.DataFrame(optimum, columns=column_names)
                    df_pesos.insert(0, 'portfolios', [f'portfolio {i+1}' for i in range(len(df_pesos))])

                    frontier = nsga_3.evaluate(asset_values, optimum)
                    column_names_metrics = ["Retorno", "Volatilidad", "DownsideRisk"]
                    df_metrics = pd.DataFrame(frontier, columns=column_names_metrics)
                    df_metrics.insert(0, 'portfolios', [f'portfolio {i+1}' for i in range(len(df_metrics))])

                    st.subheader("Resultados de la Optimización")

                    st.subheader("Gráfica 2D: Retorno vs Volatilidad")
                    fig_2d = px.scatter(df_metrics, x='Volatilidad', y='Retorno', 
                                        color='portfolios', title='Retorno vs Volatilidad',
                                        labels={'Volatilidad': 'Volatilidad', 'Retorno': 'Retorno'})
                    st.plotly_chart(fig_2d)

                    st.subheader("Gráfica 3D: Retorno, Volatilidad y DownsideRisk")
                    fig_3d = px.scatter_3d(df_metrics, x='Volatilidad', y='DownsideRisk', z='Retorno', 
                                          color='portfolios', title='Frontera Eficiente 3D')
                    st.plotly_chart(fig_3d)

                    st.write("Pesos de los Portafolios:")
                    st.write(df_pesos)

                    st.write("Métricas de los Portafolios:")
                    st.write(df_metrics)

        except Exception as e:
            st.error(f"Error al leer el archivo Excel: {e}")

    if st.button("Cerrar Sesión"):
        logout()
        st.rerun()  # Recargar la página para actualizar el estado

# Mensaje de error si las credenciales son incorrectas
elif st.session_state["authentication_status"] is False:
    print("Credenciales incorrectas. Mostrando mensaje de error.")  # Depuración
    st.error("Usuario o contraseña incorrectos")
    if st.button("Volver a intentar"):
        st.session_state["authentication_status"] = None
        st.rerun()  # Recargar la página para actualizar el estado  # Recargar la página para actualizar el estado