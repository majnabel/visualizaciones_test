import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px

#config de la visualización de la página
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

#inicio y títulos
st.title("Análisis de Ventas y Clientes")
st.subheader("Dashboard Interactivo")

#carga los datos con caché
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    # Convertir 'Time' a formato de hora para consistencia, aunque no se use directamente en estos gráficos
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time
    return df

df = load_data()

#barra lateraal
st.sidebar.header("Filtros")

#filtro de ciudad
ciudad = st.sidebar.multiselect(
    "Selecciona Ciudad",
    options=df["City"].unique(),
    default=df["City"].unique()
)

#filtro de género
genero = st.sidebar.multiselect(
    "Selecciona Género",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

#filtro de customer type
tipo_cliente = st.sidebar.multiselect(
    "Tipo de Cliente",
    options=df["Customer type"].unique(),
    default=df["Customer type"].unique()
)

#filtro de método de pago
payment = st.sidebar.multiselect(
    "Método de Pago",
    options=df["Payment"].unique(),
    default=df["Payment"].unique()
)

#filtro de fechas
fecha_min_df = df["Date"].min()
fecha_max_df = df["Date"].max()

fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de Fechas",
    value=(fecha_min_df, fecha_max_df),
    min_value=fecha_min_df,
    max_value=fecha_max_df
)

#fechas formateadas
fecha_inicio = pd.to_datetime(fecha_inicio)
fecha_fin = pd.to_datetime(fecha_fin)


#filtrado
df_filtrado = df[
    (df["City"].isin(ciudad)) &
    (df["Gender"].isin(genero)) &
    (df["Customer type"].isin(tipo_cliente)) &
    (df["Payment"].isin(payment)) &
    (df["Date"] >= fecha_inicio) &
    (df["Date"] <= fecha_fin)
]

#pestañas
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Ventas Mensuales",
    "Correlación Lineal (heatmap)",
    "Ingreso Bruto por Sucursal",
    "Gasto por Tipo de Cliente",
    "Ingresos brutos con Cantidad y Calificación (visualización 3D)"
])

with tab1:
    st.subheader("Evolución Mensual de las Ventas Totales")
    #dataframe inicial
    ventas_mensuales = df_filtrado.groupby(df_filtrado['Date'].dt.to_period('M'))['Total'].sum().reset_index()
    ventas_mensuales['Date_Monthly'] = ventas_mensuales['Date'].dt.to_timestamp()

    #líneas para venta mensual
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=ventas_mensuales, x='Date_Monthly', y='Total', marker='o', ax=ax)
    ax.set_title('Evolución Mensual de las Ventas Totales')
    ax.set_xlabel('Mes y Año')
    ax.set_ylabel('Ventas Totales')
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    st.subheader("Análisis de Correlación Numérica (Heatmap)")
    numeric_cols_to_analyze = ['Unit price', 'Quantity', 'Tax 5%', 'Total', 'cogs', 'gross income', 'Rating']
    existing_numeric_cols = [col for col in numeric_cols_to_analyze if col in df_filtrado.columns]
    numeric_df_for_corr = df_filtrado[existing_numeric_cols].copy()

    #cálculo de la matriz
    correlation_matrix = numeric_df_for_corr.corr()

    #heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax)
    ax.set_title('Matriz de Correlación de Variables Numéricas')
    plt.tight_layout()
    st.pyplot(fig)

with tab3:
    st.subheader("Composición del Ingreso Bruto por Sucursal y Línea de Producto")
    #dataframe para la comp de ingreso bruto
    ingreso_bruto_composicion = df_filtrado.groupby(['Branch', 'Product line'])['gross income'].sum().unstack(fill_value=0)

    #barras apiladas
    fig, ax = plt.subplots(figsize=(12, 7))
    ingreso_bruto_composicion.plot(kind='bar', stacked=True, colormap='viridis', ax=ax)
    ax.set_title('Composición del Ingreso Bruto por Sucursal y Línea de Producto')
    ax.set_xlabel('Sucursal (Branch)')
    ax.set_ylabel('Ingreso Bruto')
    ax.tick_params(axis='x', rotation=0) # FIX: Changed ax.xticks to ax.tick_params for rotation
    ax.legend(title='Línea de Producto', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig)

with tab4:
    st.subheader("Comparación del Gasto Total por Tipo de Cliente")
    #boxplot
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df_filtrado, x='Customer type', y='Total', palette='pastel', ax=ax)
    ax.set_title('Distribución del Gasto Total por Tipo de Cliente')
    ax.set_xlabel('Tipo de Cliente')
    ax.set_ylabel('Gasto Total')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

with tab5:
    st.subheader("Visualización 3D: Relación entre Ingreso Bruto, Cantidad y Calificación")
    if not df_filtrado.empty and all(col in df_filtrado.columns for col in ['gross income', 'Quantity', 'Rating', 'Product line']):
        fig_3d = px.scatter_3d(df_filtrado,
                               x='gross income',
                               y='Quantity',
                               z='Rating',
                               color='Product line', 
                               hover_name='Invoice ID',
                               title='Relación 3D: Ingreso Bruto, Cantidad y Calificación por Línea de Producto')
        fig_3d.update_layout(scene_camera=dict(up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=-0.1), eye=dict(x=1.5, y=1.5, z=0.5)))
        st.plotly_chart(fig_3d, use_container_width=True)
