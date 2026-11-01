"""Self-contained product regression; never depends on legacy/sample data."""
import json, urllib.request, urllib.error, urllib.parse
from check_auth import BASE,client,call
import uuid
opener=client()
token=json.loads(call(opener,'/api/auth/csrf')[1])['token']
account={'username':'browse_'+uuid.uuid4().hex[:10],'password':uuid.uuid4().hex}
assert call(opener,'/api/auth/register',account,token)[0]==201
assert call(opener,'/api/auth/login',account,token)[0]==200
assert call(opener,'/api/my/products',{'title':'browse_'+uuid.uuid4().hex[:10],'description':'市场回归','price':'1','location':'校园','kind':'SELL'},token)[0]==201

def get(path):
 try:
  with opener.open(BASE+path) as r:return r.status,r.read()
 except urllib.error.HTTPError as e:return e.code,e.read()
status,body=get('/api/products?size=2');assert status==200
page=json.loads(body);assert page['total']>0 and len(page['items'])<=2
item=page['items'][0]
assert json.loads(get('/api/products/'+str(item['id']))[1])['title']==item['title']
assert get(item['imageUrl'])[0]==200
assert get('/market/'+str(item['id']))[0]==200
assert get('/api/products/999999999')[0]==404
assert get('/api/products?page=0')[0]==400
assert get('/api/products?size=51')[0]==400
search=json.loads(get('/api/products?keyword='+urllib.parse.quote(item['title']))[1]);assert any(p['id']==item['id'] for p in search['items'])
assert json.loads(get('/api/products?keyword=__no_such_product_987654321__')[1])['total']==0
if page['total']>2:
 second=json.loads(get('/api/products?size=2&page=2')[1]);assert not ({p['id'] for p in page['items']} & {p['id'] for p in second['items']})
print('PASS: list, detail, image, route fallback, search, empty result, pagination, invalid params, missing product')
