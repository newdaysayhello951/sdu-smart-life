"""Creates test accounts and a withdrawn product to verify edit/upload authorization."""
from check_auth import client,call
import json,uuid,urllib.request,urllib.error
from pathlib import Path
a,b=client(),client()
def login(c):
 token=json.loads(call(c,'/api/auth/csrf')[1])['token'];u={'username':'img_'+uuid.uuid4().hex[:12],'password':uuid.uuid4().hex};assert call(c,'/api/auth/register',u,token)[0]==201;assert call(c,'/api/auth/login',u,token)[0]==200;return token
at,bt=login(a),login(b)
item={'title':'图片回归','description':'测试','price':'20.00','location':'校园'}
assert call(a,'/api/my/products',item,at)[0]==201
key=json.loads(call(a,'/api/my/products')[1])[0]['id']
def edit(c,token):
 req=urllib.request.Request('http://127.0.0.1:5173/api/my/products/'+str(key),data=json.dumps({**item,'title':'修改后的商品'}).encode(),headers={'Content-Type':'application/json','X-XSRF-TOKEN':token},method='PUT')
 try:return c.open(req).status
 except urllib.error.HTTPError as e:return e.code
assert edit(b,bt)==404
assert edit(a,at)==204
assert json.loads(call(a,'/api/products/'+str(key))[1])['title']=='修改后的商品'
def upload(c,token,body):
 boundary=uuid.uuid4().hex
 data=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="photo.jpg"\r\nContent-Type: image/jpeg\r\n\r\n').encode()+body+f'\r\n--{boundary}--\r\n'.encode()
 req=urllib.request.Request('http://127.0.0.1:5173/api/my/products/'+str(key)+'/image',data=data,headers={'Content-Type':'multipart/form-data; boundary='+boundary,'X-XSRF-TOKEN':token})
 try:
  with c.open(req) as r:return r.status,r.read()
 except urllib.error.HTTPError as e:return e.code,e.read()
photo=(Path(__file__).resolve().parents[1]/'frontend/public/assets/legacy/images/sdu.jpg').read_bytes()
assert upload(b,bt,photo)[0]==404
assert upload(a,at,b'not an image')[0]==400
status,body=upload(a,at,photo);assert status==200
url=json.loads(body)['imageUrl'];assert call(b,url)[0]==200
assert json.loads(call(a,'/api/products/'+str(key))[1])['imageUrl']==url
assert call(a,'/api/my/products/'+str(key)+'/withdraw',{},at)[0]==204
assert upload(a,at,photo)[0]==404
print('PASS: edit, cross-user denial, invalid image, upload/read, persistence, withdrawn rejection')
