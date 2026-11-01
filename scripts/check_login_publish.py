from check_auth import BASE,client,call
import json,uuid,urllib.request,urllib.error
from pathlib import Path
c=client()
assert call(c,'/api/products')[0]==401
t=json.loads(call(c,'/api/auth/csrf')[1])['token'];u={'username':'pub_'+uuid.uuid4().hex[:12],'password':uuid.uuid4().hex}
assert call(c,'/api/auth/register',u,t)[0]==201
assert call(c,'/api/auth/login',u,t)[0]==200
assert json.loads(call(c,'/api/auth/me')[1])['username']==u['username']
assert call(c,'/api/products')[0]==200
item={'title':'首次带图发布','description':'回归验证','price':'12.50','location':'校园'}
def publish(photo,path='/api/my/products/publish'):
 boundary=uuid.uuid4().hex
 body=(f'--{boundary}\r\nContent-Disposition: form-data; name="product"\r\nContent-Type: application/json\r\n\r\n'+json.dumps(item)+f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="photo.jpg"\r\nContent-Type: image/jpeg\r\n\r\n').encode()+photo+f'\r\n--{boundary}--\r\n'.encode()
 req=urllib.request.Request(BASE+path,data=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary,'X-XSRF-TOKEN':t})
 try:
  with c.open(req) as r:return r.status,r.read()
 except urllib.error.HTTPError as e:return e.code,e.read()
assert publish(b'invalid')[0]==400
assert json.loads(call(c,'/api/my/products')[1])==[]
photo=(Path(__file__).resolve().parents[1]/'frontend/public/assets/legacy/images/sdu.jpg').read_bytes()
status,body=publish(photo);assert status==201
key=json.loads(body)['id'];detail=json.loads(call(c,'/api/products/'+str(key))[1]);assert detail['imageUrl'].startswith('/api/images/')
assert call(c,detail['imageUrl'])[0]==200
assert call(client(),detail['imageUrl'])[0]==401
item['title']='编辑文字与图片'
path='/api/my/products/'+str(key)+'/edit-with-image'
assert publish(b'invalid',path)[0]==400
assert json.loads(call(c,'/api/products/'+str(key))[1])['title']==detail['title']
assert publish(photo,path)[0]==204
assert json.loads(call(c,'/api/products/'+str(key))[1])['title']==item['title']
assert call(c,'/api/my/products/'+str(key)+'/withdraw',{},t)[0]==204
assert call(c,'/api/auth/logout',{},t)[0]==204
assert call(c,'/api/products')[0]==401
print('PASS: login gate, restored session, image-first publish, rollback, protected image, logout gate')
