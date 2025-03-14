import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64  # Para la descarga de archivos

from modules.backtesting import backtesting_generator

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("Por favor, inicia sesión para acceder a esta página.")
    st.stop()

st.title("Backtesting")

uploaded_portfolios = st.file_uploader("Sube el archivo CSV de portafolios", type=["csv"])
uploaded_prices = st.file_uploader("Sube el archivo Excel de precios", type=["xlsx"])

# Verificar si se han subido ambos archivos
if uploaded_portfolios is not None and uploaded_prices is not None:
    # Cargar los datos de los portafolios
    portfolios = pd.read_csv(uploaded_portfolios, index_col=0)

    prices = pd.read_excel(uploaded_prices, index_col=0)


    portfolio_names = portfolios.index.tolist()
    selected_portfolio = st.selectbox('Selecciona un portafolio', portfolio_names)

    if st.button("Star Backtesting"):

        portfolio_weights = portfolios.loc[selected_portfolio]


        portfolio_returns = backtesting_generator.backtest_portfolio(portfolio_weights, prices)

        nav = (1 + portfolio_returns).cumprod() * 100

        drawdown = backtesting_generator.calculate_drawdown(portfolio_returns)

        portfolio_returns_pct = portfolio_returns

        monthly_returns = portfolio_returns.resample('ME').apply(lambda x: (1 + x).prod() - 1) 

        quarterly_returns = portfolio_returns.resample('QE').apply(lambda x: (1 + x).prod() - 1) 

        yearly_returns = portfolio_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) 


        # Mostrar gráficos con Plotly
        st.subheader('Rendimiento del Portafolio (NAV base 100)')
        fig_nav = go.Figure()
        fig_nav.add_trace(go.Scatter(
            x=nav.index,
            y=nav,
            mode='lines',
            name='NAV'
        ))
        fig_nav.update_layout(
            xaxis_title='Fecha',
            yaxis_title='NAV',
            hovermode='x unified'
        )
        st.plotly_chart(fig_nav)

        st.subheader('Drawdown del Portafolio (%)')
        fig_drawdown = go.Figure()
        fig_drawdown.add_trace(go.Scatter(
            x=drawdown.index,
            y=drawdown,
            mode='lines',
            name='Drawdown'
        ))
        fig_drawdown.update_layout(
            xaxis_title='Fecha',
            yaxis_title='Drawdown (%)',
            yaxis_tickformat='.2%',
            hovermode='x unified'
        )
        st.plotly_chart(fig_drawdown)


        st.subheader('Histogramas de Rendimientos')


        st.write("**Histograma Diario**")
        fig_daily = go.Figure()
        fig_daily.add_trace(go.Histogram(
            x=portfolio_returns_pct,
            nbinsx=50,
            name='Rendimientos Diarios'
        ))
        fig_daily.update_layout(
            xaxis_title='Rendimiento (%)',
            yaxis_title='Frecuencia',
            xaxis_tickformat='.2%',
            title='Distribución de Rendimientos Diarios (%)'
        )
        st.plotly_chart(fig_daily)

        st.write("**Histograma Mensual**")
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Histogram(
            x=monthly_returns,
            nbinsx=50,
            name='Rendimientos Mensuales'
        ))
        fig_monthly.update_layout(
            xaxis_title='Rendimiento (%)',
            yaxis_title='Frecuencia',
            xaxis_tickformat='.2%',
            title='Distribución de Rendimientos Mensuales (%)'
        )
        st.plotly_chart(fig_monthly)

        st.write("**Histograma Trimestral**")
        fig_quarterly = go.Figure()
        fig_quarterly.add_trace(go.Histogram(
            x=quarterly_returns,
            nbinsx=50,
            name='Rendimientos Trimestrales'
        ))
        fig_quarterly.update_layout(
            xaxis_title='Rendimiento (%)',
            yaxis_title='Frecuencia',
            xaxis_tickformat='.2%',
            title='Distribución de Rendimientos Trimestrales (%)'
        )
        st.plotly_chart(fig_quarterly)

        st.write("**Histograma Anual**")
        fig_yearly = go.Figure()
        fig_yearly.add_trace(go.Histogram(
            x=yearly_returns,
            nbinsx=50,
            name='Rendimientos Anuales'
        ))
        fig_yearly.update_layout(
            xaxis_title='Rendimiento (%)',
            yaxis_title='Frecuencia',
            xaxis_tickformat='.2%',
            title='Distribución de Rendimientos Anuales (%)'
        )
        st.plotly_chart(fig_yearly)


        st.subheader('Estadísticas del Portafolio')
        st.write(f"Retorno Total: {(nav.iloc[-1] / 100 - 1) * 100:.2f}%")  

        st.write(f"Drawdown Máximo: {drawdown.min()* 100:.2f}%")
        st.write(f"Volatilidad (Desviación Estándar): {portfolio_returns.std() * 100:.2f}%")

        results_df = pd.DataFrame({
            'Fecha': portfolio_returns.index,
            'Rendimiento Diario (%)': portfolio_returns_pct,
            'NAV': nav,
            'Drawdown (%)': drawdown
        })

        st.subheader('Resultados del Backtesting')
        st.write(results_df)

        st.markdown(backtesting_generator.to_csv_download_link(results_df, "backtesting_results.csv"), unsafe_allow_html=True)
