import pandas as pd, numpy as np

# parse ONI (NOAA)
df = pd.read_csv('/tmp/opencode/oni.txt', sep=r'\s+', skiprows=1,
                 names=['SEAS','YR','TOTAL','ANOM'])
# anual mean de ANOM por año
oni = df.groupby('YR')['ANOM'].mean()
# guardar
out = pd.DataFrame({'Anio': oni.index.astype(int), 'ONI': oni.values})
out.to_csv('data/oni_anual_1950_2026.csv', index=False, encoding='utf-8')
# sanity check años clave
for y in [1983, 1998, 2010, 2011, 2016, 2020, 2021, 2023]:
    print(f"ONI {y}: {oni.get(y, float('nan')):+.2f}")
print("(negativo=La Niña, positivo=El Niño; 2015-16 y 2023 = El Niño, 2020-21 = La Niña)")
