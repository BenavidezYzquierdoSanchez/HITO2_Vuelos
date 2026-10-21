# Diseño y filtros del HTML original

La aplicación reutiliza el CSS del HTML adjunto y adapta sus estilos a los controles de Streamlit. Paleta #070d18, #10192b y #2ee6a6; tipografía Manrope con alternativa local; tarjetas con degradados; seis KPI; chips de filtros y paneles en dos columnas.

## Navegación y controles

Panorama, Estacionalidad, Geografía, Aerolíneas y Metodología. Año, mes, aerolínea, radio de vuelo, estado de origen y criterio de atraso ≥15/≥60. Selectores con opción Todos. Cargar JSON, Exportar CSV y Limpiar filtros funcionan. Para pantalla completa utiliza F11. Los chips resumen la selección; se modifica desde los selectores.

El umbral actualiza la tasa y la serie de atraso, sin cambiar puntualidad ni el denominador de demora media. Radio muestra los límites del HTML, aunque el JSON no permite verificar distancias individuales. US se identifica como nacional. El mapa conserva filtros propios de aeropuertos porque hubs no tiene fecha ni aerolínea. No se reproducen matrices simuladas día/hora ni datos de ejemplo.

## Actualizar

Detén Streamlit con Ctrl+C. Copia desde este ZIP app.py, src/analysis.py, .streamlit/config.toml y verificar.py a las mismas carpetas de tu proyecto. Conserva tu entorno .venv. No hacen falta nuevas dependencias.

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Recarga el navegador con Ctrl+F5 si conserva el diseño anterior. Sube esos cuatro archivos a GitHub si ya publicaste el proyecto.

## Verificación y alcance

Pruebas AppTest correctas: cuatro vistas, seis filtros, selección de año/aerolínea, umbral ≥60, ausencia de resultados, limpieza, cinco secciones y mapa. Se comprobó carga del payload y rechazo de cube vacío. No se realizó inspección visual en navegador en este entorno; la adaptación usa componentes Streamlit y no promete identidad píxel a píxel. Manrope y el fondo cartográfico requieren internet.

El informe y notebook conservan su análisis original. Esta actualización cambia la interfaz y aumenta de cuatro a seis KPI; los cuatro gráficos de Panorama siguen conectados. Las definiciones actualizadas se muestran en Metodología.
