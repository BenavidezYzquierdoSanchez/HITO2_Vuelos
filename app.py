"""Interfaz Streamlit basada en el dashboard HTML original."""
import json,re,html
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.analysis import load,aggregate,geo,CAUSES,LABELS,ROOT
st.set_page_config(page_title='US_Flights · Puntualidad Aérea',page_icon='✈',layout='wide')
source=(ROOT/'referencias/dashboard_US_Flights_sidebar.html').read_text(encoding='utf-8')
original_css=re.search(r'<style>(.*?)</style>',source,re.S).group(1)
st.markdown('<style>@import url("https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap");'+original_css+'''
.stApp,[data-testid="stAppViewContainer"] {background:#070d18;color:#e8eef8;font-family:Manrope,system-ui,sans-serif;}
[data-testid="stHeader"] {background:#070d18;}
.block-container {max-width:1800px;padding:2rem 2rem 3rem;}
[data-testid="stSidebar"] {background:#0a101c;border-right:1px solid rgba(148,163,184,.16);min-width:290px;width:290px;}
[data-testid="stSidebar"] [data-testid="stSelectbox"] {background:#10192b;border:1px solid rgba(148,163,184,.14);border-radius:12px;padding:8px 12px;}
[data-testid="stSidebar"] [data-testid="stSelectbox"]:hover {border-color:rgba(46,230,166,.35);}
[data-testid="stSidebar"] [data-testid="stSelectbox"] label p {font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#8b97ab;}
[data-testid="stSidebar"] [data-baseweb="select"] > div {background:transparent;border:0;font-weight:700;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:7px 10px;border-radius:10px;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {background:#162033;}
[data-testid="stSidebar"] button {background:#121c30;border:1px solid rgba(148,163,184,.16);border-radius:10px;color:#d5deea;}
[data-testid="stDownloadButton"] button {border-color:#2ec4b6;color:#2ec4b6;}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:rgba(148,163,184,.16);border-radius:16px;}
h1,h2,h3 {font-family:Manrope,system-ui,sans-serif;color:#f4f7fb;}
h3 {font-size:1.05rem !important;}
.kpis {grid-template-columns:repeat(6,minmax(0,1fr));}
.kpi .v {font-size:clamp(24px,2.1vw,34px);}.kpi .badge {font-size:10px;color:#c5d0dc;background:rgba(255,255,255,.06);}
@media(max-width:1250px){.kpis{grid-template-columns:repeat(3,minmax(0,1fr));}}
@media(max-width:650px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr));}.block-container{padding:1rem;}}
</style>''',unsafe_allow_html=True)

def escape(x):return html.escape(str(x))
def reset():
    for key in ['year','month','airline','haul','state']:st.session_state[key]='all'
    st.session_state['threshold']=15;st.session_state['quality']=True

def draw(fig,height=340):
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='Manrope, sans-serif',color='#b7c3d4',size=11),margin=dict(t=20,r=15,b=45,l=45),height=height,legend=dict(orientation='h',y=-.25),colorway=['#2ec4b6','#5b8def','#f5b942','#f07178'])
    fig.update_xaxes(gridcolor='rgba(148,163,184,.12)');fig.update_yaxes(gridcolor='rgba(148,163,184,.12)')
    st.plotly_chart(fig,width='stretch')

def interpretation(text):st.markdown('<div class="interp">'+escape(text)+'</div>',unsafe_allow_html=True)
def panel(title,note,fig,text):
    with st.container(border=True):
        st.subheader(title);st.caption(note);draw(fig);interpretation(text)

st.sidebar.markdown('<div class="brand"><strong>US_Flights</strong><span>Puntualidad Aérea</span></div>',unsafe_allow_html=True)
page=st.sidebar.radio('Navegación',['Panorama','Estacionalidad','Geografía','Aerolíneas','Metodología'],label_visibility='collapsed',key='page')
with st.sidebar.expander('Cargar JSON'):
    upload=st.file_uploader('Dataset de vuelos',type=['json'],key='upload')
try:
    raw,a,p=load(json.loads(upload.getvalue().decode('utf-8-sig')) if upload else None)
except (ValueError,KeyError,TypeError,UnicodeError) as exc:
    st.error(f'No se pudo cargar el dataset: {exc}');st.info('Carga un JSON con una lista cube y el mismo esquema del archivo original.');st.stop()
# Keep uploaded options consistent with prior selections
for key,col in [('year','Year'),('month','Month'),('airline','Airline'),('haul','Haul'),('state','OriginState')]:
    if st.session_state.get(key,'all') not in ['all']+a[col].dropna().tolist():st.session_state[key]='all'
def group(name):st.sidebar.markdown('<div class="group-label">'+name+'</div>',unsafe_allow_html=True)
def select(label,key,col,all_label,format_value=str,reverse=False):
    opts=sorted(a[col].dropna().unique().tolist(),reverse=reverse)
    return st.sidebar.selectbox(label,['all']+opts,key=key,format_func=lambda v:all_label if v=='all' else format_value(v))
st.sidebar.markdown('<div class="filters-title">Filtros</div>',unsafe_allow_html=True)
group('Temporal')
year=select('Año','year','Year','Todos los años',lambda x:f'Año {int(x)}',True)
months=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
month=select('Mes','month','Month','Todos los meses',lambda x:f'{months[int(x)-1]} (Mes {int(x)})')
group('Operativo')
block=re.search(r'const CARRIER_NAMES\s*=\s*\{(.*?)\};',source,re.S)
names=dict(re.findall(r'["\']?(\w+)["\']?\s*:\s*["\']([^"\']+)["\']',block.group(1))) if block else {}
airline=select('Aerolínea','airline','Airline','Todas las aerolíneas',lambda x:f'{x} — {names[x]}' if x in names else x)
haul=select('Radio de vuelo','haul','Haul','Todos los radios',lambda x:{'corto':'Corto (< 500 mi)','medio':'Medio (500–1.500 mi)','largo':'Largo (> 1.500 mi)'}.get(x,x))
group('Geográfico y criterio')
state=select('Estado de origen','state','OriginState','Todos los orígenes',lambda x:'US — EE.UU. (Nacional)' if x=='US' else x)
threshold=st.sidebar.selectbox('Criterio de atraso',[15,60],key='threshold',format_func=lambda x:'DOT Estándar: ≥ 15 min' if x==15 else 'Atraso Severo: ≥ 60 min')
if 'quality' not in st.session_state:st.session_state['quality']=True
quality=st.sidebar.checkbox('Solo registros validados',key='quality')
st.sidebar.button('Limpiar filtros',on_click=reset,width='stretch')
st.sidebar.caption('Pantalla completa: pulsa F11 en tu navegador. Los filtros se aplican automáticamente.')
pool=a.copy()
for col,value in [('Year',year),('Month',month),('Airline',airline),('Haul',haul),('OriginState',state)]:
    if value!='all':pool=pool[pool[col]==value]
d=pool[pool.valid].copy() if quality else pool.copy()
st.sidebar.download_button('Exportar CSV',d.to_csv(index=False).encode('utf-8-sig'),'vuelos_filtrados.csv','text/csv',width='stretch')
st.markdown('<div class="top"><div><h1>US_Flights · Puntualidad Aérea de EE.UU.</h1><p class="lede">Plataforma interactiva de inteligencia operacional. Filtros conectados, análisis temporal, geoespacial y de aerolíneas.</p></div><span class="status-badge">● '+('JSON cargado' if upload else 'Datos disponibles')+'</span></div>',unsafe_allow_html=True)
chips=[f'{col}: {v}' for col,v in [('Año',year),('Mes',month),('Aerolínea',airline),('Radio',haul),('Origen',state)] if v!='all']+[f'Atraso ≥ {threshold} min','Datos validados' if quality else 'Diagnóstico bruto']
st.markdown('<div class="chips">'+''.join('<span class="pill">'+escape(v)+'</span>' for v in chips)+'</div>',unsafe_allow_html=True)
if page=='Geografía':
    st.info('Hubs es un resumen independiente sin fecha, aerolínea ni alcance. Los filtros del cubo no modifican el mapa; usa su selector de aeropuertos.')
    try:h=geo(p)
    except (KeyError,TypeError,ValueError):st.warning('El JSON no contiene un bloque hubs utilizable.');st.stop()
    mapped=h.dropna(subset=['lat','lon']);missing=h[h.lat.isna()]
    selected=st.multiselect('Aeropuertos',sorted(mapped.code),default=sorted(mapped.code));m=mapped[mapped.code.isin(selected)]
    if m.empty:st.info('Selecciona al menos un aeropuerto.');st.stop()
    with st.container(border=True):
        st.subheader('Mapa de hubs · Puntualidad y volumen');st.caption(f'{len(mapped)} de {len(h)} hubs con coordenadas. Sin ubicación: {", ".join(missing.code)}. Área proporcional a vuelos; escala de color fija 65–90%.')
        f=px.scatter_geo(m,lat='lat',lon='lon',color='otp',size='flights',hover_name='code',hover_data=['cancel'],range_color=[65,90],color_continuous_scale='Viridis',projection='mercator',size_max=42,labels={'otp':'Puntualidad (%)','flights':'Vuelos'})
        f.update_geos(showland=True,landcolor='#162033',showocean=True,oceancolor='#070d18',showcountries=True,countrycolor='#52617a',lataxis_range=[15,55],lonaxis_range=[-165,-60]);draw(f,540)
        interpretation('El período de estos indicadores no está declarado. No se infieren diferencias estatales del código nacional US.')
    st.dataframe(h,hide_index=True)
    st.caption('El fondo geográfico de Plotly requiere conexión; las coordenadas proceden del HTML adjunto.')
elif page=='Metodología':
    st.subheader('Marco analítico y calidad')
    st.markdown('**Puntualidad:** Σontime / Σops. **Atraso:** Σdelayed15 o Σdelayed60 / Σops, según el criterio elegido. **Cancelación:** Σcancel / Σops. **Atraso medio:** ΣsumDelayMin / Σdelayed15, siempre con denominador ≥15. Las causas también mantienen su universo original, al no existir minutos desglosados por el umbral ≥60.')
    st.markdown('**Radio de vuelo:** se muestran las etiquetas del HTML (<500, 500–1.500 y >1.500 millas). El JSON ya trae la categoría; no contiene distancias individuales para comprobarla.')
    st.markdown('**Incertidumbre:** intervalos Wilson 95% bajo un modelo binomial independiente. No incorporan sesgo de selección, errores del origen ni dependencia entre vuelos. Si el archivo es censal, las tasas son descriptivas y los intervalos representan un proceso hipotético.')
    st.markdown('**Calidad:** se comprueban conteos, balances, fechas, claves y minutos. El modo bruto es diagnóstico. No se usan datos simulados del HTML. Los resúmenes de hubs no se vinculan artificialmente al cubo.')
    st.write(f'{len(a):,} filas originales · {int(a.valid.sum()):,} válidas · {int((~a.valid).sum()):,} con incidencias.')
    st.dataframe(a.loc[~a.valid,['source_row','Year','Month','Airline','issues']],hide_index=True)
else:
    if d.empty:st.warning('No hay registros válidos para esta combinación. Cambia la selección o limpia los filtros.');st.stop()
    if not quality:st.warning('Modo diagnóstico: contiene inconsistencias. No usar sus cifras para conclusiones operacionales.')
    sums=d.select_dtypes('number').sum();n=sums.ops;otp=100*sums.ontime/n;delay=100*sums[f'delayed{threshold}']/n
    causes=d[CAUSES].sum();total=causes.sum();idx=int(causes.to_numpy().argmax());dominant=100*causes.iloc[idx]/total if total else 0
    avg=sums.sumDelayMin/sums.delayed15 if sums.delayed15 else None
    st.markdown(f'<div class="live"><strong>{int(n):,} operaciones</strong> · {len(d):,} registros · {int((~pool.valid).sum()):,} filas con incidencias en el filtro original. Las cuatro vistas comparten la selección.</div>',unsafe_allow_html=True)
    items=[('Llegadas a tiempo',f'{otp:.1f}%','Puntuales / operaciones','t0',otp,'◷'),(f'Atraso ≥ {threshold} min',f'{delay:.1f}%','Demoras / operaciones','t1',delay,'!'),('Atraso grave ≥ 60',f'{100*sums.delayed60/n:.1f}%','Subconjunto de atraso ≥15','t4',100*sums.delayed60/n,'△'),('Atraso medio | late',f'{avg:.0f} min' if avg is not None else 'Sin casos','Solo llegadas ≥15 min','t3',0,'◴'),('Cancelación',f'{100*sums.cancel/n:.2f}%','Canceladas / operaciones','t4',100*sums.cancel/n,'⊘'),('Causa dominante',f'{dominant:.1f}%',LABELS[idx] if total else 'Sin minutos registrados','t5',dominant,'◔')]
    cards=[]
    for label,value,sub,cls,meter,icon in items:
        bar='' if label.startswith('Atraso medio') else f'<div class="meter"><span style="width:{min(100,max(0,meter)):.2f}%"></span></div>'
        cards.append(f'<div class="kpi {cls}"><div class="kpi-h"><span class="ico">{icon}</span><span class="badge">{escape(sub)}</span></div><div class="k">{escape(label)}</div><div class="v">{escape(value)}</div>{bar}</div>')
    st.markdown('<div class="kpis">'+''.join(cards)+'</div>',unsafe_allow_html=True)
    st.caption('El criterio de atraso cambia el KPI y la serie de demoras. Puntualidad, causas y demora media mantienen sus definiciones. La fuente primaria y representatividad no están verificadas.')
    t=aggregate(d,'date').set_index('date').reindex(pd.date_range(d.date.min(),d.date.max(),freq='MS')).rename_axis('date').reset_index();t['atraso']=100*t[f'delayed{threshold}']/t.ops
    b=aggregate(d,'Airline').sort_values('otp');b['plus']=b.hi-b.otp;b['minus']=b.otp-b.lo
    h=aggregate(d,'Haul');cf=pd.DataFrame({'Causa':LABELS,'Porcentaje':causes.to_numpy()/total*100 if total else [0]*5})
    trend=go.Figure([go.Scatter(x=t.date,y=t.otp,name='Puntualidad',mode='lines+markers',line_color='#2ec4b6',connectgaps=False),go.Scatter(x=t.date,y=t.atraso,name=f'Atraso ≥{threshold}',mode='lines+markers',line_color='#5b8def',connectgaps=False)]);trend.update_yaxes(title='Operaciones (%)',range=[0,100])
    ranks=px.scatter(b,x='otp',y='Airline',error_x='plus',error_x_minus='minus',hover_data=['ops'],labels={'otp':'Puntualidad (%)','Airline':'Aerolínea'},color_discrete_sequence=['#2ec4b6'])
    reach=px.bar(h,x='Haul',y='otp',range_y=[0,100],hover_data=['ops'],labels={'Haul':'Radio de vuelo','otp':'Puntualidad (%)'},color_discrete_sequence=['#2ec4b6'])
    reasons=px.bar(cf,x='Porcentaje',y='Causa',orientation='h',color_discrete_sequence=['#5b8def'])
    low=t.loc[t.otp.idxmin()]
    if page=='Panorama':
        left,right=st.columns([1.4,1])
        with left:panel('Evolución temporal','Serie mensual · Fechas reales y huecos sin interpolación',trend,f'El mínimo seleccionado es {low.otp:.2f}% en {low.date:%Y-%m}. La composición del tráfico puede cambiar.')
        with right:panel('Puntualidad por radio','Porcentajes ponderados por operaciones',reach,f'Brecha entre categorías: {h.otp.max()-h.otp.min():.2f} puntos porcentuales; asociación descriptiva.')
        left,right=st.columns([1.4,1])
        with left:panel('Aerolíneas e incertidumbre','Tasa puntual e intervalo Wilson 95%',ranks,'Los intervalos son condicionales al modelo binomial. Revisa el volumen antes de comparar aerolíneas.')
        with right:panel('Causas de demora','Participación en minutos atribuidos',reasons,f'{LABELS[idx]} representa {dominant:.2f}% de los minutos seleccionados. No demuestra causalidad.')
    elif page=='Estacionalidad':
        panel('Evolución mensual y atraso','Misma selección que los indicadores · Umbral configurable',trend,f'Mínimo de puntualidad: {low.date:%Y-%m}, {low.otp:.2f}%. No comparar años parciales con años completos.')
        st.caption('La serie muestra variación mensual; por sí sola no demuestra estacionalidad. En el archivo original, 2026 llega a mayo y febrero–junio de 2023 queda sin registros validados.')
        st.dataframe(t[['date','ops','otp','atraso','cancel_pct']],hide_index=True)
    elif page=='Aerolíneas':
        left,right=st.columns([1.4,1])
        with left:panel('Comparación de aerolíneas','Wilson 95% · Volumen disponible al pasar el cursor',ranks,f'{b.iloc[-1].Airline} tiene {b.iloc[-1].otp:.2f}% con {int(b.iloc[-1].ops):,} operaciones. No es un ranking ajustado por rutas.')
        with right:panel('Causas en la selección','Minutos atribuidos por categoría',reasons,f'{LABELS[idx]} concentra {dominant:.2f}% del total.')
        st.dataframe(b[['Airline','ops','otp','lo','hi','cancel_pct']],hide_index=True)
    with st.expander('Datos de la selección'):
        st.dataframe(d,hide_index=True)
st.markdown('<footer>US_Flights · Hito 2 · Análisis descriptivo de los archivos proporcionados</footer>',unsafe_allow_html=True)
