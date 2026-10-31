from check_auth import client,call
from concurrent.futures import ThreadPoolExecutor
import uuid,json
def account():
 c=client();t=json.loads(call(c,'/api/auth/csrf')[1])['token'];u={'username':'trade_'+uuid.uuid4().hex[:10],'password':uuid.uuid4().hex};assert call(c,'/api/auth/register',u,t)[0]==201;assert call(c,'/api/auth/login',u,t)[0]==200;return c,t
seller,st=account();a,at=account();b,bt=account();outsider,ot=account()
assert call(client(),'/api/orders')[0]==401
item={'title':'并发交易测试','description':'test','price':'25.50','location':'campus'}
assert call(seller,'/api/my/products',item,st)[0]==201
product=json.loads(call(seller,'/api/my/products')[1])[0]['id'];path='/api/orders/product/'+str(product)
assert call(seller,path,{},st)[0]==400
with ThreadPoolExecutor(max_workers=2) as pool:
 futures=[pool.submit(call,a,path,{},at),pool.submit(call,b,path,{},bt)];results=[f.result() for f in futures]
assert sorted(r[0] for r in results)==[200,409]
idx=next(i for i,r in enumerate(results) if r[0]==200);buyer,token=(a,at) if idx==0 else (b,bt)
order=json.loads(results[idx][1])['id'];orderpath='/api/orders/'+str(order)
assert json.loads(call(buyer,path,{},token)[1])['id']==order
assert json.loads(call(seller,'/api/products/'+str(product))[1])['status']=='RESERVED'
assert call(seller,'/api/my/products/'+str(product)+'/withdraw',{},st)[0]==404
assert call(outsider,orderpath+'/cancel',{},ot)[0]==404
assert call(seller,orderpath+'/complete',{},st)[0]==403
assert call(buyer,orderpath+'/cancel',{},token)[0]==200
assert json.loads(call(seller,'/api/products/'+str(product))[1])['status']=='AVAILABLE'
assert call(buyer,orderpath+'/cancel',{},token)[0]==200
assert call(buyer,orderpath+'/complete',{},token)[0]==409
order=json.loads(call(buyer,path,{},token)[1])['id'];orderpath='/api/orders/'+str(order)
assert call(buyer,orderpath+'/complete',{},token)[0]==200
assert call(buyer,orderpath+'/complete',{},token)[0]==200
assert json.loads(call(seller,'/api/products/'+str(product))[1])['status']=='SOLD'
assert call(b,path,{},bt)[0] in (400,409)
orders=json.loads(call(buyer,'/api/orders')[1]);record=next(o for o in orders if o['id']==order);assert record['status']=='COMPLETED' and float(record['price'])==25.5 and record['role']=='BUYER'
assert json.loads(call(outsider,'/api/orders')[1])==[]
assert call(buyer,'/api/orders?before=-1')[0]==400
print('PASS: own-product denial, concurrent single winner, retry idempotency, cancel/relist, owner authorization, buyer confirmation, final state and private snapshots')
