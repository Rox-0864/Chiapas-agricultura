import pandas as pd, numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder

mun = pd.read_csv('data/chiapas_municipal_2003_2025.csv')
key = ['Nommunicipio','Nomcultivo','Nomcicloproductivo','Nommodalidad']
mun = mun.sort_values(key + ['Anio']).reset_index(drop=True)
for k in [1,2,3]:
    mun[f'lag{k}'] = mun.groupby(key)['Volumenproduccion'].shift(k)

# modelo simple y robusto: Ridge en log(vol) con rezagos + dummies de cultivo/ciclo/modalidad
# (sin municipio para no sobreajustar; el nivel municipal queda en el rezago de cada serie)
def build_X(df, enc=None):
    lag = np.log1p(df[['lag1','lag2','lag3']].fillna(0).values)
    cats = df[['Nomcultivo','Nomcicloproductivo','Nommodalidad']].astype(str).values
    if enc is None:
        enc = OneHotEncoder(handle_unknown='ignore', sparse_output=False).fit(cats)
    oh = enc.transform(cats)
    return np.hstack([lag, oh]), enc

results = []
for t in range(2011, 2025):
    train = mun[(mun['Anio'] <= t) & mun['lag3'].notna()]
    test  = mun[(mun['Anio'] == t+1) & mun['lag1'].notna()].copy()
    if test.empty or train.empty: continue
    Xtr, enc = build_X(train); Xte, _ = build_X(test, enc)
    ytr = np.log1p(train['Volumenproduccion'].values)
    m = Ridge(alpha=10.0).fit(Xtr, ytr)
    test['pred'] = np.expm1(m.predict(Xte))
    test['persist'] = test['lag1']
    g = test.groupby('Nomcultivo').agg(a=('Volumenproduccion','sum'),
                                       p=('pred','sum'), ps=('persist','sum'))
    for crop, r in g.iterrows():
        results.append((t+1, crop, r['a'], r['ps'], r['p']))

res = pd.DataFrame(results, columns=['Anio','crop','a','ps','p'])
res['ape_ps'] = abs(res.a-res.ps)/res.a*100
res['ape_m'] = abs(res.a-res.p)/res.a*100
print("=== Ridge(log) con rezagos + dummies vs persistencia ===")
print(f"{'Cultivo':28s} {'persist':>9s} {'Ridge':>9s}")
for crop, r in res.groupby('crop')[['ape_ps','ape_m']].mean().sort_values('ape_ps').iterrows():
    win = 'RIDGE GANA' if r['ape_m']<r['ape_ps']-0.5 else ('empate' if abs(r['ape_m']-r['ape_ps'])<=0.5 else 'persist gana')
    print(f"{crop:28s} {r['ape_ps']:9.1f} {r['ape_m']:9.1f}  {win}")
print(f"\nGLOBAL: persistencia={res.ape_ps.mean():.1f}% | Ridge={res.ape_m.mean():.1f}%")
