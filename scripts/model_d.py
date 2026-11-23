import pandas as pd, numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder

mun = pd.read_csv('data/chiapas_municipal_2003_2025.csv')
oni = pd.read_csv('data/oni_anual_1950_2026.csv')
key = ['Nommunicipio','Nomcultivo','Nomcicloproductivo','Nommodalidad']
mun = mun.sort_values(key + ['Anio']).reset_index(drop=True)
for k in [1,2,3]:
    mun[f'lag{k}'] = mun.groupby(key)['Volumenproduccion'].shift(k)
oni_map = dict(zip(oni['Anio'], oni['ONI']))
# ONI del MISMO año (techo: asumiendo pronóstico perfecto de ENSO)
mun['ONI_same'] = mun['Anio'].map(lambda y: oni_map.get(y, np.nan))

CATS = ['Nomcultivo','Nomcicloproductivo','Nommodalidad']
def onehot(df, enc=None):
    c = df[CATS].astype(str).values
    if enc is None: enc = OneHotEncoder(handle_unknown='ignore', sparse_output=False).fit(c)
    return enc.transform(c), enc

def run(use_oni_same):
    res=[]
    for t in range(2011, 2025):
        feats = ['lag1','lag2','lag3'] + (['ONI_same'] if use_oni_same else [])
        train = mun[mun['Anio']<=t].dropna(subset=feats+['Volumenproduccion'])
        test  = mun[mun['Anio']==t+1].dropna(subset=feats).copy()
        if test.empty or train.empty: continue
        Xtr = np.hstack([np.log1p(train[['lag1','lag2','lag3']].values)] + ([train[['ONI_same']].values] if use_oni_same else []))
        Xtr = np.hstack([Xtr, onehot(train)[0]])
        Xte = np.hstack([np.log1p(test[['lag1','lag2','lag3']].values)] + ([test[['ONI_same']].values] if use_oni_same else []))
        Xte = np.hstack([Xte, onehot(test, onehot(train)[1])[0]])
        m = Ridge(alpha=10.0).fit(Xtr, np.log1p(train['Volumenproduccion'].values))
        test['pred']=np.expm1(m.predict(Xte))
        g=test.groupby('Nomcultivo').agg(a=('Volumenproduccion','sum'),p=('pred','sum'),ps=('lag1','sum'))
        for crop,r in g.iterrows(): res.append((t+1,crop,r['a'],r['ps'],r['p']))
    res=pd.DataFrame(res,columns=['Anio','crop','a','ps','p'])
    res['ape_ps']=abs(res.a-res.ps)/res.a*100; res['ape_m']=abs(res.a-res.p)/res.a*100
    return res

base = run(False)
techo = run(True)
print("=== ¿el clima ayuda? (h=1, 2012-2025) ===")
print(f"  persistencia:              {base.ape_ps.mean():6.1f}%")
print(f"  Ridge (solo rezagos):      {base.ape_m.mean():6.1f}%")
print(f"  Ridge + ONI (mismo año)*:  {techo.ape_m.mean():6.1f}%   (*techo: asume ENSO perfectamente pronosticado)")
print()
print("por cultivo (persist | rezagos | +ONI mismo año):")
for crop,r in techo.groupby('crop')[['ape_ps','ape_m']].mean().sort_values('ape_ps').iterrows():
    rb=base[base.crop==crop]['ape_m'].mean()
    print(f"  {crop:28s} {r['ape_ps']:6.1f} {rb:6.1f} {r['ape_m']:6.1f}")
