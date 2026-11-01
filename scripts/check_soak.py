"""Bounded 45s mixed read/write load; isolated QA database only. Requires PyMySQL."""
import hashlib,http.cookiejar,json,os,threading,time,urllib.request,urllib.error,uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pymysql

BASE=os.environ['TEST_BASE_URL'];DATABASE=os.environ['TEST_DATABASE']
assert BASE=='http://127.0.0.1:15173' and DATABASE.startswith('sdu_smart_life_qa_')
opener=lambda:urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
samples=[];errors=[];lock=threading.Lock();sent=[]
def request(c,path,method='GET',body=None,token=None,expected=200):
 started=time.perf_counter();headers={'Content-Type':'application/json'}
 if token:headers['X-XSRF-TOKEN']=token
 data=json.dumps(body).encode() if body is not None else None
 try:
  with c.open(urllib.request.Request(BASE+path,data=data,method=method,headers=headers),timeout=20) as r:status,payload=r.status,r.read()
 except urllib.error.HTTPError as e:status,payload=e.code,e.read()
 except OSError as error:
  with lock:errors.append({'path':path,'transport':str(error)})
  return None
 with lock:
  samples.append((status,time.perf_counter()-started))
  if status!=expected:errors.append({'path':path,'status':status,'body':payload[:160].decode(errors='replace')})
 try:return json.loads(payload)
 except ValueError:return None
def account(_):
 c=opener();t=request(c,'/api/auth/csrf')['token'];name='soak_'+uuid.uuid4().hex[:16];user={'username':name,'password':uuid.uuid4().hex}
 request(c,'/api/auth/register','POST',user,t,201);request(c,'/api/auth/login','POST',user,t);person=request(c,'/api/people/me')
 assert person is not None
 return c,t,person['id']
with ThreadPoolExecutor(max_workers=12) as pool:accounts=list(pool.map(account,range(24)))
chats=[]
for i in range(0,24,2):
 c,t,_=accounts[i];chat=request(c,'/api/chats/with/'+str(accounts[i+1][2]),'POST',{},t)['id'];chats.append(chat)
start=time.monotonic();deadline=start+45;barrier=threading.Barrier(64)
def worker(index):
 c,t,user=accounts[index%24];chat=chats[(index%24)//2];counter=0;cursor=0;barrier.wait()
 while time.monotonic()<deadline:
  with lock:
   if len(samples)>25000:return
  action=(counter+index)%8
  if action==0:
   text=f'soak-{index}-{counter}';request(c,f'/api/chats/{chat}/messages','POST',{'content':text},t,201)
   with lock:sent.append((chat,user,text))
  elif action==1:
   batch=request(c,f'/api/chats/{chat}/messages?after={cursor}')
   if batch:cursor=batch[-1]['id']
  elif action==2:request(c,f'/api/chats/{chat}/read?through={cursor}','POST',{},t)
  else:request(c,['/api/products?size=3','/api/products?kind=WANTED&size=3','/api/campus/places','/api/notifications/unread','/api/my/products'][action-3])
  counter+=1
with ThreadPoolExecutor(max_workers=64) as pool:list(pool.map(worker,range(64)))
elapsed=time.monotonic()-start
connection=pymysql.connect(host='127.0.0.1',user=os.getenv('DB_USER','root'),password=os.environ['DB_PASSWORD'],database=DATABASE)
with connection.cursor() as q:
 for chat in chats:
  expected={(user,text) for cid,user,text in sent if cid==chat}
  q.execute('SELECT sender_id,content FROM private_message WHERE chat_id=%s',(chat,));actual=set(q.fetchall())
  if expected!=actual:errors.append({'chat':chat,'expectedMessages':len(expected),'actualMessages':len(actual)})
  q.execute('SELECT COUNT(*) FROM user_notification WHERE chat_id=%s',(chat,));notifications=q.fetchone()[0]
  if notifications!=len(actual):errors.append({'chat':chat,'messages':len(actual),'notifications':notifications})
connection.close();durations=sorted(seconds*1000 for _,seconds in samples)
report={'concurrency':64,'seconds':round(elapsed,2),'requests':len(samples),'messages':len(sent),'http5xx':sum(status>=500 for status,_ in samples),'p50ms':round(durations[len(durations)//2],1),'p95ms':round(durations[int(len(durations)*.95)],1),'maxMs':round(max(durations),1),'errors':errors}
(Path(__file__).resolve().parents[1]/'.tools/soak-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True));raise SystemExit(bool(errors))
