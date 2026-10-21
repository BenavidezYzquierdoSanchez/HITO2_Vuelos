"""Carga, auditoría y visualizaciones compartidas. No se imputan cifras."""
from pathlib import Path
import json,re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
CAUSES=['carrierDelay','weatherDelay','nasDelay','secDelay','lateAirDelay']
LABELS=['Aerolínea','Clima','Sistema aéreo','Seguridad','Avión previo']
COUNTS=['ops','ontime','delayed15','delayed60','cancel','divert']
NUM=COUNTS+['sumDelayMin']+CAUSES
KEYS=['Year','Month','Airline','OriginState','Haul']
BLUE='#2463A0'; TEAL='#008779'; ORANGE='#C46B17'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#243448','figure.facecolor':'white','axes.facecolor':'white'})

def load(payload=None):
    if payload is None: payload=json.loads((ROOT/'data/data_vuelos_dashboard_final.json').read_text(encoding='utf-8'))
    if not isinstance(payload,dict) or not isinstance(payload.get('cube'),list) or not payload['cube']:
        raise ValueError('cube debe ser una lista no vacía')
    raw=pd.DataFrame(payload['cube'])
    if not set(KEYS+NUM)<=set(raw): raise ValueError('Faltan columnas requeridas')
    d=raw.copy(); d['source_row']=np.arange(len(d))+1
    for c in NUM+['Year','Month']: d[c]=pd.to_numeric(d[c],errors='coerce')
    d['date']=pd.to_datetime(dict(year=d.Year,month=d.Month,day=1),errors='coerce')
    rules={
        'nulos_o_no_finitos':~np.isfinite(d[NUM]).all(axis=1)|d[KEYS].isna().any(axis=1),
        'negativos_o_cero_ops':(d[NUM]<0).any(axis=1)|(d.ops<=0),
        'conteos_no_enteros':(d[COUNTS]%1!=0).any(axis=1),
        'balance_estados':~np.isclose(d.ops,d[['ontime','delayed15','cancel','divert']].sum(axis=1),rtol=0,atol=0.01),
        'subconjunto_60':d.delayed60>d.delayed15,
        'balance_causas':~np.isclose(d[CAUSES].sum(axis=1),d.sumDelayMin,rtol=0,atol=0.01),
        'fecha_invalida':d.date.isna(),
        'clave_duplicada':d.duplicated(KEYS,keep=False)}
    checks=pd.DataFrame(rules)
    d['issues']=checks.apply(lambda r:'; '.join(r.index[r]),axis=1)
    d['valid']=~checks.any(axis=1)
    return raw,d,payload

def aggregate(d,by):
    a=d.groupby(by,as_index=False,observed=True)[NUM].sum()
    a['otp']=100*a.ontime/a.ops
    a['cancel_pct']=100*a.cancel/a.ops
    a['delay_pct']=100*a.delayed15/a.ops
    a['avg_delay']=a.sumDelayMin/a.delayed15.replace(0,np.nan)
    lo,hi=wilson(a.ontime,a.ops);a['lo']=lo;a['hi']=hi
    return a

def wilson(k,n,z=1.959963984540054):
    p=k/n; den=1+z*z/n
    mid=(p+z*z/(2*n))/den
    half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return 100*(mid-half),100*(mid+half)

def metrics(d):
    s=d[NUM].sum(); n=s.ops
    return {'Operaciones':int(n),'Puntualidad':100*s.ontime/n if n else np.nan,
            'Cancelación':100*s.cancel/n if n else np.nan,
            'Demora media en retrasados':s.sumDelayMin/s.delayed15 if s.delayed15 else np.nan}

def geo(payload):
    text=(ROOT/'referencias/dashboard_US_Flights_sidebar.html').read_text(encoding='utf-8')
    block=re.search(r'const AIRPORT_COORDS = \{(.*?)\};',text,re.S).group(1)
    coords={k:(float(a),float(b)) for k,a,b in re.findall(r'(\w+):\[([\d.-]+),\s*([\d.-]+)\]',block)}
    h=pd.DataFrame(payload['hubs']);h['lat']=h.code.map(lambda c:coords.get(c,(np.nan,np.nan))[0]);h['lon']=h.code.map(lambda c:coords.get(c,(np.nan,np.nan))[1])
    h['coordinate_source']='AIRPORT_COORDS del HTML adjunto'
    return h

def figure(kind,d,raw,payload):
    fig,ax=plt.subplots(figsize=(9,4.5),layout='constrained')
    if kind==1:
        a=aggregate(d,'date').set_index('date').reindex(pd.date_range(d.date.min(),d.date.max(),freq='MS'))
        ax.plot(a.index,a.otp,color=BLUE,marker='.',label='Puntualidad');ax.set(ylabel='Puntualidad (%)',title='01 Evolución mensual del subconjunto validado',ylim=(0,100)); ax.grid(alpha=.2)
    elif kind==2:
        s=d[d.Month==4]; sets=s.groupby('Year').apply(lambda g:set(zip(g.Airline,g.Haul)),include_groups=False)
        common=set.intersection(*sets.tolist());s=s[[x in common for x in zip(s.Airline,s.Haul)]]
        a=aggregate(s,'Year');ax.bar(a.Year.astype(str),a.otp,color=BLUE);ax.set(ylabel='Puntualidad (%)',ylim=(0,100),title=f'02 Abril válido en cinco años · {len(common)} segmentos comunes')
    elif kind==3:
        a=aggregate(d,'Airline').sort_values('otp');ax.errorbar(a.otp,a.Airline,xerr=[a.otp-a.lo,a.hi-a.otp],fmt='o',color=BLUE,capsize=3);ax.set(xlabel='Puntualidad (%) e intervalo Wilson 95%',title='03 Precisión condicional por aerolínea');ax.grid(axis='x',alpha=.2)
    elif kind==4:
        a=aggregate(d,'Haul');ax.bar(a.Haul,a.otp,color=TEAL);ax.set(ylabel='Puntualidad (%)',ylim=(0,100),title='04 Puntualidad por alcance del vuelo')
    elif kind==5:
        s=d[NUM].sum(); vals=[s.ontime,s.delayed15-s.delayed60,s.delayed60,s.cancel,s.divert]; names=['Puntual','Demora 15–59','Demora ≥60','Cancelado','Desviado'];ax.barh(names,np.array(vals)/s.ops*100,color=[TEAL,BLUE,ORANGE,'#9A4771','#777777']);ax.set(xlabel='% de operaciones',title='05 Resultados mutuamente excluyentes')
    elif kind==6:
        s=d[CAUSES].sum();ax.barh(LABELS,s/s.sum()*100,color=BLUE);ax.set(xlabel='% de minutos atribuidos',title='06 Composición de las causas registradas')
    elif kind==7:
        a=aggregate(d,'Airline');ax.scatter(a.ops,a.otp,c=a.cancel_pct,cmap='viridis',s=75)
        for _,r in a.iterrows():ax.annotate(r.Airline,(r.ops,r.otp),fontsize=8,xytext=(3,3),textcoords='offset points')
        fig.colorbar(ax.collections[0],ax=ax,label='Cancelación (%)');ax.set(xlabel='Operaciones',ylabel='Puntualidad (%)',title='07 Volumen y desempeño por aerolínea')
    elif kind==8:
        h=geo(payload).dropna(subset=['lat','lon']);sc=ax.scatter(h.lon,h.lat,s=h.flights/5000,c=h.otp,vmin=65,vmax=90,cmap='viridis',alpha=.8,edgecolors='white')
        for _,r in h[h.code.isin(['HNL','SEA','SFO','LAX','PHX','DEN','DFW','ORD','ATL','MIA','BOS'])].iterrows():ax.annotate(r.code,(r.lon,r.lat),fontsize=7,xytext=(3,4),textcoords='offset points')
        ax.set(xlim=(-165,-65),ylim=(17,51),xlabel='Longitud (grados)',ylabel='Latitud (grados)',title=f'08 Localización de hubs con coordenadas ({len(h)}/{len(payload["hubs"])})')
        ax.set_aspect(1/np.cos(np.deg2rad(35)));ax.grid(alpha=.25);fig.colorbar(sc,ax=ax,label='Puntualidad declarada (%)',shrink=.8)
    elif kind==9:
        a=raw.groupby(['Year','Month']).size().unstack().reindex(columns=range(1,13));im=ax.imshow(a,aspect='auto',cmap='Blues');ax.set(xticks=range(12),xticklabels=range(1,13),yticks=range(len(a)),yticklabels=a.index,xlabel='Mes',ylabel='Año',title='09 Cobertura de registros del archivo original')
        for i in range(len(a)):
            for j in range(12):ax.text(j,i,'—' if pd.isna(a.iloc[i,j]) else str(int(a.iloc[i,j])),ha='center',va='center',fontsize=8,color='white' if pd.notna(a.iloc[i,j]) and a.iloc[i,j]>40 else 'black')
        fig.colorbar(im,ax=ax,label='Filas agregadas')
    elif kind==10:
        h=pd.DataFrame(payload['hourly']).sort_values('hour_block');ax.plot(h.hour_block,h.avg_delay,marker='o',color=ORANGE);ax.set(xlabel='Bloque horario declarado',ylabel='Demora media declarada (min)',title='10 Perfil horario auxiliar sin denominadores');ax.grid(alpha=.2)
    return fig

def export():
    raw,a,p=load(); d=a[a.valid].copy();out=ROOT/'resultados';out.mkdir(exist_ok=True)
    a.to_csv(out/'auditoria_filas.csv',index=False);d.to_csv(out/'datos_validados.csv',index=False)
    aggregate(d,'date').to_csv(out/'indicadores_mensuales.csv',index=False);aggregate(d,'Airline').to_csv(out/'indicadores_aerolineas.csv',index=False)
    geo(p).to_csv(out/'hubs_coordenadas.csv',index=False)
    for i in range(1,11):
        f=figure(i,d,raw,p);f.savefig(out/f'figura_{i:02}.png',dpi=160);plt.close(f)
    summary={'filas_originales':len(a),'filas_validas':int(a.valid.sum()),'filas_excluidas':int((~a.valid).sum()),'ops_originales':int(a.ops.sum()),'ops_validas':int(d.ops.sum()),'kpis':metrics(d),'por_anio':a.groupby('Year').agg(filas=('valid','size'),validas=('valid','sum'),ops=('ops','sum')).reset_index().to_dict('records')}
    (out/'resumen.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8');return summary
if __name__=='__main__': print(json.dumps(export(),ensure_ascii=False,indent=2))
