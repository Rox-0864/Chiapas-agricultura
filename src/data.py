"""Carga y transformación del dataset agrícola de Chiapas (SIAP)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Columnas numéricas de producción (se validan al cargar).
NUMERIC_COLS = [
    "Sembrada", "Cosechada", "Siniestrada", "Volumenproduccion",
    "Rendimiento", "Precio", "Valorproduccion",
]


def load_data(path) -> pd.DataFrame:
    """Carga el CSV y deriva columnas útiles (tasa de siniestralidad)."""
    df = pd.read_csv(path, encoding="utf-8")

    # Normalizar tipos numéricos por si el archivo viene con strings.
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Tasa de siniestralidad (hectáreas siniestradas / sembradas).
    df["Tasa_siniestralidad"] = (df["Siniestrada"] / df["Sembrada"].replace(0, pd.NA)) * 100

    return df


def top_crops(df: pd.DataFrame, by: str = "Valorproduccion", n: int = 10) -> pd.DataFrame:
    """Top N cultivos por una métrica (valor o volumen)."""
    return (
        df.groupby("Nomcultivo")[by].sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )


def production_by_year(df: pd.DataFrame, metric: str = "Valorproduccion") -> pd.DataFrame:
    """Serie temporal de una métrica agregada por año."""
    return df.groupby("Anio")[metric].sum().reset_index()


def summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Resumen general: años, municipios, cultivos y totales clave."""
    return pd.DataFrame(
        {
            "Indicador": [
                "Años", "Municipios", "Cultivos", "Ciclos", "Modalidades",
                "Hectáreas sembradas (total)", "Hectáreas cosechadas (total)",
                "Producción total (ton)", "Valor de producción total (MXN)",
            ],
            "Valor": [
                f"{df['Anio'].min()}–{df['Anio'].max()}",
                df["Nommunicipio"].nunique(),
                df["Nomcultivo"].nunique(),
                ", ".join(df["Nomcicloproductivo"].unique()),
                ", ".join(df["Nommodalidad"].unique()),
                f"{df['Sembrada'].sum():,.0f}",
                f"{df['Cosechada'].sum():,.0f}",
                f"{df['Volumenproduccion'].sum():,.0f}",
                f"${df['Valorproduccion'].sum():,.0f}",
            ],
        }
    )
