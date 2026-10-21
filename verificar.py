from pathlib import Path
import json,sys
import numpy as np
from src.analysis import load,metrics,geo
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parent
raw,a,p=load();d=a[a.valid]
assert len(a)==3344 and len(d)==3202
assert np.isclose(metrics(d)['Puntualidad'],78.08474544990618)
assert geo(p).lat.notna().sum()==31
assert load(p)[1].valid.sum()==3202
try:load({'cube':[]});raise AssertionError('No rechazó cube vacío')
except ValueError:pass
at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run();assert not at.exception
assert len(at.get('plotly_chart'))==4
assert len(at.selectbox)==6
at.selectbox(key='year').set_value(2024);at.selectbox(key='airline').set_value('AA');at.run();assert not at.exception
assert any('operaciones' in m.value and f'{int(d[(d.Year==2024)&(d.Airline=="AA")].ops.sum()):,}' in m.value for m in at.markdown)
at.selectbox(key='threshold').set_value(60);at.run();assert not at.exception
assert any('Atraso ≥ 60 min' in m.value for m in at.markdown)
at.selectbox(key='year').set_value(2023);at.selectbox(key='month').set_value(4);at.run();assert not at.exception and len(at.get('plotly_chart'))==0
next(b for b in at.button if b.label=='Limpiar filtros').click().run();assert not at.exception
assert at.selectbox(key='year').value=='all' and at.selectbox(key='threshold').value==15
for page,count in [('Estacionalidad',1),('Aerolíneas',2),('Metodología',0),('Geografía',1)]:
    at.radio(key='page').set_value(page).run();assert not at.exception;assert len(at.get('plotly_chart'))==count
at.multiselect[0].set_value(['ATL']).run();assert not at.exception
at.multiselect[0].set_value([]).run();assert not at.exception and len(at.get('plotly_chart'))==0
r={'estado':'correcto','python':sys.version.split()[0],'controles':['KPI de referencia','31 hubs','carga del mismo payload','rechazo de cube vacío','cuatro vistas conectadas','seis filtros','año y aerolínea','umbral ≥60','selección vacía','restablecimiento','cinco secciones','mapa ATL y vacío'],'alcance':'AppTest verifica lógica y elementos; no valida CSS visual en navegador ni despliegue público.'}
(ROOT/'resultados/verificacion.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
