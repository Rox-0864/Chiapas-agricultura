import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Predicción Producción Agrícola — Chiapas",
                   page_icon="🌽", layout="wide")

# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------
@st.cache_data
def cargar():
    est = pd.read_csv("data/chiapas_estatal_1980_2025.csv")
    fc = pd.read_csv("data/forecast_core_2026_2030.csv")
    oni = pd.read_csv("data/oni_anual_1950_2026.csv")
    mun = pd.read_csv("data/chiapas_municipal_2003_2025.csv")
    return est, fc, oni, mun

est, fc, oni, mun = cargar()

CORE = ["Caña de azúcar", "Maíz grano", "Plátano", "Café cereza",
        "Mango", "Frijol", "Tomate rojo (jitomate)"]

# serie histórica core-7 agregada
historico = est[est["Nomcultivo"].isin(CORE)].groupby("Anio")["Volumenproduccion"].sum()

# ---------------------------------------------------------------------------
# Título y resumen
# ---------------------------------------------------------------------------
st.title("🌽 Predicción de Producción Agrícola — Chiapas")
st.caption("SIAP 1980–2025 · serie temporal estatal + panel municipal + variables climáticas (ENSO)")

st.markdown("""
**Conclusión honesta:** la producción agrícola de Chiapas está dominada por
shocks exógenos (clima sub-anual, decisiones humanas), por lo que **ningún
modelo supera a la persistencia** ("repetir el año anterior"). Lo útil y
defendible es un *forecast agregado con intervalos* y un *modelo por
escenarios* para los cultivos de decisión humana (palma, pastos).
""")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Producción core 2025", f"{historico.iloc[-1]/1e6:.2f} M ton")
c2.metric("Forecast central 2030", f"{fc['central'].iloc[-1]/1e6:.2f} M ton")
c3.metric("Incertidumbre 5 años (IC80)", f"±23%")
c4.metric("MAPE persistencia (1 año)", "6.4%")

st.markdown("---")

# ---------------------------------------------------------------------------
# 1. Forecast estatal con intervalos
# ---------------------------------------------------------------------------
st.header("1 · Forecast estatal — 7 cultivos core (con intervalos)")

fig = go.Figure()
fig.add_trace(go.Scatter(x=historico.index, y=historico.values/1e6,
                         mode="lines", name="Histórico (1980–2025)",
                         line=dict(color="#1f77b4", width=2)))
fig.add_trace(go.Scatter(x=fc["Anio"], y=fc["central"]/1e6,
                         mode="lines+markers", name="Forecast central",
                         line=dict(color="#d62728", width=2, dash="dash")))
fig.add_trace(go.Scatter(x=fc["Anio"], y=fc["ic80_hi"]/1e6, mode="lines",
                         line=dict(width=0), showlegend=False))
fig.add_trace(go.Scatter(x=fc["Anio"], y=fc["ic80_lo"]/1e6, mode="lines",
                         line=dict(width=0), fill="tonexty", fillcolor="rgba(214,39,40,0.15)",
                         name="IC 80%"))
fig.add_trace(go.Scatter(x=fc["Anio"], y=fc["ic95_hi"]/1e6, mode="lines",
                         line=dict(width=0), showlegend=False))
fig.add_trace(go.Scatter(x=fc["Anio"], y=fc["ic95_lo"]/1e6, mode="lines",
                         line=dict(width=0), fill="tonexty", fillcolor="rgba(214,39,40,0.08)",
                         name="IC 95%"))
fig.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0),
                  yaxis_title="Volumen (M ton)", xaxis_title="Año",
                  legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, use_container_width=True)

st.info("Modelo: *random walk con deriva* (ARIMA(0,1,0)+tendencia) en escala logarítmica. "
        "La incertidumbre crece de ±10% (1 año) a ±23% (5 años) al 80% de confianza. "
        "Es un rango de planificación, no un número puntual.")

st.markdown("---")

# ---------------------------------------------------------------------------
# 2. Escenarios palma y pastos
# ---------------------------------------------------------------------------
st.header("2 · Escenarios — cultivos de decisión humana")

def volumen_esc(crop, g, years):
    if crop == "palma":
        p = dict(s0=43938.5, yield_=14.7, harv=0.87, lag=3, hist={2023: 43938, 2024: 43938, 2025: 43938})
    else:
        p = dict(s0=60489.1, yield_=28.5, harv=1.00, lag=0, hist={})
    semb = {}
    s = p["s0"]
    for yr in years:
        s = s * (1 + g)
        semb[yr] = s
    out = {}
    for yr in years:
        src = yr - p["lag"]
        s_used = semb[src] if src >= years[0] else p["hist"].get(src, p["s0"])
        out[yr] = s_used * p["harv"] * p["yield_"]
    return out

years = list(range(2026, 2031))
esc = {
    "Expansión": {"palma": 0.03, "pastos": 0.05},
    "Estable": {"palma": 0.00, "pastos": 0.00},
    "Contracción": {"palma": -0.03, "pastos": -0.05},
}
colores = {"Expansión": "#2ca02c", "Estable": "#1f77b4", "Contracción": "#d62728"}

fig2 = make_subplots(rows=1, cols=2, subplot_titles=("Palma africana (perenne, rezago 3 años)",
                                                    "Pastos y praderas (anual)"))
for nombre_esc, gs in esc.items():
    vp = volumen_esc("palma", gs["palma"], years)
    vpa = volumen_esc("pastos", gs["pastos"], years)
    fig2.add_trace(go.Scatter(x=years, y=[vp[y]/1e6 for y in years], mode="lines+markers",
                              name=nombre_esc, legendgroup=nombre_esc,
                              line=dict(color=colores[nombre_esc], width=2)), row=1, col=1)
    fig2.add_trace(go.Scatter(x=years, y=[vpa[y]/1e6 for y in years], mode="lines+markers",
                              name=nombre_esc, legendgroup=nombre_esc, showlegend=False,
                              line=dict(color=colores[nombre_esc], width=2)), row=1, col=2)
fig2.update_layout(height=420, margin=dict(l=0, r=0, t=40, b=0),
                   yaxis_title="M ton", legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig2, use_container_width=True)

st.info("La palanca es la superficie sembrada (`Sembrada`). Para palma (perenne), "
        "una decisión de expandir hoy recién se refleja en producción ~2029. Para pastos "
        "(anual), el efecto es inmediato. Las tasas son supuestos transparentes editables en `scripts/escenarios.py`.")

st.markdown("---")

# ---------------------------------------------------------------------------
# 3. Cobertura de datos
# ---------------------------------------------------------------------------
st.header("3 · Cobertura de datos (años disponibles por cultivo)")

cov = []
for c in sorted(est["Nomcultivo"].unique()):
    yrs = sorted(est[est["Nomcultivo"] == c]["Anio"].unique())
    cov.append({"Cultivo": c, "Años": len(yrs), "Desde": yrs[0], "Hasta": yrs[-1]})
cov_df = pd.DataFrame(cov).sort_values("Años", ascending=False)
st.dataframe(cov_df, use_container_width=True, hide_index=True)
st.caption("Pastos y praderas (el #1 por volumen) es el de peor serie: solo 2003+ y con hueco 2020-2021. "
           "Palma africana desde 1983 (su introducción); papaya desde 1994.")

st.markdown("---")

# ---------------------------------------------------------------------------
# 4. Validación: por qué gana la persistencia
# ---------------------------------------------------------------------------
st.header("4 · Validación — por qué gana la persistencia")

comp = pd.DataFrame({
    "Modelo": ["Persistencia (baseline)", "Serie temporal (ETS)", "Panel Ridge (rezagos)",
               "Panel + Sembrada/Precio/ENSO", "Panel + ENSO mismo año (techo)", "Gradient Boosting"],
    "MAPE a 1 año": ["6.4%", "16.1%", "10.4%", "11.4%", "10.8%", "20% (sobreajusta)"],
    "¿Supera a persistencia?": ["—", "❌", "❌", "❌", "❌", "❌"],
})
st.table(comp)

st.markdown("""
**Interpretación:**
- La **persistencia** ya captura casi toda la estructura estable; el resto es ruido.
- El **ENSO anual** es demasiado grueso: la producción la define la lluvia en una *ventana
  fenológica* específica, no el promedio anual de El Niño.
- Las **decisiones humanas** (pastos→ganadería, palma→commodity) son quiebres estructurales
  que dejan un rastro *adelantado* medible: la superficie sembrada.
""")

with st.expander("📋 Detalle del hallazgo: el 'modelo a 5 años'"):
    st.markdown("""
    El "modelo predictivo a 5 años" que se recordaba **sí existía** (`Modelos.zip`:
    `Prediccion.ipynb`, `PredRL.ipynb`, `Pred.RLsp.ipynb`) usando Regresión Lineal con
    **precipitación y temperatura** (`PP_Chiapas.csv`, `PT_Chiapas.csv`) para predecir
    volumen/valor a 5 años (2024–2028). Sin embargo tenía vicios de validez:
    - `train_test_split` con `random_state` → **split aleatorio, no temporal** (fuga de datos).
    - Usar `Valorproduccion` para predecir `Volumenproduccion` → **circular** (son casi proporcionales).
    - Extrapolación lineal a 5 años.

    Este análisis es la **versión corregida** de ese intento: validación temporal *walk-forward*,
    baseline honesto (persistencia) y conclusiones con intervalos de incertidumbre.
    """)

st.markdown("---")
st.caption("Reproducible: `scripts/forecast_estatal.py`, `scripts/escenarios.py`, `scripts/model_*.py` · "
           "Informe completo en `INFORME_PREDICTIVO.md`")
