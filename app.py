import streamlit as st
import pandas as pd

st.set_page_config(page_title="App Comercial", layout="wide")

st.title("📊 Aplicación Comercial - Volumen por Provincia")

# Subir archivo
uploaded_file = st.file_uploader("Sube el Excel histórico de ventas", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalizamos nombres de columnas (ajusta si es necesario)
    df.columns = df.columns.str.strip().str.lower()

    # Verificamos columnas mínimas
    required_columns = ["cliente", "provincia", "fecha", "kw"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        st.error(f"Faltan columnas necesarias: {missing}")
    else:
        # Convertimos fecha
        df["fecha"] = pd.to_datetime(df["fecha"])

        # Agrupamos por cliente y fecha (consolidar productos)
        ventas_consolidadas = (
            df.groupby(["cliente", "provincia", "fecha"])
              .agg(volumen_total_kw=("kw", "sum"))
              .reset_index()
        )

        # Totales por cliente
        resumen_clientes = (
            ventas_consolidadas.groupby(["cliente", "provincia"])
            .agg(
                volumen_total_kw=("volumen_total_kw", "sum"),
                numero_compras=("fecha", "count"),
                ultima_compra=("fecha", "max")
            )
            .reset_index()
            .sort_values(by="volumen_total_kw", ascending=False)
        )

        # Filtro por provincia
        provincias = sorted(resumen_clientes["provincia"].unique())
        provincia_seleccionada = st.selectbox("Seleccionar Provincia", provincias)

        clientes_filtrados = resumen_clientes[
            resumen_clientes["provincia"] == provincia_seleccionada
        ]

        st.subheader("Clientes")

        st.dataframe(
            clientes_filtrados,
            use_container_width=True
        )

        # Seleccionar cliente
        cliente_seleccionado = st.selectbox(
            "Seleccionar Cliente",
            clientes_filtrados["cliente"].unique()
        )

        if cliente_seleccionado:
            st.divider()
            st.subheader(f"📌 Ficha Cliente: {cliente_seleccionado}")

            cliente_data = clientes_filtrados[
                clientes_filtrados["cliente"] == cliente_seleccionado
            ].iloc[0]

            col1, col2, col3 = st.columns(3)

            col1.metric("⚡ Volumen Total (kW)", round(cliente_data["volumen_total_kw"], 2))
            col2.metric("🛒 Nº Compras", int(cliente_data["numero_compras"]))
            col3.metric("📅 Última Compra", cliente_data["ultima_compra"].date())

            st.subheader("Histórico de Compras")

            historial = ventas_consolidadas[
                ventas_consolidadas["cliente"] == cliente_seleccionado
            ].sort_values(by="fecha", ascending=False)

            st.dataframe(historial, use_container_width=True)

            st.subheader("👤 Contactos (local, demo)")

            if "contactos" not in st.session_state:
                st.session_state.contactos = {}

            if cliente_seleccionado not in st.session_state.contactos:
                st.session_state.contactos[cliente_seleccionado] = []

            with st.form("nuevo_contacto"):
                nombre = st.text_input("Nombre")
                email = st.text_input("Email")
                telefono = st.text_input("Teléfono")
                submitted = st.form_submit_button("Añadir Contacto")

                if submitted:
                    st.session_state.contactos[cliente_seleccionado].append({
                        "nombre": nombre,
                        "email": email,
                        "telefono": telefono
                    })

            contactos_cliente = st.session_state.contactos[cliente_seleccionado]

            if contactos_cliente:
                contactos_df = pd.DataFrame(contactos_cliente)
                st.dataframe(contactos_df, use_container_width=True)
            else:
                st.info("No hay contactos añadidos aún.")
