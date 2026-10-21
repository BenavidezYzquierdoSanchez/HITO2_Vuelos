# Hito 2 · US Flights

Comienza por **Informe_HITO2.docx**. El notebook ejecutado contiene diez gráficos, sus preguntas e interpretaciones. La aplicación Streamlit incluye cuatro KPI y cinco visualizaciones: cuatro conectadas con filtros comunes y un mapa con filtros independientes.

**Estado real:** aplicación funcional local. La publicación y URL pública exigidas por la rúbrica siguen pendientes; no se afirma cumplimiento total ni se garantiza una nota. Consulta FICHA_TECNICA.md.

## Inicio en Windows

Instala Python 3.12, descomprime todo y abre PowerShell en esta carpeta.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Se abrirá http://localhost:8501. Mantén la terminal abierta. Pulsa Ctrl+C para detener.

## Inicio en macOS o Linux

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Reproducir y comprobar

Con el entorno activado, ejecuta:

```bash
python ejecutar_notebook.py
python verificar.py
```

En Windows puedes sustituir `python` por `.venv\Scripts\python.exe`; en macOS/Linux, por `.venv/bin/python`. El ejecutor registra un kernel llamado hito2-vuelos en tu usuario y ejecuta todas las celdas; no necesita una interfaz de Jupyter. Para una interfaz puedes abrir el notebook en VS Code con soporte Jupyter. Los resultados están guardados en el notebook entregado.

## Archivos

- `Informe_HITO2.docx`: desarrollo académico y matriz de trazabilidad de la hoja 2.
- `HITO2_Analisis.ipynb`: notebook ejecutado con diez figuras.
- `app.py`: aplicación de Streamlit.
- `src/analysis.py`: carga, auditoría, KPI y funciones de graficado compartidas.
- `data/data_vuelos_dashboard_final.json`: copia exacta del JSON adjunto.
- `referencias/`: HTML y rúbrica originales, conservados sin modificaciones.
- `resultados/`: auditoría por fila, datos validados, tablas, imágenes y verificación.
- `requirements.txt`: versiones directas del entorno utilizado.
- `.streamlit/config.toml`: tema coherente con el wireframe.
- `FICHA_TECNICA.md`: método, fuentes y publicación pendiente.
- `MANIFEST_SHA256.txt`: huellas de integridad antes de empaquetar.

## Lectura correcta

Se conservan 3.344 filas y se analizan 3.202 que pasan los controles: 142 excluidas, 2.945.667 operaciones. Ningún valor se reemplaza por los ejemplos del HTML. Las métricas validadas son descriptivas y no representan una verdad corregida del universo. Los filtros del mapa son independientes porque hubs no contiene fecha ni aerolínea. Hay 31 hubs ubicados y cuatro sin coordenadas. 2026 solo incluye enero–mayo.

No uses el HTML original como resultado validado: incluye datos de muestra y una matriz día–hora simulada. Se conserva únicamente como referencia. No se ha preparado un modelo predictivo porque no lo pide la rúbrica y los agregados no justifican hacerlo.

Verificación de esta entrega: Python 3.12.14; notebook ejecutado secuencialmente con IPython en proceso mediante `python ejecutar_notebook.py --sin-kernel` porque el entorno de preparación no permite sockets locales. Todas las celdas se ejecutaron y sus salidas se guardaron. La app se comprobó con Streamlit AppTest; no se verificó un servidor público ni las teselas en navegador.

Febrero–junio de 2023 no conserva filas válidas. Abril se compara entre 2021, 2022, 2024, 2025 y 2026.
