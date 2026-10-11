"""Export reviewed slide PNGs to a matching PDF with declared video links."""
import argparse, json
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--previews',type=Path,required=True)
p.add_argument('--content',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();slides=json.loads(a.content.read_text());a.output.parent.mkdir(parents=True,exist_ok=True)
c=Canvas(str(a.output),pagesize=(960,540));c.setTitle('RflySim measured component handoff')
for i,s in enumerate(slides):
    c.drawImage(str(a.previews/f'slide-{i+1:02d}.png'),0,0,width=960,height=540)
    for j,(_,url) in enumerate(s.get('links',[])):
        c.linkURL(url,(.75*(72+j*178),.75*(720-655),.75*(72+j*178+165),.75*(720-623)),relative=0)
    c.showPage()
c.save();d=PdfReader(a.output)
assert len(d.pages)==len(slides)
assert sum(len(x.get('/Annots',[])) for x in d.pages)==sum(len(s.get('links',[])) for s in slides)
print(f'{len(d.pages)} PDF pages; declared links preserved')
