import pandas as pd, numpy as np
from statsmodels.tsa.arima.model import ARIMA

est = pd.read_csv('data/chiapas_estatal_1980_2025.csv')
CORE = ['Caña de azúcar','Maíz grano','Plátano','Café cereza','Mango','Frijol','Tomate rojo (jitomate)']
total = est[est['Nomcultivo'].isin(CORE)].groupby('Anio')['Volumenproduccion'].sum()
print(f"Serie estatal CORE (7 cultivos): {total.index.min()}..{total.index.max()}, {len(total)} años")
print(f"Último (2025): {total.iloc[-1]/1e6:.2f} M ton | Promedio 5 años recientes: {total.tail(5).mean()/1e6:.2f} M ton")

# forecast en log (intervalos positivos, multiplicativos) con random-walk + drift
ylog = np.log(total.values.astype(float))
model = ARIMA(ylog, order=(0,1,0), trend='t').fit()
fc = model.get_forecast(5)
m = np.exp(fc.predicted_mean)
c80 = np.exp(fc.conf_int(alpha=0.2))
c95 = np.exp(fc.conf_int(alpha=0.05))

years = list(range(2026, 2031))
print(f"\n=== FORECAST 2026-2030 (M ton, CORE 7 cultivos) ===")
print(f"{'Año':>6} {'central':>9} {'IC 80%':>20} {'IC 95%':>22}")
for i, yr in enumerate(years):
    print(f"{yr:>6} {m[i]/1e6:>9.2f} [{c80[i,0]/1e6:>7.2f},{c80[i,1]/1e6:>7.2f}]  [{c95[i,0]/1e6:>7.2f},{c95[i,1]/1e6:>7.2f}]")

print(f"\n=== incertidumbre (amplitud relativa del IC80, % del valor central) ===")
for i, yr in enumerate(years):
    w = (c80[i,1]-c80[i,0])/2/m[i]*100
    print(f"  {yr}: ±{w:.0f}%")

# guardar forecast para el informe
out = pd.DataFrame({'Anio': years, 'central': m, 'ic80_lo': c80[:,0], 'ic80_hi': c80[:,1],
                    'ic95_lo': c95[:,0], 'ic95_hi': c95[:,1]})
out.to_csv('data/forecast_core_2026_2030.csv', index=False, encoding='utf-8')
print("\nGuardado en data/forecast_core_2026_2030.csv")
