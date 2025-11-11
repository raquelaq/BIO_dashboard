import streamlit as st
import pandas as pd
import plotly.express as px

# CONFIGURACIÓN GENERAL
st.set_page_config(
    page_title="Atlas del Sistema Inmunitario",
    page_icon="🧫",
    layout="wide"
)

st.title("🧬 Atlas Cuantitativo del Sistema Inmunitario")
st.markdown("""
Este panel interactivo se basa en los datos del artículo **A quantitative atlas of the human immune system (PNAS, 2023)**.  
Permite explorar cómo se distribuyen el **número** y la **masa** de células inmunitarias entre los distintos sistemas del cuerpo humano.
""")

# CARGA DE DATOS
@st.cache_data
def load_data():
    df_system = pd.read_csv("MNI_por_sistema.csv")
    df_cell = pd.read_csv("Desbalance_por_tipo_celular_y_sistema.csv")
    return df_system, df_cell

df_system, df_cell = load_data()

# MÉTRICAS RESUMEN
col1, col2, col3 = st.columns(3)
col1.metric("🧮 Total de células inmunes", f"{df_cell['num_cells'].sum():.2e}")
col2.metric("⚖️ Masa inmunitaria total (g)", f"{df_cell['mass_g'].sum():.1f}")
col3.metric("🔬 Sistemas analizados", df_system['system'].nunique())

st.divider()

# PESTAÑAS PRINCIPALES
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 MNI Global",
    "⚖️ Comparación masa vs número",
    "🔬 Detalle por sistema",
    "🧪 Simulación (escenario obesidad)"
])

# TAB 1 — MNI GLOBAL
with tab1:
    st.header("Índice de Desbalance Masa–Número (MNI) por sistema")

    mni_range = st.slider(
        "Filtra sistemas por rango de MNI:",
        min_value=float(df_system["MNI"].min()),
        max_value=float(df_system["MNI"].max()),
        value=(float(df_system["MNI"].min()), float(df_system["MNI"].max()))
    )
    filtered = df_system[(df_system["MNI"] >= mni_range[0]) & (df_system["MNI"] <= mni_range[1])]

    fig1 = px.bar(
        filtered.sort_values("MNI", ascending=False),
        x="MNI", y="system",
        orientation="h",
        color="MNI",
        color_continuous_scale=["#d95f02", "#1b9e77"],
        hover_data={"share_mass":":.3f", "share_cells":":.3f"},
        title="MNI = participación en masa − participación en número"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    **Interpretación:**  
    - MNI > 0 → más masa relativa que número (p.ej. hígado, pulmones).  
    - MNI < 0 → muchas células pequeñas (médula ósea, sistema linfático).
    """)

    st.markdown("""
    **Conclusiones**

    - Los sistemas con **MNI positivo** (Others, Liver, Lungs, Skin) tienen **más masa inmunitaria relativa** que número de células, debido a la abundancia de **macrófagos y mastocitos**.  
    - Los sistemas con **MNI negativo** (Bone Marrow, Lymphatic System) contienen **muchas células pequeñas**, sobre todo **linfocitos**.  
    - Este patrón muestra que la masa inmunitaria y el número celular no coinciden espacialmente, reflejando la especialización de cada tejido.
    """)

# TAB 2 — DISPERSIÓN MASA VS NÚMERO
with tab2:
    st.header("Comparación global entre participación en masa y en número")

    selected_systems = st.multiselect(
        "Selecciona uno o varios sistemas para resaltar:",
        options=sorted(df_system["system"].dropna().unique()),
        default=["Liver", "Lungs"]
    )

    fig2 = px.scatter(
        df_system,
        x="share_cells", y="share_mass", text="system",
        color=df_system["system"].isin(selected_systems),
        color_discrete_map={True:"#4B8BBE", False:"lightgray"},
        title="Participación en masa vs participación en número de células inmunes"
    )
    fig2.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                   line=dict(color="gray", dash="dash"))
    fig2.update_traces(textposition="top center", marker=dict(size=12))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    > Los puntos sobre la diagonal (y=x) indican equilibrio.  
    > Por encima → más masa que número; por debajo → más número que masa.
    """)

    st.markdown("""
    **Conclusiones**

    - Los sistemas **por encima de la diagonal** (Liver, Lungs, Others) poseen **mayor masa relativa**.  
    - Los **por debajo** (Bone Marrow, Lymphatic System) muestran **mayor número relativo**.  
    - La gráfica demuestra la asimetría entre **función metabólica (tejidos “pesados”)** 
      y **producción/almacenamiento (tejidos “ligeros”)** del sistema inmunitario.
    """)

# TAB 3 — DETALLE POR SISTEMA
with tab3:
    st.header("Desglose por tipo celular dentro de cada sistema")

    colA, colB = st.columns([1, 3])
    with colA:
        selected_systems2 = st.multiselect(
            "Selecciona sistemas a analizar:",
            options=sorted(df_cell["system"].dropna().unique()),
            default=["Liver"]
        )
        selected_family = st.multiselect(
            "Filtra por familia celular (opcional):",
            options=sorted(df_cell["cell_type_family"].dropna().unique()),
            default=[]
        )

    filtered_cells = df_cell[df_cell["system"].isin(selected_systems2)]
    if selected_family:
        filtered_cells = filtered_cells[filtered_cells["cell_type_family"].isin(selected_family)]

    col1, col2 = st.columns(2)

    with col1:
        fig3 = px.bar(
            filtered_cells.sort_values("MNI_sys", ascending=False),
            x="MNI_sys", y="cell_type", color="cell_type_family",
            orientation="h",
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Tipos celulares más 'pesados' o 'ligeros'"
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        fig4 = px.bar(
            filtered_cells.melt(
                id_vars=["cell_type", "cell_type_family", "system"],
                value_vars=["mass_share_sys", "num_share_sys"],
                var_name="Métrica", value_name="Proporción"
            ),
            x="cell_type", y="Proporción", color="Métrica",
            barmode="group",
            title="Comparación de masa y número dentro del sistema"
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=filtered_cells.to_csv(index=False),
        file_name="datos_filtrados.csv",
        mime="text/csv"
    )

    st.markdown(f"""
    **Conclusiones**

    - Las diferencias de **MNI_sys** muestran qué células dominan la masa y cuáles el número.  
    - En hígado y pulmón destacan los **macrófagos**; en médula y linfático, los **linfocitos**.  
    - Esto refuerza la idea de que el desbalance global surge de la composición celular de cada tejido.
    """)

# TAB 4 — SIMULACIÓN (ESCENARIO OBESIDAD)
with tab4:
    st.header("Simulador de cambios en composición inmunitaria")

    st.markdown("""
    El siguiente control permite simular un aumento de macrófagos en el tejido adiposo (incluido en “Others”), 
    como ocurre en la **obesidad**.  
    Ajusta el multiplicador y observa cómo cambia la distribución global del MNI.
    """)

    factor = st.slider("Multiplicar macrófagos en 'Others' por:", 1, 20, 10)

    df_sim = df_cell.copy()
    mask = (df_sim["system"] == "Others") & (df_sim["cell_type"] == "Macrophages")
    df_sim.loc[mask, ["num_cells", "mass_g"]] *= factor

    sim_summary = df_sim.groupby("system").agg(
        total_cells=('num_cells', 'sum'),
        total_mass_g=('mass_g', 'sum')
    ).reset_index()
    sim_summary["share_cells"] = sim_summary["total_cells"]/sim_summary["total_cells"].sum()
    sim_summary["share_mass"] = sim_summary["total_mass_g"]/sim_summary["total_mass_g"].sum()
    sim_summary["MNI"] = sim_summary["share_mass"] - sim_summary["share_cells"]

    fig5 = px.bar(
        sim_summary.sort_values("MNI", ascending=False),
        x="MNI", y="system", orientation="h",
        color="MNI",
        color_continuous_scale=["#d95f02", "#1b9e77"],
        title=f"Simulación: efecto del aumento de macrófagos ×{factor}"
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("""
    👉 Observa cómo el sistema “Others” aumenta su peso relativo en el conjunto, 
    desplazando la masa inmunitaria total hacia los tejidos adiposos.
    """)

    st.markdown("""
    **Conclusiones**

    - Al aumentar los macrófagos adiposos (en “Others”), el MNI global se desplaza hacia los tejidos grasos.  
    - Esto simula el comportamiento observado en la **obesidad**, donde el sistema inmune se redistribuye hacia el tejido adiposo.  
    - Biológicamente, refleja la **inflamación crónica de bajo grado** típica del estado metabólico alterado.
    """)

st.divider()

st.markdown("""
### Conclusión general
- **MNI positivo:** tejidos con pocas células pero de gran tamaño (hígado, pulmones, piel, adiposo).  
- **MNI negativo:** tejidos con muchas células pequeñas (médula ósea, sistema linfático).  
- La simulación muestra que un aumento en macrófagos adiposos redistribuye la **masa inmunitaria corporal**, 
  en línea con lo observado en la obesidad.  

📘 *Fuente: "A quantitative atlas of the human immune system", PNAS 2023.*
""")
