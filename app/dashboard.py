import sqlite3
import time

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from stats import (
    category_stats,
    price_zscores,
    price_zscores_python,
)

st.set_page_config(
    page_title="GameScout Dashboard",
    layout="wide"
)

st.title("GameScout Dashboard")

# Cargar datos

conn = sqlite3.connect("database.db")

df = pd.read_sql_query(
    """
    SELECT
        p.product_id,
        p.title,
        p.price_eur,
        p.type_id,
        pt.name AS product_type
    FROM product AS p
    INNER JOIN producttype AS pt
        ON p.type_id = pt.id
    """,
    conn,
)

conn.close()

# Sidebar

st.sidebar.header("Filtros")

selected_types = st.sidebar.multiselect(
    "Product Type",
    options=sorted(df["product_type"].unique())
)

min_price = float(df["price_eur"].min())
max_price = float(df["price_eur"].max())

price_range = st.sidebar.slider(
    "Precio (€)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
)

search = st.sidebar.text_input(
    "Buscar por título"
)

threshold = st.sidebar.slider(
    "Umbral Z-score",
    0.5,
    5.0,
    2.0,
    0.1,
)

# Aplicar filtros

filtered = df.copy()

if selected_types:
    filtered = filtered[
        filtered["product_type"].isin(selected_types)
    ]

filtered = filtered[
    (filtered["price_eur"] >= price_range[0]) &
    (filtered["price_eur"] <= price_range[1])
]

if search:

    filtered = filtered[
        filtered["title"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

# Si no hay datos

if filtered.empty:

    st.warning("No existen productos para los filtros seleccionados.")
    st.stop()

# Top 10 productos más caros

st.subheader("Top 10 productos más caros")

top10 = (
    filtered
    .sort_values(
        by="price_eur",
        ascending=False
    )
    .head(10)
)

fig = px.bar(
    top10,
    x="price_eur",
    y="title",
    orientation="h",
    labels={
        "price_eur": "Precio (€)",
        "title": "Producto",
    },
)

st.plotly_chart(fig, use_container_width=True)

# Histograma

st.subheader("Distribución de precios")

fig = px.histogram(
    filtered,
    x="price_eur",
    nbins=20,
    labels={
        "price_eur": "Precio (€)"
    },
)

st.plotly_chart(fig, use_container_width=True)

# Precio promedio por categoría

st.subheader("Precio promedio por categoría")

avg = (
    filtered
    .groupby(
        "product_type",
        as_index=False
    )["price_eur"]
    .mean()
)

fig = px.bar(
    avg,
    x="product_type",
    y="price_eur",
    labels={
        "product_type": "Categoría",
        "price_eur": "Precio promedio (€)",
    },
)

st.plotly_chart(fig, use_container_width=True)

# Tabla productos

st.subheader("Productos filtrados")

table = filtered.copy()

table["price_eur"] = table["price_eur"].map(
    lambda x: f"€ {x:.2f}"
)

table = table.rename(
    columns={
        "title": "Título",
        "product_type": "Tipo",
        "price_eur": "Precio (€)",
    }
)

st.dataframe(
    table[
        [
            "product_id",
            "Título",
            "Tipo",
            "Precio (€)",
        ]
    ],
    use_container_width=True,
)

# Preparar arreglos para Numba

prices = filtered["price_eur"].to_numpy(dtype=np.float64)

type_ids = filtered["type_id"].to_numpy(dtype=np.int64)

# Resumen por categoría

categories, counts, mins, maxs, means, stds = category_stats(
    prices,
    type_ids,
)

type_names = (
    df[
        [
            "type_id",
            "product_type",
        ]
    ]
    .drop_duplicates()
    .set_index("type_id")["product_type"]
    .to_dict()
)

summary = pd.DataFrame(
    {
        "Categoría": [type_names[i] for i in categories],
        "Cantidad": counts,
        "Precio mínimo (€)": mins,
        "Precio máximo (€)": maxs,
        "Precio promedio (€)": means,
        "Desv. estándar": stds,
    }
)

st.subheader("Resumen por categoría")

st.dataframe(
    summary,
    use_container_width=True,
)

# Outliers

zscores = price_zscores(
    prices,
    type_ids,
)

filtered = filtered.copy()

filtered["zscore"] = zscores

outliers = filtered[
    np.abs(filtered["zscore"]) > threshold
]

st.subheader("Outliers / Ofertas")

if outliers.empty:

    st.info("No existen productos fuera del umbral seleccionado.")

else:

    outliers = outliers.copy()

    outliers["price_eur"] = outliers["price_eur"].map(
        lambda x: f"€ {x:.2f}"
    )

    outliers = outliers.rename(
        columns={
            "title": "Título",
            "product_type": "Tipo",
            "price_eur": "Precio (€)",
            "zscore": "Z-score",
        }
    )

    st.dataframe(
        outliers[
            [
                "product_id",
                "Título",
                "Tipo",
                "Precio (€)",
                "Z-score",
            ]
        ],
        use_container_width=True,
    )

# Benchmark

# Warm-up (compilación)
price_zscores(
    prices,
    type_ids,
)

start = time.perf_counter()

price_zscores_python(
    prices,
    type_ids,
)

python_time = time.perf_counter() - start

start = time.perf_counter()

price_zscores(
    prices,
    type_ids,
)

numba_time = time.perf_counter() - start

st.subheader("Benchmark")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Python",
    f"{python_time:.6f} s",
)

col2.metric(
    "Numba",
    f"{numba_time:.6f} s",
)

if numba_time > 0:

    col3.metric(
        "Aceleración",
        f"{python_time / numba_time:.2f}x",
    )

st.caption(
    "La primera ejecución de la función con numba no fue considerada en el benchmark."
)
