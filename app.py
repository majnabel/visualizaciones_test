import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px

## Configuración de página
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

## Título del dashboard
st.title("Análisis de Ventas y Clientes")
st.subheader("Dashboard Interactivo")

## Función para cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time
    return df

df = load_data()

## Barra lateral de filtros
st.sidebar.header("Filtros")

## Filtro por ciudad
ciudad = st.sidebar.multiselect(
    "Selecciona Ciudad",
    options=df["City"].unique(),
    default=df["City"].unique()
)

## Filtro por género
genero = st.sidebar.multiselect(
    "Selecciona Género",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

## Filtro por tipo de cliente
tipo_cliente = st.sidebar.multiselect(
    "Tipo de Cliente",
    options=df["Customer type"].unique(),
    default=df["Customer type"].unique()
)

## Filtro por método de pago
payment = st.sidebar.multiselect(
    "Método de Pago",
    options=df["Payment"].unique(),
    default=df["Payment"].unique()
)

## Filtro por rango de fechas
fecha_min_df = df["Date"].min()
fecha_max_df = df["Date"].max()

fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de Fechas",
    value=(fecha_min_df, fecha_max_df),
    min_value=fecha_min_df,
    max_value=fecha_max_df
)

## Convertir fechas para comparación
fecha_inicio = pd.to_datetime(fecha_inicio)
fecha_fin = pd.to_datetime(fecha_fin)

## Aplicar filtros al DataFrame
df_filtrado = df[
    (df["City"].isin(ciudad)) &
    (df["Gender"].isin(genero)) &
    (df["Customer type"].isin(tipo_cliente)) &
    (df["Payment"].isin(payment)) &
    (df["Date"] >= fecha_inicio) &
    (df["Date"] <= fecha_fin)
]

## Pestañas para gráficos
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Ventas Mensuales",
    "Heatmap Correlación",
    "Ingreso Bruto por Sucursal",
    "Gasto por Tipo de Cliente",
    "Visualización 3D"
])

with tab1:
    st.subheader("Evolución Mensual de las Ventas Totales")
    ## Cálculo de ventas mensuales
    ventas_mensuales = df_filtrado.groupby(df_filtrado['Date'].dt.to_period('M'))['Total'].sum().reset_index()
    ventas_mensuales['Date_Monthly'] = ventas_mensuales['Date'].dt.to_timestamp()

    ## Gráfico de líneas para ventas mensuales
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=ventas_mensuales, x='Date_Monthly', y='Total', marker='o', ax=ax)
    ax.