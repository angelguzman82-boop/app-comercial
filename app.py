import streamlit as st
import pandas as pd

st.set_page_config(page_title="App Comercial", layout="wide")

st.title("📊 Aplicación Comercial")

uploaded_file = st.file_uploader("Sube tu Excel de ventas", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Limpiar nombres de columnas (elimina espacios)
    df.columns = df.columns.str.strip()

    # Convertir fecha
    df["Fecha factura"] = pd.to_datetime(df["Fecha factura"])

    # Crear nombre completo del contacto
    df["Contacto"] = df["Nombre"] + " " + df["Apellido"]

    # Agrupar ventas por cliente y fecha
    ventas = (
        df.groupby(["Cliente", "Provincia", "Fecha factura"])
        .agg(
            volumen_total=("kW", "sum"),
        )
        .reset_index()
    )

    # Resumen por cliente
    resumen = (
        ventas.groupby(["Cliente", "Provincia"])
        .agg(
            volumen_total=("volumen_total", "sum"),
            numero_compras=("Fecha factura", "count"),
            ultima_compra=("Fecha factura", "max")
        )
        .reset_index()
        .sort_values(by="volumen_total", ascending=False)
    )

    provincias = sorted(resumen["Provincia"].unique())
    provincia_sel = st.selectbox("Selecciona Provincia", provincias)

    clientes_filtrados = resumen[resumen["Provincia"] == provincia_sel]

    st.subheader("Clientes por Volumen Total")
    st.dataframe(clientes_filtrados, use_container_width=True)

    cliente_sel = st.selectbox(
        "Selecciona Cliente",
        clientes_filtrados["Cliente"]
    )

    if cliente_sel:
        st.divider()
        st.subheader(f"📌 Ficha Cliente: {cliente_sel}")

        datos_cliente = clientes_filtrados[
            clientes_filtrados["Cliente"] == cliente_sel
        ].iloc[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("⚡ Volumen Total (kW)", round(datos_cliente["volumen_total"], 2))
        col2.metric("🛒 Nº Compras", int(datos_cliente["numero_compras"]))
        col3.metric("📅 Última Compra", datos_cliente["ultima_compra"].date())

        st.subheader("Histórico de Compras")

        historial = ventas[
            ventas["Cliente"] == cliente_sel
        ].sort_values(by="Fecha factura", ascending=False)

        st.dataframe(historial, use_container_width=True)

        st.subheader("👤 Contactos")

        contactos = df[df["Cliente"] == cliente_sel][
            ["Contacto", "Email", "Teléfono"]
        ].drop_duplicates()

        st.dataframe(contactos, use_container_width=True)
