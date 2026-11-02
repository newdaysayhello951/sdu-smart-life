"""Install independent campus AI dependencies from public upstream releases."""
import urllib.request,json,hashlib,zipfile,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
target=ROOT/'.tools/ai';target.mkdir(exist_ok=True)
urls={'model.onnx':'https://huggingface.co/Xenova/multilingual-e5-small/resolve/main/onnx/model_quantized.onnx','tokenizer.json':'https://huggingface.co/Xenova/multilingual-e5-small/resolve/main/tokenizer.json','qdrant.zip':'https://github.com/qdrant/qdrant/releases/download/v1.15.4/qdrant-x86_64-pc-windows-msvc.zip'}
report={}
for name,url in urls.items():
 p=target/name
 if not p.exists():
  print('Downloading '+name,flush=True)
  with op.open(urllib.request.Request(url.replace('huggingface.co','hf-mirror.com') if os.getenv('HF_MIRROR')=='1' else url,headers={'User-Agent':'SmartCampus-Setup/1.0'}),timeout=90) as res,(target/(name+'.download')).open('wb') as out:
   while b:=res.read(1024*1024):out.write(b)
  (target/(name+'.download')).replace(p)
 report[name]={'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
if not (target/'qdrant.exe').exists():
 with zipfile.ZipFile(target/'qdrant.zip') as z:
  for name in z.namelist():
   if name.endswith('qdrant.exe'):(target/'qdrant.exe').write_bytes(z.read(name))
(target/'manifest.json').write_text(json.dumps(report,indent=2))
(target/'qdrant.yaml').write_text('storage:\n  storage_path: ./storage\nservice:\n  host: 127.0.0.1\n  http_port: 6333\n  grpc_port: 6334\ntelemetry_disabled: true\n')
print('Independent campus model and Qdrant ready.',flush=True)
