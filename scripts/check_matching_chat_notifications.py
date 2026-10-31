from check_auth import client,call
import uuid,json,urllib.request,urllib.error
from concurrent.futures import ThreadPoolExecutor
def account():
 c=client();t=json.loads(call(c,'/api/auth/csrf')[1])['token'];u={'username':'connect_'+uuid.uuid4().hex[:9],'password':uuid.uuid4().hex};assert call(c,'/api/auth/register',u,t)[0]==201;assert call(c,'/api/auth/login',u,t)[0]==200;return c,t,json.loads(call(c,'/api/people/me')[1])
a,at,ap=account();b,bt,bp=account();outside,ot,op=account()
assert call(client(),'/api/notifications')[0]==401
# Both listings use persisted owner IDs; each market page is bounded.
for kind in ['SELL','WANTED']:
 for i in range(4):assert call(a,'/api/my/products',{'title':ap['username']+kind+str(i),'description':'校园牵线测试','price':'30.00','location':'校园','kind':kind},at)[0]==201
 page=json.loads(call(b,'/api/products?kind='+kind+'&size=3&keyword='+ap['username'])[1]);assert len(page['items'])==3 and page['total']==4
 assert all(p['kind']==kind and p['ownerId']==ap['id'] for p in page['items'])
 second=json.loads(call(b,'/api/products?kind='+kind+'&size=3&page=2&keyword='+ap['username'])[1]);assert len(second['items'])==1
 assert not ({p['id'] for p in page['items']} & {p['id'] for p in second['items']})
 public=json.loads(call(b,'/api/people/'+str(ap['id'])+'/listings?kind='+kind)[1]);assert len(public)==4
person=json.loads(call(b,'/api/people/'+str(ap['id']))[1]);assert person['username']==ap['username'] and 'password' not in str(person).lower()
assert call(a,'/api/chats/with/'+str(ap['id']),{},at)[0]==400
assert call(a,'/api/chats/with/999999999',{},at)[0]==404
with ThreadPoolExecutor(max_workers=2) as pool:
 f1=pool.submit(call,a,'/api/chats/with/'+str(bp['id']),{},at);f2=pool.submit(call,b,'/api/chats/with/'+str(ap['id']),{},bt);r1,r2=f1.result(),f2.result()
assert r1[0]==r2[0]==200 and json.loads(r1[1])['id']==json.loads(r2[1])['id']
chat=json.loads(r1[1])['id'];base='/api/chats/'+str(chat)
assert call(outside,base+'/messages')[0]==404
assert call(outside,base+'/messages',{'content':'越权'},ot)[0]==404
assert call(a,base+'/messages',{'content':'   '},at)[0]==400
assert call(a,base+'/messages',{'content':'x'*2001},at)[0]==400
for i in range(101):assert call(a,base+'/messages',{'content':'hello '+str(i)+' 😊'},at)[0]==201
assert json.loads(call(b,'/api/notifications/unread')[1])['count']==101
assert json.loads(call(a,'/api/notifications/unread')[1])['count']==0
notices=json.loads(call(b,'/api/notifications')[1]);assert len(notices)==30 and all(n['unread'] for n in notices)
first_notice=notices[0]['id'];assert call(outside,'/api/notifications/'+str(first_notice)+'/read',{},ot)[0]==404
assert call(b,'/api/notifications/'+str(first_notice)+'/read',{},bt)[0]==200
assert json.loads(call(b,'/api/notifications/unread')[1])['count']==100
# A notification arriving after the visible snapshot stays unread after read-all.
assert call(a,base+'/messages',{'content':'new message'},at)[0]==201
assert call(b,'/api/notifications/read-all?through='+str(first_notice),{},bt)[0]==200
assert json.loads(call(b,'/api/notifications/unread')[1])['count']==1
messages=[];after=0
while True:
 batch=json.loads(call(b,base+'/messages?after='+str(after))[1]);messages+=batch
 if not batch:break
 after=batch[-1]['id']
 if len(batch)<50:break
assert len(messages)==102 and len({m['id'] for m in messages})==102
assert call(b,base+'/read?through='+str(messages[-1]['id']),{},bt)[0]==200
assert json.loads(call(b,'/api/notifications/unread')[1])['count']==0
assert call(outside,base+'/read?through='+str(after),{},ot)[0]==404
assert call(b,base+'/messages',{'content':'你好，线下见'},bt)[0]==201
assert json.loads(call(a,'/api/notifications/unread')[1])['count']==1
assert json.loads(call(a,base+'/messages?after='+str(messages[-1]['id']))[1])[0]['senderId']==bp['id']
assert call(a,'/api/products?kind=BAD')[0]==400
assert call(a,'/api/orders')[0]==404

# Renaming updates public listings, peers, message authors and historical notification labels.
renamed=ap['username']+'_new'
profile={'username':renamed,'signature':'test','location':'','qq':'','dormitory':''}
request=urllib.request.Request('http://127.0.0.1:5173/api/profile',data=json.dumps(profile).encode(),headers={'Content-Type':'application/json','X-XSRF-TOKEN':at},method='PUT')
assert a.open(request).status==200
assert json.loads(call(b,'/api/people/'+str(ap['id']))[1])['username']==renamed
assert next(c for c in json.loads(call(b,'/api/chats')[1]) if c['id']==chat)['peerName']==renamed
assert json.loads(call(b,base+'/messages')[1])[0]['username']==renamed
assert all(n['title'].startswith(renamed) for n in json.loads(call(b,'/api/notifications')[1]) if n['kind']=='CHAT')
# Hide only this run's synthetic market fixtures, keeping their database history.
for fixture in json.loads(call(a,'/api/my/products')[1]):
 if fixture['title'].startswith(ap['username']) and fixture['status']=='AVAILABLE':assert call(a,'/api/my/products/'+str(fixture['id'])+'/withdraw',{},at)[0]==204
print('PASS: SELL/WANTED bounded paging, public profile, one chat per pair, bidirectional chat, outsider denial, 101 unread, snapshot read-all, paging and retired orders')
