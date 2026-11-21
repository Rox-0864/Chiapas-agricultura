# Guía de estudio — errores del proyecto original y sus correcciones

Al revisar el repositorio de Chiapas-agricultura, encontramos los siguientes
problemas. Cada uno sigue el formato **problema → por qué es un error →
corrección**.

---

## 1. El error principal: notebook copiado de otro proyecto

### El problema
El único notebook del repo (`Copia_de_EDA_METS_OPS_1.ipynb`) **no analizaba
agricultura**. Era una copia del proyecto de oncología (metástasis / METS OPS).
Sus celdas hablaban de:

- `EXPEDIENTE`, `NOMBRE` → identificadores de **pacientes**.
- `RESPUESTA (CRITERIOS RANO)` → criterios de respuesta **oncológica**.
- `CIRUGÍA PREVIA`, `TRATAMIENTO SISTEMICO`, `TUMOR PRIMARIO`, `LOCALIZACIÓN` →
  variables clínicas.

Ninguna de esas columnas existe en el CSV agrícola (que tiene `Nomcultivo`,
`Sembrada`, `Rendimiento`, etc.).

### Por qué es un error
El notebook estaba **desconectado del dataset real**. Era un copy-paste del
proyecto de oncología que nunca se adaptó. Quien lo corriera obtendría errores
(`KeyError: 'EXPEDIENTE'`) o, peor, creería que el análisis está hecho cuando no
lo está.

### La corrección
Se reemplazó por `analisis_agricola.ipynb`, un EDA real sobre los datos de
Chiapas: top cultivos, tendencias, rendimiento, precios, municipios y
siniestralidad.

---

## 2. Sin documentación

### El problema
No había `README.md`, ni `requirements.txt`, ni `.gitignore`.

### Por qué es un error
Sin README nadie sabe qué es el proyecto ni cómo correrlo; sin dependencias
declaradas no es reproducible.

### La corrección
Se agregaron `README.md` (con los hallazgos y el uso), `requirements.txt`
(pandas, matplotlib, seaborn, jupyter) y `.gitignore`.

---

## 3. Sin análisis reproducible

### El problema
No había forma de regenerar los resultados: solo un notebook copiado.

### La corrección
Se agregó `scripts/eda.py` que ejecuta el EDA completo y guarda los gráficos en
`results/` + un `results/resumen.csv`. Así el análisis es reproducible por línea
de comandos, no solo interactivo.

---

## 4. Código no modular

### El problema
Todo el (supuesto) análisis estaba en un notebook plano, sin funciones
reutilizables.

### La corrección
Se separó en módulos reutilizables:
- `src/data.py` → carga + transformaciones (tasa de siniestralidad, top cultivos,
  resumen).
- `src/plots.py` → funciones de visualización (cada una guarda su gráfico).

El notebook y el script comparten `src/data.py`, evitando duplicación.

---

## Resumen rápido

| # | Error | Corrección |
|---|-------|------------|
| 1 | Notebook copiado del proyecto de oncología | EDA real de agricultura |
| 2 | Sin README/requirements/gitignore | documentación completa |
| 3 | Sin análisis reproducible | `scripts/eda.py` + `results/` |
| 4 | Código no modular | `src/data.py` + `src/plots.py` |

---

## Lección transversal

Este es el mismo patrón que apareció en otros repos (s20-10-data, etc.): **usar
un notebook/archivo de otro proyecto como plantilla sin adaptarlo**. El nombre
"`Copia_de_EDA_METS_OPS_1.ipynb`" lo delata: era una copia del EDA de oncología
("METS OPS") renombrada, pero con el contenido intacto.

**Regla:** antes de reutilizar un notebook de otro proyecto, verificá que las
columnas y el objetivo coincidan con el dataset actual. Un `KeyError` al correr
es la señal más clara de que la plantilla no corresponde.
