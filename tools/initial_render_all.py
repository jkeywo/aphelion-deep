import subprocess,sys,os
from pathlib import Path
root=Path(r'C:\AnalogueGames\aphelion-deep\.staging')
renderer=r'C:\Users\jkeyw\.cache\codex-runtimes\codex-primary-runtime\plugins\openai-primary-runtime\plugins\documents\skills\documents\render_docx.py'
os.environ['PATH']=r'C:\Program Files\LibreOffice\program;'+os.environ['PATH']
for p in root.glob('*-import.docx'):
 subprocess.run([sys.executable,renderer,str(p),'--output_dir',str(root/'qa'/p.stem),'--dpi','80'],check=True)
