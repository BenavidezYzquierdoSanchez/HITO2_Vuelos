"""Ejecuta todas las celdas; --sin-kernel permite entornos sin sockets locales."""
from pathlib import Path
import sys,subprocess,os,base64
import nbformat
ROOT=Path(__file__).resolve().parent
path=ROOT/'HITO2_Analisis.ipynb';nb=nbformat.read(path,as_version=4)
if '--sin-kernel' in sys.argv:
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    shell=InteractiveShell.instance();os.chdir(ROOT);count=0
    for cell in nb.cells:
        if cell.cell_type!='code':continue
        count+=1
        with capture_output() as cap:
            result=shell.run_cell(cell.source,store_history=True)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError(f'Error en celda {count}: {result.error_before_exec or result.error_in_exec}')
        outputs=[]
        if cap.stdout:outputs.append(nbformat.v4.new_output('stream',name='stdout',text=cap.stdout))
        if cap.stderr:outputs.append(nbformat.v4.new_output('stream',name='stderr',text=cap.stderr))
        for output in cap.outputs:
            data={key:base64.b64encode(value).decode('ascii') if isinstance(value,bytes) else value for key,value in output.data.items()}
            outputs.append(nbformat.v4.new_output('display_data',data=data,metadata=output.metadata))
        cell.outputs=outputs;cell.execution_count=count
    nb.metadata['execution_method']='IPython en proceso, celdas ejecutadas en orden, sin sockets'
else:
    from nbclient import NotebookClient
    subprocess.run([sys.executable,'-m','ipykernel','install','--user','--name','hito2-vuelos','--display-name','Hito 2 Vuelos'],check=True)
    NotebookClient(nb,timeout=180,kernel_name='hito2-vuelos',resources={'metadata':{'path':str(ROOT)}}).execute()
    nb.metadata['execution_method']='nbclient con kernel IPython'
nb.metadata.kernelspec={'display_name':'Python 3','language':'python','name':'python3'}
nbformat.write(nb,path);print('Notebook ejecutado sin errores:',path)
