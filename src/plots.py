"""Funciones de visualización para el EDA agrícola.

Cada función guarda el gráfico en PNG en ``results/`` y devuelve la ruta, para
que los resultados queden como artefactos reproducibles.
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

RESULTS_DIR = "results"
sns.set_theme(style="whitegrid")


def _save(fig, name: str) -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_top_crops(df, metric="Valorproduccion", n=10, title=None) -> str:
    data = (
        df.groupby("Nomcultivo")[metric].sum()
        .sort_values(ascending=True)
        .tail(n)
    )
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(data.index, data.values)
    ax.set_title(title or f"Top {n} cultivos por {metric}")
    ax.set_xlabel(metric)
    return _save(fig, "top_cultivos.png")


def plot_production_trend(df, metric="Valorproduccion", title=None) -> str:
    series = df.groupby("Anio")[metric].sum()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(series.index, series.values, marker="o")
    ax.set_title(title or f"Evolución de {metric} (2003–2023)")
    ax.set_xlabel("Año")
    ax.set_ylabel(metric)
    return _save(fig, "tendencia_produccion.png")


def plot_yield_by_modality(df) -> str:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df, x="Nommodalidad", y="Rendimiento", ax=ax)
    ax.set_title("Rendimiento por modalidad (riego vs temporal)")
    ax.set_xlabel("Modalidad")
    ax.set_ylabel("Rendimiento (ton/ha)")
    return _save(fig, "rendimiento_modalidad.png")


def plot_price_evolution(df, crops, title=None) -> str:
    fig, ax = plt.subplots(figsize=(12, 6))
    for crop in crops:
        sub = df[df["Nomcultivo"] == crop].groupby("Anio")["Precio"].mean()
        ax.plot(sub.index, sub.values, marker="o", label=crop)
    ax.set_title(title or "Evolución del precio promedio por cultivo")
    ax.set_xlabel("Año")
    ax.set_ylabel("Precio promedio (MXN/ton)")
    ax.legend()
    return _save(fig, "evolucion_precios.png")


def plot_top_municipalities(df, n=10) -> str:
    data = (
        df.groupby("Nommunicipio")["Valorproduccion"].sum()
        .sort_values(ascending=True)
        .tail(n)
    )
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(data.index, data.values)
    ax.set_title(f"Top {n} municipios por valor de producción")
    ax.set_xlabel("Valor de producción (MXN)")
    return _save(fig, "top_municipios.png")


def plot_siniestralidad(df, n=10) -> str:
    data = (
        df.groupby("Nomcultivo")["Tasa_siniestralidad"].mean()
        .sort_values(ascending=True)
        .tail(n)
    )
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(data.index, data.values, color="firebrick")
    ax.set_title(f"Top {n} cultivos con mayor tasa de siniestralidad")
    ax.set_xlabel("Tasa de siniestralidad (%)")
    return _save(fig, "siniestralidad.png")


def plot_cycle_distribution(df) -> str:
    counts = df.groupby("Nomcicloproductivo")["Valorproduccion"].sum()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Valor de producción por ciclo")
    return _save(fig, "ciclos.png")
