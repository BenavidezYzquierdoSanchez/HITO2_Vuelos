# Ficha técnica

## Objeto y estado

US Flights: puntualidad, demoras, cancelaciones y geografía exploratoria. Entrega según HITO 2 y rúbrica de su segunda hoja.

**URL de aplicación desplegada: PENDIENTE.** La aplicación ha sido ejecutada mediante pruebas locales; no se ha publicado en una cuenta externa. Esta condición impide declarar completo el criterio de despliegue. Una URL localhost no es un enlace público.

## Fuentes y trazabilidad

1. JSON adjunto `data_vuelos_dashboard_final.json`: 3.344 agregados, 35 hubs, 10 bloques horarios y un resumen dow. No acredita fuente primaria, licencia, fecha de extracción ni representatividad. Se conserva su contenido exacto.
2. HTML adjunto `dashboard_US_Flights_sidebar.html`: wireframe, definiciones y coordenadas AIRPORT_COORDS. Sus ejemplos y simulaciones no son datos observados. No se transfieren al análisis.
3. DOCX adjunto `HITO 2.docx`: estructura de entrega y rúbrica. Original conservado en referencias.
4. Documentación oficial de Streamlit consultada el 20/10/2026:
   - https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
   - https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization

## Datos preparados

Unidad: año, mes, aerolínea, OriginState, alcance. Período enero de 2021–mayo de 2026. OriginState solo vale US. Auditoría: esquema, conversión, finitud, nulos, no negatividad, conteos enteros, fechas válidas, clave única, balance de estados, subconjunto delayed60 y conciliación de minutos. El balance de causas es una hipótesis de consistencia acorde con el HTML, pendiente de confirmación del proveedor.

Los originales no se modifican. `auditoria_filas.csv` agrega source_row (posición 1-indexada en cube), issues y valid. Se excluyen 142 filas del análisis principal y se preserva acceso al bruto mediante modo diagnóstico. CSV validados: 3.202 filas y 35.436.522 operaciones. No se realizan imputaciones, promedios de porcentajes ni expansión artificial a vuelos individuales.

## KPI e incertidumbre

- Operaciones: suma de ops.
- Puntualidad: 100 × suma de ontime / suma de ops.
- Cancelación: 100 × suma de cancel / suma de ops.
- Demora media de retrasados: suma de sumDelayMin / suma de delayed15; sin denominador se muestra ausencia de casos.
- Wilson 95% para tasas por aerolínea, bajo modelo binomial independiente. No cubre sesgo de selección ni errores, ni dependencia entre vuelos. Si la tabla es censal, la tasa observada no tiene error muestral; el intervalo solo ilustra un proceso hipotético.

## Interactividad y geografía

Cuatro vistas operacionales comparten filtros de año, mes, aerolínea, alcance y calidad. El mapa constituye la quinta visualización, con filtro propio de códigos IATA. Se une hubs al diccionario del HTML: 31/35 ubicados, faltan IAH, LGA, DCA y FLL. No se inventan estados ni coordenadas. La tabla completa conserva esos hubs. Los valores de hubs no se cruzan con cube y no reciben sus filtros. El mapa usa Mercator, área proporcional a vuelos y escala de color fija 65–90%; el fondo puede requerir internet.

## Dependencias y ejecución

Python 3.12 recomendado. Versiones directas en requirements.txt. `README.md` incluye instrucciones para Windows, macOS y Linux. `python ejecutar_notebook.py` ejecuta todas las celdas; `python verificar.py` valida cálculos y estados de la app. `python -m streamlit run app.py` inicia la app en http://localhost:8501. La instalación inicial requiere acceso al repositorio de paquetes. No se descarga ningún dataset.

## Publicar en Streamlit Community Cloud

1. Iniciar sesión en GitHub y crear un repositorio autorizado para estos datos.
2. Subir el contenido de HITO2_Vuelos a la raíz del repositorio, incluidas data, src, referencias y .streamlit. No subir un ZIP como sustituto del código.
3. Iniciar sesión en https://share.streamlit.io y elegir Create app.
4. Seleccionar repositorio, rama y archivo principal app.py; configurar Python 3.12.
5. Desplegar y comprobar cuatro KPI, cuatro vistas operacionales, selección vacía y mapa con ATL.
6. Copiar aquí la URL real que entregue el servicio y verificar que el docente pueda acceder. Guardar evidencia de esa prueba antes de presentar.

No se ha realizado este paso porque no se dispone de una cuenta/repositorio de alojamiento conectado para el proyecto. No se incluyen enlaces simulados ni una declaración de publicación.

## Limitaciones

Auditoría interna no prueba autenticidad. Exclusiones afectan 7,67% de operaciones y son especialmente relevantes en 2023. No hay microdatos para corregir dependencia, controlar rutas o verificar demora real. No se conocen los límites de Haul. La tabla hourly no dispone de conteos, período ni zona horaria; dow no permite comparación semanal. Datos de 2026 parciales; comparación interanual de abril con segmentos comunes. No hay inferencia causal ni pronósticos.

Verificación de esta entrega: Python 3.12.14; notebook ejecutado secuencialmente con IPython en proceso mediante `python ejecutar_notebook.py --sin-kernel` porque el entorno de preparación no permite sockets locales. Todas las celdas se ejecutaron y sus salidas se guardaron. La app se comprobó con Streamlit AppTest; no se verificó un servidor público ni las teselas en navegador.

Febrero–junio de 2023 no conserva filas válidas. Abril se compara entre 2021, 2022, 2024, 2025 y 2026.
