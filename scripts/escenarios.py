import pandas as pd, numpy as np

# Supuestos transparentes (calibrados con datos 2022-2025)
palma = dict(sembrada_2025=43938.5, yield_ton_ha=14.7, cosechada_pct=0.87, lag=3)
pastos = dict(sembrada_2025=60489.1, yield_ton_ha=28.5, cosechada_pct=1.00, lag=0)

# Sembrada histórica de palma para alimentar el rezago de los primeros años del escenario
est = pd.read_csv('data/chiapas_estatal_1980_2025.csv')
palma_semb = {2003:16793, 2019:45436, 2022:45423, 2023:43938, 2024:43938, 2025:43938}  # aprox

# escenarios: tasa anual de cambio de Sembrada
ESCENARIOS = {
    'Expansión':   {'palma': +0.03, 'pastos': +0.05},
    'Estable':     {'palma':  0.00, 'pastos':  0.00},
    'Contracción': {'palma': -0.03, 'pastos': -0.05},
}
YEARS = list(range(2026, 2031))

def proyectar_sembrada(s0, g):
    s = s0; out = {}
    for yr in YEARS:
        s = s * (1 + g)
        out[yr] = s
    return out

def volumen(crop, g):
    p = palma if crop=='Palma africana o de aceite' else pastos
    semb = proyectar_sembrada(p['sembrada_2025'], g)
    # sembrada del año t-lag (para palma usa histórico reciente en 2026-2028)
    vol = {}
    for yr in YEARS:
        src_yr = yr - p['lag']
        if src_yr >= 2026:
            s_used = semb[src_yr]
        else:
            s_used = palma_semb.get(src_yr, p['sembrada_2025'])
        vol[yr] = s_used * p['cosechada_pct'] * p['yield_ton_ha']
    return vol

print("=== MODELO POR ESCENARIOS (volumen en M ton) ===\n")
for crop, nombre in [('Palma africana o de aceite','PALMA AFRICANA (perenne, rezago 3 años)'),
                     ('Pastos y praderas','PASTOS Y PRADERAS (anual, sin rezago)')]:
    p = palma if 'Palma' in crop else pastos
    print(f"### {nombre}")
    print(f"    Sembrada 2025={p['sembrada_2025']:.0f} ha | yield={p['yield_ton_ha']:.1f} ton/ha | cosechada={p['cosechada_pct']:.0%} | rezago={p['lag']} años")
    print(f"    {'Escenario':14s} " + " ".join(f"{yr:>7d}" for yr in YEARS))
    resumen = {}
    for esc, gs in ESCENARIOS.items():
        v = volumen(crop, gs[('palma' if 'Palma' in crop else 'pastos')])
        vals = [f"{v[yr]/1e6:>7.2f}" for yr in YEARS]
        print(f"    {esc:14s} " + " ".join(vals))
        resumen[esc] = v[2030]
    print(f"    -> 2030: {', '.join(f'{k} {v/1e6:.2f}M' for k,v in resumen.items())}")
    print()
