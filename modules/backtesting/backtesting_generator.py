import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64 


def calculate_drawdown(returns):
    cumulative_returns = (1 + returns).cumprod()
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns - peak) / peak
    return drawdown


def backtest_portfolio(portfolio, prices):
    weights = portfolio.iloc[1:].astype(float) 
    portfolio_returns = (prices.pct_change().dropna() * weights).sum(axis=1)
    return portfolio_returns

def to_csv_download_link(df, filename):
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar {filename}</a>'
    return href