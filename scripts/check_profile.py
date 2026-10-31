from check_auth import client,call
import uuid,json,urllib.request
c=client();t=json.loads(call(c,'/api/auth/csrf')[1])['token'];u={'username':'profile_'+uuid.uuid4().hex[:10],'password':uuid.uuid4().hex}
assert call(c,'/api/auth/register',u,t)[0]==201
assert call(c,'/api/auth/login',u,t)[0]==200
value={'displayName':'山大学生','signature':'校园生活','location':'图书馆'}
req=urllib.request.Request('http://127.0.0.1:5173/api/profile',data=json.dumps(value).encode(),headers={'Content-Type':'application/json','X-XSRF-TOKEN':t},method='PUT')
assert c.open(req).status==200
profile=json.loads(call(c,'/api/profile')[1]);assert all(profile[k]==v for k,v in value.items())
assert call(client(),'/api/profile')[0]==401
print('PASS: profile persistence and anonymous denial')
