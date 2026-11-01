"""Lost/found regression; only runs on the disposable QA server."""
from check_auth import client,call
import json,uuid,urllib.request,urllib.error
owner,other=client(),client()
def login(c):
 t=json.loads(call(c,'/api/auth/csrf')[1])['token'];u={'username':'lost_'+uuid.uuid4().hex[:12],'password':uuid.uuid4().hex}
 assert call(c,'/api/auth/register',u,t)[0]==201
 assert call(c,'/api/auth/login',u,t)[0]==200
 return json.loads(call(c,'/api/auth/csrf')[1])['token']
t,ot=login(owner),login(other)
for kind in ['LOST','FOUND']:
 item={'title':'失物回归_'+uuid.uuid4().hex[:8],'description':'昨天拾取的钥匙，私聊核验','price':'0','location':'海棠测试地点','kind':kind}
 assert call(owner,'/api/my/products',item,t)[0]==201
 mine=json.loads(call(owner,'/api/my/products')[1]);p=next(x for x in mine if x['title']==item['title']);pid=p['id']
 result=json.loads(call(owner,'/api/products?kind='+kind+'&keyword='+urllib.parse.quote('海棠测试地点'))[1]);assert any(x['id']==pid for x in result['items'])
 for market in ['SELL','WANTED']:
  assert all(x['id']!=pid for x in json.loads(call(owner,'/api/products?kind='+market)[1])['items'])
 def put(c,payload,token):
  req=urllib.request.Request('http://127.0.0.1:15173/api/my/products/'+str(pid),data=json.dumps(payload).encode(),method='PUT',headers={'Content-Type':'application/json','X-XSRF-TOKEN':token})
  try:return c.open(req).status
  except urllib.error.HTTPError as e:return e.code
 assert put(other,item,ot)==404
 assert put(owner,{**item,'description':'已更新失物描述'},t)==204
 assert json.loads(call(owner,'/api/products/'+str(pid))[1])['description']=='已更新失物描述'
 assert call(other,'/api/my/products/'+str(pid)+'/withdraw',{},ot)[0]==404
 assert call(owner,'/api/my/products/'+str(pid)+'/withdraw',{},t)[0]==204
 assert all(x['id']!=pid for x in json.loads(call(owner,'/api/products?kind='+kind)[1])['items'])
 assert call(owner,'/api/my/products',{**item,'price':'1'},t)[0]==400
assert call(owner,'/api/my/products',{**item,'kind':'SELL','price':'0'},t)[0]==400
print('PASS: lost/found publish, location search, market isolation, edit, owner authorization, finish, price validation')
