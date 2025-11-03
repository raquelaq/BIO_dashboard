import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
st.set_page_config(
    page_title="Atlas del Sistema Inmunitario",
    page_icon="🧫",
    layout="wide"
)

st.title("🧬 Atlas Cuantitativo del Sistema Inmunitario")
st.markdown("""
Este panel interactivo muestra la distribución del número y masa de células inmunitarias
en distintos sistemas del cuerpo humano, a partir de los datos del *Quantitative Atlas of the Human Immune System (PNAS, 2023)*.
""")

# ==============================
# CARGA DE DATOS
# ==============================
@st.cache_data
def load_data():
    df_system = pd.read_csv("MNI_por_sistema.csv")
    df_cell = pd.read_csv("Desbalance_por_tipo_celular_y_sistema.csv")
    return df_system, df_cell

df_system, df_cell = load_data()

# ==============================
# SECCIÓN 1: VISIÓN GLOBAL
# ==============================
st.header("Índice de Desbalance Masa–Número (MNI) por sistema")

fig1 = px.bar(
    df_system.sort_values("MNI", ascending=False),
    x="MNI",
    y="system",
    orientation="h",
    color="MNI",
    color_continuous_scale=["#d95f02", "#1b9e77"],
    title="MNI = participación en masa − participación en número"
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
**Interpretación:**  
- MNI > 0 → El sistema tiene *más masa inmunitaria relativa* que número de células (p.ej., hígado, pulmones).  
- MNI < 0 → Tiene *muchas células pero más ligeras o pequeñas* (p.ej., médula ósea, sistema linfático).
""")

# ==============================
# SECCIÓN 2: DISPERSIÓN GLOBAL
# ==============================
st.header("⚖️ Comparación entre participación en masa y en número")

fig2 = px.scatter(
    df_system,
    x="share_cells",
    y="share_mass",
    text="system",
    title="Comparación global: participación en masa vs participación en número",
)
fig2.add_shape(
    type="line",
    x0=0, y0=0, x1=1, y1=1,
    line=dict(color="gray", dash="dash")
)
fig2.update_traces(textposition="top center", marker=dict(size=12, color="#4B8BBE"))
st.plotly_chart(fig2, use_container_width=True)

# ==============================
# SECCIÓN 3: DETALLE POR SISTEMA
# ==============================
st.header("🔬 Desglose por tipo celular dentro de cada sistema")

selected_system = st.selectbox(
    "Selecciona un sistema:",
    options=sorted(df_cell["system"].dropna().unique())
)

subset = df_cell[df_cell["system"] == selected_system]

col1, col2 = st.columns(2)

# --- Gráfico 1: MNI por tipo celular dentro del sistema ---
with col1:
    st.subheader(f"Desbalance por tipo celular en {selected_system}")
    fig3 = px.bar(
        subset.sort_values("MNI_sys", ascending=False),
        x="MNI_sys",
        y="cell_type",
        color="cell_type_family",
        orientation="h",
        color_discrete_sequence=px.colors.qualitative.Bold,
        title=f"Tipos celulares más 'pesados' o 'ligeros' en {selected_system}"
    )
    st.plotly_chart(fig3, use_container_width=True)

# --- Gráfico 2: Comparación masa vs número dentro del sistema ---
with col2:
    st.subheader(f"Proporción de masa y número en {selected_system}")
    fig4 = px.bar(
        subset.melt(
            id_vars=["cell_type", "cell_type_family"],
            value_vars=["mass_share_sys", "num_share_sys"],
            var_name="Métrica",
            value_name="Proporción"
        ),
        x="cell_type",
        y="Proporción",
        color="Métrica",
        barmode="group",
        title=f"Comparación interna en {selected_system}"
    )
    st.plotly_chart(fig4, use_container_width=True)

# ==============================
# SECCIÓN 4: CONCLUSIÓN
# ==============================
st.markdown("""
---
### Conclusión general
- Los **tejidos con MNI positivo** (Liver, Lungs, Skin, Others) concentran menos células pero de mayor tamaño (macrófagos, mastocitos).  
- Los **tejidos con MNI negativo** (Bone Marrow, Lymphatic System) contienen enormes cantidades de linfocitos y precursores, pero con menor masa total.  
- El índice MNI ayuda a **visualizar la diferencia entre “cantidad” y “peso” inmunitario**, un concepto clave del atlas.

📘 *Fuente: "A quantitative atlas of the human immune system", PNAS 2023.*
""")
