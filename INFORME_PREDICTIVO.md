# Informe — Modelo predictivo de producción agrícola (Chiapas)

> Análisis y validación de la predictibilidad de la producción agrícola de
> Chiapas (SIAP), con dos enfoques comparados (serie temporal estatal y panel
> municipal), variables externas (clima, precio, superficie) y un modelo por
> escenarios para los cultivos de decisión humana.

---

## 1. Resumen ejecutivo

Se construyeron dos datasets limpios (serie estatal 1980–2025 y panel municipal
2003–2025) y se validaron varios modelos con validación temporal *walk-forward*
(sin fuga de datos). El resultado central es claro y honesto:

> **Ningún modelo basado en la historia de producción —ni siquiera añadiendo
> clima (ENSO), precio y superficie sembrada— supera a la persistencia
> ("repetir el año anterior").**

La producción anual a nivel municipal está dominada por shocks locales e
idiosincráticos (clima sub-anual, plagas, decisiones de productores) que no
están en ningún dataset disponible. Un "pronóstico de producción a mediano
plazo" con precisión fina **no es defendible con estos datos**. Lo que sí es
útil y defendible se presenta al final: un forecast agregado a nivel estatal
con intervalos de confianza, y un modelo por escenarios para los cultivos cuya
dinámica es una decisión humana (pastos→ganadería, palma→commodity).

---

## 2. El hallazgo inicial: el "modelo a 5 años" no existe

El usuario recordaba haber hecho un "modelo predictivo a 5 años". La revisión
del historial de git reveló que **ese modelo nunca existió en este repo**:

- El único notebook original (`Copia_de_EDA_METS_OPS_1.ipynb`) era una **copia
  del proyecto de oncología** (metástasis cerebrales). Hacía tests chi-cuadrado
  entre `CIRUGÍA PREVIA`, `TRATAMIENTO SISTÉMICO` y `RESPUESTA (CRITERIOS RANO)`.
- El "5 años" es una confusión con el proyecto de oncología (tiempo a
  progresión), no con agricultura.

Además, aunque existiera, un horizonte de 5 años con datos anuales es
extrapolar ~25% de la historia disponible: la incertidumbre lo vuelve
inutilizable (ver sección 6).

---

## 3. Datos construidos

Fuente oficial SIAP (`nube.agricultura.gob.mx`, datos abiertos). Archivos en `data/`:

| Archivo | Descripción | Cobertura |
|---|---|---|
| `chiapas_estatal_1980_2025.csv` | Serie estatal, top 10 cultivos | 1980–2025 |
| `chiapas_municipal_2003_2025.csv` | Panel municipal (125 municipios) | 2003–2025 |
| `oni_anual_1950_2026.csv` | Índice ENSO (NOAA ONI), media anual | 1950–2026 |
| `forecast_core_2026_2030.csv` | Forecast estatal con intervalos | 2026–2030 |

**Cobertura real de los 10 cultivos top (hallazgo clave):**

- 7 cultivos con **46 años completos**: caña de azúcar, maíz grano, plátano,
  café cereza, mango, frijol, tomate rojo.
- **Pastos y praderas**: solo 2003+ (21 años), con un **hueco en 2020–2021**
  en la propia fuente SIAP. Es el cultivo #1 por volumen pero el de peor serie.
- **Palma africana**: desde 1983 (su introducción).
- **Papaya**: desde 1994.

### Notas técnicas de los datos (drift de esquema SIAP)

- Encoding mixto: el CSV preexistente es **UTF-8**; los descargados SIAP son
  **latin-1**.
- La columna de cultivo cambia de nombre según el año (`Nomcultivo` vs
  `Nomcultivo Sin Um` en 2020); la de precio (`Precio` vs `Preciomediorural`).
- Los datos nacionales 1980–2002 tienen filas por ciclo×modalidad → hay que
  agregar por (año, cultivo).

---

## 4. Metodología de validación

- **Walk-forward temporal** (ventana expansiva): se entrena con datos hasta el
  año *t* y se predice *t+1*, *t+2*, *t+3*. Nunca se usa el futuro.
- **Baseline honesto**: persistencia (repetir el año anterior). Si un modelo no
  le gana a esto, no aporta nada.
- **Métrica**: MAPE (error porcentual absoluto medio).
- **Sin fuga de datos**: los modelos de panel usan solo rezagos; las variables
  contemporáneas al año a predecir se excluyeron.

---

## 5. Resultados: por qué gana la persistencia

MAPE a 1 año (validación walk-forward):

| Modelo | MAPE | ¿Supera a persistencia? |
|---|---|---|
| **Persistencia** | **6.4%** (nivel serie) | — baseline |
| Serie temporal (ETS, 46 años, estatal) | 16.1% | ❌ |
| Panel Ridge (solo rezagos) | 10.4% | ❌ |
| Panel Ridge + Sembrada/Precio/ENSO | 11.4% | ❌ |
| Panel Ridge + ENSO del año a predecir (techo) | 10.8% | ❌ |
| Panel Gradient Boosting | 20% | ❌ (sobreajusta) |

Interpretación técnica:

1. **La persistencia es un piso muy alto.** A nivel serie municipal
   (municipio×cultivo×ciclo×modalidad), "repetir el año anterior" ya captura
   casi toda la estructura estable; el error residual es ruido.

2. **El ENSO anual es demasiado grueso.** La producción la define la lluvia en
   una *ventana fenológica* específica (p. ej., floración del maíz), no el
   promedio anual de El Niño. Por eso ni con ENSO "perfecto" ayuda.

3. **Las decisiones humanas son quiebres estructurales.** La expansión de
   pastos (ganadería) y de palma (commodity) son cambios de régimen que un
   modelo extrapolativo no puede anticipar. Pero dejan un rastro *adelantado*
   medible: la superficie sembrada (`Sembrada`).

Señales que confirman lo anterior (datos duros):

- Palma africana: `Sembrada` creció de **16,800 ha (2003) a 45,400 ha (2019)**,
  y correlaciona **0.84 con el volumen 1–3 años después** (cultivo perenne,
  tarda en producir).
- Pastos: `Sembrada` saltó de **65,000 ha (2019) a 87,000 ha (2022)**, luego
  contrajo a **60,000 ha (2025)** — la reconversión ganadera y su reversión.

---

## 6. Forecast estatal agregado (nivel estado, 7 cultivos core)

Los 7 cultivos con serie completa (caña, maíz, plátano, café, mango, frijol,
tomate rojo) se agregan a un total estatal estable. Modelo: *random walk con
deriva* (ARIMA(0,1,0) + tendencia), que es la extensión natural de la
persistencia, ajustado en escala logarítmica (intervalos positivos).

| Año | Central | IC 80% | IC 95% |
|---|---|---|---|
| 2026 | 6.04 M ton | [5.45, 6.69] | [5.17, 7.06] |
| 2027 | 6.15 M ton | [5.33, 7.11] | [4.93, 7.67] |
| 2028 | 6.27 M ton | [5.25, 7.48] | [4.78, 8.21] |
| 2029 | 6.39 M ton | [5.21, 7.83] | [4.67, 8.72] |
| 2030 | 6.50 M ton | [5.18, 8.17] | [4.59, 9.22] |

**Lectura honesta:** la producción estatal de los cultivos estables ronda los
**6.0–6.5 M ton** en el próximo lustro, con una incertidumbre que crece de
**±10% (1 año) a ±23% (5 años)** al 80% de confianza. Es un rango de
planificación, no un número puntual.

---

## 7. Modelo por escenarios (palma y pastos)

Para los dos cultivos cuya dinámica es una **decisión humana**, en lugar de
"predecir" se proyecta usando la superficie sembrada como palanca. El modelo es
transparente: `Volumen = Sembrada × cosechada% × rendimiento`.

### Palma africana (perenne, rezago ~3 años)

`Sembrada 2025 = 43,938 ha`, rendimiento ~14.7 ton/ha, 87% cosechada.

| Escenario | 2026 | 2027 | 2028 | 2029 | 2030 |
|---|---|---|---|---|---|
| Expansión (+3%/año) | 0.56 | 0.56 | 0.56 | 0.58 | 0.60 |
| Estable | 0.56 | 0.56 | 0.56 | 0.56 | 0.56 |
| Contracción (−3%/año) | 0.56 | 0.56 | 0.56 | 0.55 | 0.53 |

*(M ton. Nótese que la decisión de expandir hoy recién se refleja ~2029, por el
rezago del cultivo perenne.)*

### Pastos y praderas (anual, sin rezago)

`Sembrada 2025 = 60,489 ha`, rendimiento ~28.5 ton/ha.

| Escenario | 2026 | 2027 | 2028 | 2029 | 2030 |
|---|---|---|---|---|---|
| Expansión (+5%/año) | 1.81 | 1.90 | 2.00 | 2.10 | 2.20 |
| Estable | 1.72 | 1.72 | 1.72 | 1.72 | 1.72 |
| Contracción (−5%/año) | 1.64 | 1.56 | 1.48 | 1.40 | 1.33 |

*(M ton. Aun en expansión, 2030 quedaría por debajo del pico 2022 de 2.31 M
ton, reflejando la contracción reciente de la superficie.)*

---

## 8. Conclusiones y limitaciones

1. **La persistencia es el mejor predictor disponible.** Para planificación
   operativa, "el año que viene ≈ este año ±13% (municipal) / ±10–23% (estatal)"
   es un número útil y honesto.
2. **El forecast estatal agregado es el deliverable más sólido**: 6.0–6.5 M ton
   con intervalos explícitos.
3. **Los cultivos de decisión humana (palma, pastos) se modelan por escenarios,
   no por extrapolación**: la palanca es la superficie sembrada, y el rezago
   del cultivo perenne es un hallazgo relevante (las decisiones de hoy impactan
   ~2029).
4. **Limitación principal**: el signal climático real es sub-anual (lluvia y
   temperatura por ventana fenológica), no el ENSO anual. Ganarle a la
   persistencia exige datos climáticos de alta resolución (CHIRPS/ERA5)
   emparejados al calendario de cada cultivo — un proyecto de ingeniería de
   datos aparte.

---

## 9. Cómo reproducir

```bash
pip install -r requirements.txt

# 1. Reconstruir datasets (descarga SIAP + limpieza)
#    scripts de adquisición en /tmp/opencode/siap/build.py (ver memoria del proyecto)

# 2. Forecast estatal (sección 6)
python scripts/forecast_estatal.py

# 3. Escenarios palma/pastos (sección 7)
python scripts/escenarios.py

# 4. Validación walk-forward (sección 5)
python scripts/model_a.py      # serie temporal ETS vs persistencia
python scripts/model_b2.py     # panel Ridge vs persistencia
python scripts/model_c.py      # panel + externas (Sembrada/Precio/ENSO)
python scripts/model_d.py      # techo climático (ENSO del año a predecir)
```

Datos generados en `data/`; scripts reproducibles en `scripts/`.
