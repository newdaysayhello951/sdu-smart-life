"""Boundary and concurrency checks against local test environment."""
from check_auth import BASE,client,call
from concurrent.futures import ThreadPoolExecutor
import json,uuid,urllib.request,urllib.error
c=client();token=json.loads(call(c,'/api/auth/csrf')[1])['token'];name='strict_'+uuid.uuid4().hex[:10]
for value in ['', 'ab', 'x'*33, "x' OR 1=1 --",'中文用户名']:
 assert call(c,'/api/auth/register',{'username':value,'password':'validpassword'},token)[0]==400
for value in ['', 'short', 'a'*65, '汉'*30]:
 assert call(c,'/api/auth/register',{'username':name,'password':value},token)[0]==400
u={'username':name,'password':uuid.uuid4().hex}
assert call(c,'/api/auth/register',u,token)[0]==201
assert call(c,'/api/auth/login',u,token)[0]==200
for path in ['/api/products?page=-1','/api/products?size=0','/api/products?page=100001','/api/products?page=abc','/api/products?keyword='+'x'*101]:
 assert call(c,path)[0]==400,path
assert json.loads(call(c,'/api/products?keyword=%27%20OR%201%3D1')[1])['total']==0
item={'title':'boundary','description':'test','price':'1.00','location':'campus'}
for patch in [{'title':''},{'title':'x'*121},{'description':'x'*5001},{'price':'-1'},{'price':'0'},{'price':'1.234'},{'location':'x'*121}]:
 assert call(c,'/api/my/products',{**item,**patch},token)[0]==400,patch
# Two clients racing for one username must produce one success and one conflict.
race='race_'+uuid.uuid4().hex[:10]
def register(_):
 a=client();t=json.loads(call(a,'/api/auth/csrf')[1])['token'];return call(a,'/api/auth/register',{'username':race,'password':'racepassword'},t)[0]
with ThreadPoolExecutor(max_workers=2) as pool:assert sorted(pool.map(register,range(2)))==[201,409]
# Duplicate rename must not damage either account.
p={'username':race,'signature':'','location':'','qq':'','dormitory':''}
req=urllib.request.Request(BASE+'/api/profile',data=json.dumps(p).encode(),headers={'Content-Type':'application/json','X-XSRF-TOKEN':token},method='PUT')
try:c.open(req);raise AssertionError('duplicate rename accepted')
except urllib.error.HTTPError as e:assert e.code==409
assert json.loads(call(c,'/api/auth/me')[1])['username']==name
print('PASS: 25 boundary/concurrency checks; invalid account/password/search/product inputs, registration race, rename conflict')
