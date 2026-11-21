"""Ejecuta el EDA completo y guarda los resultados (gráficos + resumen).

Uso:
    python scripts/eda.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402

from src import data as sdata  # noqa: E402
from src import plots  # noqa: E402

DATA_PATH = "cierre_agricola_modificado.csv"


def main() -> int:
    df = sdata.load_data(DATA_PATH)

    print("=== RESUMEN GENERAL ===")
    print(sdata.summary_table(df).to_string(index=False))

    print("\n=== TOP 10 CULTIVOS POR VALOR DE PRODUCCIÓN ===")
    top = sdata.top_crops(df, by="Valorproduccion", n=10)
    print(top.to_string(index=False))

    print("\n=== TOP 10 CULTIVOS POR VOLUMEN (ton) ===")
    print(sdata.top_crops(df, by="Volumenproduccion", n=10).to_string(index=False))

    print("\n=== CULTIVOS CON MAYOR TASA DE SINIESTRALIDAD ===")
    sin = (
        df.groupby("Nomcultivo")["Tasa_siniestralidad"].mean()
        .sort_values(ascending=False).head(10).round(2)
    )
    print(sin.to_string())

    # --- Gráficos ---
    paths = [
        plots.plot_top_crops(df, "Valorproduccion", 10),
        plots.plot_production_trend(df, "Valorproduccion"),
        plots.plot_yield_by_modality(df),
        plots.plot_price_evolution(df, ["Maíz grano", "Frijol", "Café cereza", "Limón"]),
        plots.plot_top_municipalities(df, 10),
        plots.plot_siniestralidad(df, 10),
        plots.plot_cycle_distribution(df),
    ]

    print("\n=== GRÁFICOS GENERADOS ===")
    for p in paths:
        print(f"  - {p}")

    # --- Resumen exportado ---
    sdata.summary_table(df).to_csv("results/resumen.csv", index=False)
    print("\nResumen guardado en results/resumen.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
