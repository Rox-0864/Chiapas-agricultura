# Análisis de Producción Agrícola — Chiapas 🌽

Análisis exploratorio (EDA) de la **producción agrícola del estado de Chiapas**
(2003–2023), a partir de datos del **SIAP** (Servicio de Información
Agroalimentaria y Pesquera).

> Este repositorio corrige un proyecto anterior que tenía un notebook
> **copiado del proyecto de oncología** (METS OPS) y no analizaba agricultura.
> Los detalles están en la **[guía de estudio](GUIA_DE_ESTUDIO.md)**.

---

## El dataset

`cierre_agricola_modificado.csv` — 22,098 registros, 25 columnas:

- **Chiapas** (único estado), **2003–2023** (21 años).
- **124 municipios** y **74 cultivos**.
- 3 ciclos (Perennes, Primavera-Verano, Otoño-Invierno) y 2 modalidades
  (Riego, Temporal).
- Métricas: sembrada, cosechada, siniestrada, volumen, rendimiento, precio y
  valor de producción.

## Hallazgos principales

- **Maíz grano** domina por valor de producción ($95.6 mil millones MXN),
  seguido de pastos, café cereza, caña de azúcar y plátano.
- Por **volumen**, los pastos y praderas lideran (86.9 M ton).
- **Siniestralidad** más alta: chile seco (4.5%) y soya (3.1%).
- El **riego** logra mayor rendimiento promedio que el temporal.

---

## Estructura

```
Chiapas-agricultura/
├── analisis_agricola.ipynb       # EDA en notebook (Jupyter/Colab)
├── cierre_agricola_modificado.csv# dataset
├── src/
│   ├── data.py                   # carga + transformaciones
│   └── plots.py                  # funciones de visualización
├── scripts/
│   └── eda.py                    # EDA por línea de comandos (genera results/)
├── results/                      # gráficos + resumen exportados
└── requirements.txt
```

## Uso

### Notebook (interactivo)

```bash
pip install -r requirements.txt
jupyter notebook analisis_agricola.ipynb
```

O ábrelo directamente en [Google Colab](https://colab.research.google.com/).

### Script (reproducible)

```bash
python scripts/eda.py
```

Genera los gráficos en `results/` y un `results/resumen.csv`.

---

## Guía de estudio

Los errores del proyecto original y sus correcciones están explicados en
**[GUIA_DE_ESTUDIO.md](GUIA_DE_ESTUDIO.md)**.

---

## Modelo predictivo de producción

Se agregó un análisis predictivo completo (serie estatal 1980–2025 y panel
municipal 2003–2025, con variables climáticas ENSO, precio y superficie).
Resultado central: **ningún modelo supera a la persistencia**; el signal real
es sub-anual (clima) y las decisiones humanas (pastos→ganadería, palma→commodity).

Detalles, resultados y cómo reproducir en
**[INFORME_PREDICTIVO.md](INFORME_PREDICTIVO.md)**.

```
data/            # datasets + forecast
scripts/         # forecast_estatal.py, escenarios.py, model_*.py, enso.py
INFORME_PREDICTIVO.md
```
