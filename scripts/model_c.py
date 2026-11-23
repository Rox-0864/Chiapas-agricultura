import pandas as pd, numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder

mun = pd.read_csv('data/chiapas_municipal_2003_2025.csv')
oni = pd.read_csv('data/oni_anual_1950_2026.csv')

key = ['Nommunicipio','Nomcultivo','Nomcicloproductivo','Nommodalidad']
mun = mun.sort_values(key + ['Anio']).reset_index(drop=True)
for col in ['Volumenproduccion','Sembrada','Precio','Siniestrada']:
    mun[col+'_lag1'] = mun.groupby(key)[col].shift(1)
for k in [2,3]:
    mun[f'Volumenproduccion_lag{k}'] = mun.groupby(key)['Volumenproduccion'].shift(k)
oni_map = dict(zip(oni['Anio'], oni['ONI']))
mun['ONI_lag1'] = mun['Anio'].map(lambda y: oni_map.get(y-1, np.nan))

LOG_VARS = ['Volumenproduccion_lag1','Volumenproduccion_lag2','Volumenproduccion_lag3',
            'Sembrada_lag1','Precio_lag1','Siniestrada_lag1']
CATS = ['Nomcultivo','Nomcicloproductivo','Nommodalidad']

def Xmat(df, log_vars, raw_vars=None):
    X = np.log1p(df[log_vars].values)
    if raw_vars:
        X = np.hstack([X, df[raw_vars].values])
    return X

def onehot(df, enc=None):
    cats = df[CATS].astype(str).values
    if enc is None:
        enc = OneHotEncoder(handle_unknown='ignore', sparse_output=False).fit(cats)
    return enc.transform(cats), enc

def run(log_vars, raw_vars=None):
    res = []
    for t in range(2011, 2025):
        vars_ = log_vars + (raw_vars or [])
        train = mun[mun['Anio'] <= t].dropna(subset=vars_+['Volumenproduccion'])
        test  = mun[mun['Anio'] == t+1].dropna(subset=vars_).copy()
        if test.empty or train.empty: continue
        Xtr = Xmat(train, log_vars, raw_vars)
        oh_tr, enc = onehot(train)
        Xtr = np.hstack([Xtr, oh_tr])
        Xte = np.hstack([Xmat(test, log_vars, raw_vars), onehot(test, enc)[0]])
        m = Ridge(alpha=10.0).fit(Xtr, np.log1p(train['Volumenproduccion'].values))
        test['pred'] = np.expm1(m.predict(Xte))
        g = test.groupby('Nomcultivo').agg(a=('Volumenproduccion','sum'),
                                           p=('pred','sum'),
                                           ps=('Volumenproduccion_lag1','sum'))
        for crop, r in g.iterrows():
            res.append((t+1, crop, r['a'], r['ps'], r['p']))
    res = pd.DataFrame(res, columns=['Anio','crop','a','ps','p'])
    res['ape_ps'] = abs(res.a-res.ps)/res.a*100
    res['ape_m'] = abs(res.a-res.p)/res.a*100
    return res

base_log = ['Volumenproduccion_lag1','Volumenproduccion_lag2','Volumenproduccion_lag3']
ext_log  = base_log + ['Sembrada_lag1','Precio_lag1','Siniestrada_lag1']

res_base = run(base_log)
res_ext  = run(ext_log, raw_vars=['ONI_lag1'])

print("=== MAPE global h=1 (2012-2025) ===")
print(f"  persistencia:                 {res_base.ape_ps.mean():6.1f}%")
print(f"  Ridge (solo rezagos):         {res_base.ape_m.mean():6.1f}%")
print(f"  Ridge + Sembrada/Precio/ONI:  {res_ext.ape_m.mean():6.1f}%")

print("\n=== por cultivo (persist | rezagos | +externas) ===")
print(f"{'Cultivo':28s} {'persist':>8s} {'rezagos':>8s} {'+externas':>9s}")
for crop, r in res_ext.groupby('crop')[['ape_ps','ape_m']].mean().sort_values('ape_ps').iterrows():
    rb = res_base[res_base.crop==crop]['ape_m'].mean()
    gana = '  <== GANA' if r['ape_m'] < r['ape_ps']-0.5 else ''
    print(f"{crop:28s} {r['ape_ps']:8.1f} {rb:8.1f} {r['ape_m']:9.1f}{gana}")
