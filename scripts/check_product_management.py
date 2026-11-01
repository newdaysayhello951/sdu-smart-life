"""Integration check; creates an account and one withdrawn test product."""
from check_auth import BASE,client, call
import json, uuid
a,b=client(),client()
assert call(a,'/api/my/products')[0]==401
token=json.loads(call(a,'/api/auth/csrf')[1])['token']
user={'username':'owner_'+uuid.uuid4().hex[:12],'password':uuid.uuid4().hex}
assert call(a,'/api/auth/register',user,token)[0]==201
assert call(a,'/api/auth/login',user,token)[0]==200
item={'title':'管理回归商品','description':'回归检查','price':'12.50','location':'校园'}
assert call(a,'/api/my/products',{**item,'price':'-1'},token)[0]==400
assert call(a,'/api/my/products',item,token)[0]==201
mine=json.loads(call(a,'/api/my/products')[1]);assert len(mine)==1
key=mine[0]['id']
assert call(b,'/api/my/products/'+str(key)+'/withdraw',{},token)[0] in (401,403)
other=client();ot=json.loads(call(other,'/api/auth/csrf')[1])['token']
second={'username':'other_'+uuid.uuid4().hex[:12],'password':uuid.uuid4().hex}
assert call(other,'/api/auth/register',second,ot)[0]==201
assert call(other,'/api/auth/login',second,ot)[0]==200
assert call(other,'/api/my/products/'+str(key)+'/withdraw',{},ot)[0]==404
assert call(a,'/api/my/products/'+str(key)+'/withdraw',{},token)[0]==204
assert json.loads(call(a,'/api/my/products')[1])[0]['status']=='WITHDRAWN'
print('PASS: publish, invalid price, own list, anonymous and cross-user denial, withdraw')
