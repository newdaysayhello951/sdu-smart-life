from check_auth import client,call
import uuid,json,urllib.request
c=client();t=json.loads(call(c,'/api/auth/csrf')[1])['token'];u={'username':'profile_'+uuid.uuid4().hex[:10],'password':uuid.uuid4().hex}
assert call(c,'/api/auth/register',u,t)[0]==201
assert call(c,'/api/auth/login',u,t)[0]==200
value={'username':u['username']+'_new','qq':'123456789','dormitory':'阅海居B2','signature':'校园生活','location':'图书馆'}
req=urllib.request.Request('http://127.0.0.1:5173/api/profile',data=json.dumps(value).encode(),headers={'Content-Type':'application/json','X-XSRF-TOKEN':t},method='PUT')
assert c.open(req).status==200
profile=json.loads(call(c,'/api/profile')[1]);assert all(profile[k]==v for k,v in value.items())
assert call(client(),'/api/profile')[0]==401
assert json.loads(call(c,'/api/auth/me')[1])['username']==value['username']
assert call(c,'/api/my/products')[0]==200
other=client();ot=json.loads(call(other,'/api/auth/csrf')[1])['token']
assert call(other,'/api/auth/login',u,ot)[0]==401
assert call(other,'/api/auth/login',{**u,'username':value['username']},ot)[0]==200
assert call(c,'/api/profile/avatar')[0]==200
print('PASS: profile persistence and anonymous denial')

from pathlib import Path
photo=(Path(__file__).resolve().parents[1]/'frontend/public/assets/legacy/images/sdu.jpg').read_bytes()
boundary=uuid.uuid4().hex
body=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="avatar.jpg"\r\nContent-Type: image/jpeg\r\n\r\n').encode()+photo+f'\r\n--{boundary}--\r\n'.encode()
request=urllib.request.Request('http://127.0.0.1:5173/api/profile/avatar',data=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary,'X-XSRF-TOKEN':t})
assert c.open(request).status==200
assert call(c,'/api/profile/avatar')[1].startswith(b'\x89PNG')
item={'title':'改名关联回归','description':'测试归属','price':'10','location':'校园'}
assert call(c,'/api/my/products',item,t)[0]==201
before=json.loads(call(c,'/api/my/products')[1])
renamed={**value,'username':value['username']+'x'}
request=urllib.request.Request('http://127.0.0.1:5173/api/profile',data=json.dumps(renamed).encode(),headers={'Content-Type':'application/json','X-XSRF-TOKEN':t},method='PUT')
assert c.open(request).status==200
assert json.loads(call(other,'/api/auth/me')[1])['username']==renamed['username']
after=json.loads(call(c,'/api/my/products')[1])
assert [{k:v for k,v in x.items() if k!='ownerName'} for x in after]==[{k:v for k,v in x.items() if k!='ownerName'} for x in before]
assert all(x['ownerName']==renamed['username'] for x in after)
assert call(c,'/api/my/products/'+str(before[0]['id'])+'/withdraw',{},t)[0]==204
print('PASS: avatar blob, rename across sessions and stable product ownership')
