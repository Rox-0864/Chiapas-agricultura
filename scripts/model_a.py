import pandas as pd, numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

est = pd.read_csv('data/chiapas_estatal_1980_2025.csv')
TOP10 = ['Pastos y praderas','Caña de azúcar','Maíz grano','Plátano','Café cereza',
         'Palma africana o de aceite','Mango','Papaya','Frijol','Tomate rojo (jitomate)']

H = [1, 2, 3]
results = []
for crop in TOP10:
    s = est[est['Nomcultivo']==crop].sort_values('Anio').set_index('Anio')['Volumenproduccion']
    years = s.index.values
    if len(s) < 15:
        results.append((crop, len(s), None, None, None, 'serie corta (<15 años), no modelable'))
        continue
    for h in H:
        b_errors = []; e_errors = []
        for t in years:
            if t + h not in s.index:
                continue  # salta huecos (ej. pastos 2020-2021)
            train = s[s.index <= t]
            if len(train) < 10:
                continue
            y_true = s[s.index == t+h].values[0]
            b = s[s.index == t].values[0]
            b_errors.append(abs(y_true - b)/abs(y_true))
            try:
                m = ExponentialSmoothing(train.values, trend='add', seasonal=None,
                                         initialization_method='estimated').fit()
                f = m.forecast(h)[-1]
                e_errors.append(abs(y_true - f)/abs(y_true))
            except Exception:
                e_errors.append(np.nan)
        results.append((crop, len(s), h, 100*np.mean(b_errors), 100*np.nanmean(e_errors), ''))

print(f"{'Cultivo':28s} {'n':>4s} {'h':>2s} {'MAPE persist':>12s} {'MAPE ETS':>12s}")
print('-'*68)
for crop, n, h, mb, me, note in results:
    if note:
        print(f"{crop:28s} {n:4d}      {note}")
    else:
        win = 'ETS GANA' if me < mb-0.5 else ('empate' if abs(me-mb)<=0.5 else 'persist gana')
        print(f"{crop:28s} {n:4d} {h:2d} {mb:12.1f} {me:12.1f}  {win}")

print('\n=== RESUMEN por horizonte ===')
for h in H:
    rows = [r for r in results if r[2]==h and r[3] is not None]
    if rows:
        mb = np.mean([r[3] for r in rows]); me = np.mean([r[4] for r in rows])
        print(f"h={h}: persistencia={mb:.1f}% | ETS={me:.1f}% | mejora={mb-me:+.1f} pts")
