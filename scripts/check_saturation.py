"""Bounded concurrency and fault injection. Refuses the active database and ports."""
import base64,binascii,hashlib,http.cookiejar,json,os,queue,socket,struct,threading,time,traceback,urllib.error,urllib.request,uuid,zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pymysql

BASE=os.environ['TEST_BASE_URL'].rstrip('/');DATABASE=os.environ['TEST_DATABASE']
assert BASE=='http://127.0.0.1:15173' and DATABASE.startswith('sdu_smart_life_qa_')
ROOT=Path(__file__).resolve().parents[1];results=[];samples=[];sample_lock=threading.Lock()
def db():return pymysql.connect(host='127.0.0.1',user=os.getenv('DB_USER','root'),password=os.environ['DB_PASSWORD'],database=DATABASE,charset='utf8mb4')
def client():return urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def req(c,path,method='GET',data=None,token=None,content_type='application/json'):
 headers={'Content-Type':content_type}
 if token:headers['X-XSRF-TOKEN']=token
 if data is not None and not isinstance(data,bytes):data=json.dumps(data).encode()
 start=time.perf_counter()
 try:
  with c.open(urllib.request.Request(BASE+path,data=data,method=method,headers=headers),timeout=30) as r:status,body=r.status,r.read()
 except urllib.error.HTTPError as e:status,body=e.code,e.read()
 finally:
  elapsed=time.perf_counter()-start
 with sample_lock:samples.append((path,status,elapsed))
 try:return status,json.loads(body)
 except (ValueError,UnicodeDecodeError):return status,body
def ok(response,status=200):assert response[0]==status,response;return response[1]
def account():
 c=client();t=ok(req(c,'/api/auth/csrf'))['token'];u={'username':'sat_'+uuid.uuid4().hex[:16],'password':uuid.uuid4().hex}
 ok(req(c,'/api/auth/register','POST',u,t),201);ok(req(c,'/api/auth/login','POST',u,t));t=ok(req(c,'/api/auth/csrf'))['token'];person=ok(req(c,'/api/people/me'))
 with db() as connection:
  with connection.cursor() as q:q.execute('SELECT id FROM app_user WHERE username=%s',(u['username'],));assert q.fetchone()[0]==person['id'],'Wrong backend/database!'
 return c,t,person['id']
def case(name):
 def decorate(function):
  start=time.perf_counter()
  try:function();result={'name':name,'passed':True}
  except Exception as error:result={'name':name,'passed':False,'error':str(error),'traceback':traceback.format_exc()[-2500:]}
  result['seconds']=round(time.perf_counter()-start,3);results.append(result);print(('PASS: ' if result['passed'] else 'FAIL: ')+name,flush=True)
 return decorate
def parallel(function,count=32,workers=16):
 with ThreadPoolExecutor(max_workers=workers) as pool:return list(pool.map(function,range(count)))
def image(color):
 def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',binascii.crc32(kind+data)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',4,4,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+bytes(color)*4)*4))+chunk(b'IEND',b'')
def multipart(c,path,part,value,token,file=None):
 boundary='sat_'+uuid.uuid4().hex
 body=(f'--{boundary}\r\nContent-Disposition: form-data; name="{part}"\r\nContent-Type: application/json\r\n\r\n'+json.dumps(value)+'\r\n').encode() if part else b''
 if file is not None:body+=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="fixture.png"\r\nContent-Type: image/png\r\n\r\n').encode()+file+b'\r\n'
 body+=f'--{boundary}--\r\n'.encode()
 return req(c,path,'POST',body,token,'multipart/form-data; boundary='+boundary)
def listing(c,t,title='saturation',kind='WANTED'):
 ok(req(c,'/api/my/products','POST',{'title':title,'description':'并发验证','price':'12.34','location':'校园','kind':kind},t),201)
 return next(p for p in ok(req(c,'/api/my/products')) if p['title']==title)['id']

a,at,aid=account();b,bt,bid=account();outside,ot,oid=account()
chat=ok(req(a,'/api/chats/with/'+str(bid),'POST',{},at))['id'];place=ok(req(a,'/api/campus/places'))[0]['id']
root=ok(multipart(a,'/api/conversations','message',{'placeId':place,'content':'并发主题'},at),201)['id']

@case('24 concurrent duplicate registrations: one winner')
def registration():
 name='race_sat_'+uuid.uuid4().hex[:12]
 def create(_):
  c=client();t=ok(req(c,'/api/auth/csrf'))['token'];return req(c,'/api/auth/register','POST',{'username':name,'password':uuid.uuid4().hex},t)[0]
 statuses=parallel(create,24,24);assert statuses.count(201)==1 and statuses.count(409)==23,statuses

@case('48 bidirectional attempts create exactly one chat')
def open_chat():
 replies=parallel(lambda i:req(a if i%2 else b,'/api/chats/with/'+str(bid if i%2 else aid),'POST',{},at if i%2 else bt),48,24)
 assert all(status==200 and result['id']==chat for status,result in replies),replies

@case('160 concurrent bidirectional messages: durable, unique, paginated, correct unread')
def messages():
 replies=parallel(lambda i:req(a if i%2 else b,f'/api/chats/{chat}/messages','POST',{'content':'concurrent-'+str(i)+'😊'},at if i%2 else bt),160,24)
 assert all(status==201 for status,_ in replies),[r for r in replies if r[0]!=201]
 seen=[];after=0
 while True:
  batch=ok(req(a,f'/api/chats/{chat}/messages?after={after}'));seen+=batch
  if len(batch)<50:break
  after=batch[-1]['id']
 assert len(seen)==160 and len({m['id'] for m in seen})==160
 assert {m['content'] for m in seen}=={'concurrent-'+str(i)+'😊' for i in range(160)}
 assert ok(req(a,'/api/notifications/unread'))['count']==80
 assert ok(req(b,'/api/notifications/unread'))['count']==80

@case('Read-all snapshot races with 40 new messages without marking future arrivals')
def read_snapshot():
 through=ok(req(a,'/api/notifications'))[0]['id']
 replies=parallel(lambda i:req(a,'/api/notifications/read-all?through='+str(through),'POST',{},at) if i==0 else req(b,f'/api/chats/{chat}/messages','POST',{'content':'new-'+str(i)},bt),41,16)
 assert all(status in (200,201) for status,_ in replies)
 with db() as connection:
  with connection.cursor() as q:
   q.execute('SELECT COUNT(*) FROM user_notification WHERE user_id=%s AND id<=%s AND read_at IS NULL',(aid,through));assert q.fetchone()[0]==0
   q.execute('SELECT COUNT(*) FROM user_notification WHERE user_id=%s AND id>%s AND read_at IS NOT NULL',(aid,through));assert q.fetchone()[0]==0

@case('Delayed message commit cannot be skipped by an ID cursor')
def message_commit_order():
 connection=db()
 try:
  with connection.cursor() as q:q.execute('INSERT INTO private_message(chat_id,sender_id,content) VALUES(%s,%s,%s)',(chat,aid,'delayed-commit'))
  with ThreadPoolExecutor(max_workers=1) as pool:
   future=pool.submit(req,b,f'/api/chats/{chat}/messages','POST',{'content':'following-commit'},bt)
   time.sleep(.3);overtook=future.done();connection.commit();ok(future.result(),201)
  assert not overtook,'A later message committed before the older message: live cursors can permanently skip it'
 finally:connection.rollback();connection.close()

@case('80 concurrent nested replies, preview order and complete pagination')
def replies():
 children=parallel(lambda i:multipart(b,'/api/conversations','message',{'placeId':place,'content':'reply-'+str(i),'parentId':root},bt),80,24)
 assert all(status==201 for status,_ in children),[r for r in children if r[0]!=201]
 ids={result['id'] for _,result in children};child=min(ids)
 ok(multipart(a,'/api/conversations','message',{'placeId':place,'content':'nested','parentId':child},at),201)
 seen=[];after=0
 while True:
  thread=ok(req(a,f'/api/conversations/{root}?after={after}'));seen+=thread['replies']
  if len(thread['replies'])<50:break
  after=thread['replies'][-1]['id']
 assert len(seen)==81 and len({m['id'] for m in seen})==81
 previews=ok(req(a,'/api/conversations?placeId='+str(place)))
 preview=next(t for t in previews if t['message']['id']==root);assert [m['id'] for m in preview['replies']]==sorted(m['id'] for m in seen)[:2]
 assert req(outside,f'/api/conversations/{child}/target/{child}')[0]==404,'A reply ID must not masquerade as a root thread'

@case('Delayed reply commit cannot be skipped by the complete-conversation cursor')
def reply_commit_order():
 connection=db()
 try:
  with connection.cursor() as q:q.execute('INSERT INTO place_comment(place_id,user_id,content,parent_id,root_id) VALUES(%s,%s,%s,%s,%s)',(place,aid,'delayed-reply',root,root))
  with ThreadPoolExecutor(max_workers=1) as pool:
   future=pool.submit(multipart,b,'/api/conversations','message',{'placeId':place,'content':'following-reply','parentId':root},bt)
   time.sleep(.3);overtook=future.done();connection.commit();ok(future.result(),201)
  assert not overtook,'A later reply overtook an uncommitted earlier reply'
 finally:connection.rollback();connection.close()

@case('Product kind changes survive editing')
def kind_edit():
 key=listing(a,at,'kind-'+uuid.uuid4().hex[:8]);value={'title':'changed kind','description':'验证','price':'1','location':'校园','kind':'SELL'}
 ok(req(a,f'/api/my/products/{key}','PUT',value,at),204)
 assert ok(req(a,f'/api/products/{key}'))['kind']=='SELL','Edit silently ignored SELL/WANTED change'

@case('Carousel snapshot does not duplicate listings when new items arrive')
def market_snapshot():
 keyword='snapshot_'+uuid.uuid4().hex[:8]
 for i in range(6):listing(a,at,keyword+str(i))
 first=ok(req(a,'/api/products?kind=WANTED&size=3&keyword='+keyword))
 listing(a,at,keyword+'new')
 second=ok(req(a,'/api/products?kind=WANTED&page=2&size=3&keyword='+keyword+'&snapshot='+str(first.get('snapshot',0))))
 assert not ({p['id'] for p in first['items']} & {p['id'] for p in second['items']}),'Concurrent publish duplicated an item across carousel pages'

@case('Concurrent rename, profile reads and publication retain stable identity')
def rename_race():
 prefix='rename_'+uuid.uuid4().hex[:8]
 def action(i):
  if i%4==0:return req(a,'/api/profile','PUT',{'username':prefix+str(i),'signature':str(i),'location':'校园','qq':'12345','dormitory':'凤凰居'},at)
  if i%4==1:return req(a,'/api/profile')
  if i%4==2:return req(a,f'/api/chats/{chat}/messages','POST',{'content':'rename-race-'+str(i)},at)
  return req(a,'/api/my/products','POST',{'title':'rename-product-'+str(i),'description':'验证','price':'1','location':'校园','kind':'WANTED'},at)
 values=parallel(action,96,24)
 assert all(status in (200,201) and (i%4 not in (0,1) or isinstance(result,dict)) for i,(status,result) in enumerate(values)),[(s,r) for s,r in values if s not in (200,201) or r is None]
 assert ok(req(a,'/api/people/me'))['id']==aid
 assert all(item['ownerId']==aid for item in ok(req(a,'/api/my/products')))

@case('Image edit atomicity, rollback, ownership, malformed files and size limits')
def image_races():
 item={'title':'image-start','description':'验证图片','price':'1','location':'校园','kind':'SELL'}
 key=ok(multipart(a,'/api/my/products/publish','product',item,at,image((255,0,0))),201)['id'];hashes={}
 for color in range(8):
  ok(multipart(a,f'/api/my/products/{key}/edit-with-image','product',{**item,'title':'color-'+str(color)},at,image((color*30,0,255))),204)
  hashes['color-'+str(color)]=hashlib.sha256(ok(req(a,f'/api/images/product/{key}'))).hexdigest()
 values=parallel(lambda i:multipart(a,f'/api/my/products/{key}/edit-with-image','product',{**item,'title':'color-'+str(i%8)},at,image(((i%8)*30,0,255))),32,16)
 assert all(status==204 for status,_ in values),values
 current=ok(req(a,f'/api/products/{key}'));blob=ok(req(a,f'/api/images/product/{key}'));assert hashes[current['title']]==hashlib.sha256(blob).hexdigest(),'Image and fields came from different transactions'
 assert multipart(outside,f'/api/my/products/{key}/edit-with-image','product',item,ot,image((0,0,0)))[0]==404
 for invalid in [b'not an image',b'<svg></svg>',image((1,2,3))[:40],b'\x89PNG\r\n\x1a\n',b'GIF89a',b'x'*(5*1024*1024+1)]:
  status,_=multipart(a,f'/api/my/products/{key}/edit-with-image','product',{**item,'title':'must-rollback'},at,invalid)
  assert status in (400,413),status
  assert ok(req(a,f'/api/products/{key}'))['title']==current['title']
  assert ok(req(a,f'/api/images/product/{key}'))==blob
 # Race an image update against withdrawal: either committed before withdrawal or rejected.
 values=parallel(lambda i:req(a,f'/api/my/products/{key}/withdraw','POST',{},at) if i==0 else multipart(a,f'/api/my/products/{key}/edit-with-image','product',item,at,image((0,255,0))),12,12)
 assert all(status in (204,404,409) for status,_ in values),values
 assert ok(req(a,f'/api/products/{key}'))['status']=='WITHDRAWN'

@case('Malformed input and authorization matrix return 4xx without leaking data')
def boundaries():
 for path in ['/api/people/me','/api/profile','/api/my/products','/api/notifications','/api/notifications/unread',f'/api/chats/{chat}/messages',f'/api/conversations/{root}','/api/campus/places']:
  assert req(client(),path)[0]==401,path
 for path in [f'/api/chats/{chat}/messages',f'/api/chats/{chat}/read?through=999999']:
  assert req(outside,path,'POST',{'content':'越权'},ot)[0]==404
 for path in ['/api/products?page=0','/api/products?size=51','/api/products?kind=OTHER','/api/products?page=9223372036854775808','/api/conversations?placeId=0','/api/notifications?before=-1']:
  assert req(a,path)[0]==400,path
 for data in [b'null',b'[]',b'{}',b'{bad json',b'{"content":null}',b'{"content":"   "}']:
  assert req(a,f'/api/chats/{chat}/messages','POST',data,at)[0]==400,data

@case('720 mixed reads at 8/24/48 concurrent clients without HTTP errors')
def mixed_load():
 paths=['/api/products?size=3','/api/products?kind=WANTED&size=3','/api/campus/places','/api/people/'+str(aid),'/api/notifications/unread','/api/my/products']
 for workers in [8,24,48]:
  values=parallel(lambda i:req(a,paths[i%len(paths)]),240,workers);assert all(status==200 for status,_ in values),[r for r in values if r[0]!=200]

@case('16 simultaneous SSE listeners: burst delivery, privacy, reconnect and logout')
def streams():
 class Stream:
  def __init__(self,c):
   self.response=c.open(BASE+'/api/events',timeout=35);self.events=queue.Queue();self.done=threading.Event()
   def read():
    event='';data=[]
    try:
     while True:
      line=self.response.readline()
      if not line:break
      line=line.decode().strip()
      if line.startswith('event:'):event=line[6:]
      elif line.startswith('data:'):data.append(line[5:])
      elif not line and data:self.events.put((event,json.loads('\n'.join(data))));data=[]
    except (OSError,ValueError):pass
    finally:self.done.set()
   threading.Thread(target=read,daemon=True).start();assert self.events.get(timeout=5)[0]=='ready'
  def close(self):
   try:self.response.fp.raw._sock.shutdown(socket.SHUT_RDWR)
   except (OSError,AttributeError):pass
   self.done.wait(1);self.response.close()
 listeners=[]
 try:
  listeners=[Stream(a) for _ in range(6)]+[Stream(b) for _ in range(6)]+[Stream(outside) for _ in range(4)]
  values=parallel(lambda i:req(a,f'/api/chats/{chat}/messages','POST',{'content':'sse-burst-'+str(i)},at),60,12);assert all(status==201 for status,_ in values)
  for stream in listeners[:12]:
   count=0;end=time.monotonic()+8
   while count<60 and time.monotonic()<end:
    event,data=stream.events.get(timeout=max(.01,end-time.monotonic()))
    if event=='update' and data.get('kind')=='chat':assert data=={'kind':'chat','chatId':chat};count+=1
   assert count==60,count
  for stream in listeners[12:]:
   while not stream.events.empty():assert stream.events.get()[0]!='update'
  listeners[0].close();ok(req(b,f'/api/chats/{chat}/messages','POST',{'content':'offline-durable'},bt),201)
  reconnected=Stream(a);listeners.append(reconnected)
  with db() as connection:
   with connection.cursor() as q:q.execute('SELECT MAX(id) FROM private_message WHERE chat_id=%s',(chat,));last=q.fetchone()[0]
  assert any(m['content']=='offline-durable' for m in ok(req(a,f'/api/chats/{chat}/messages?after={last-1}')))
  ok(req(b,'/api/auth/logout','POST',{},bt),204)
  assert all(stream.done.wait(5) for stream in listeners[6:12])
  assert req(b,'/api/events')[0]==401
 finally:
  for stream in listeners:stream.close()

durations=sorted(elapsed*1000 for _,_,elapsed in samples)
report={'database':DATABASE,'requests':len(samples),'passed':sum(r['passed'] for r in results),'failed':sum(not r['passed'] for r in results),'latencyMs':{'p50':round(durations[len(durations)//2],1),'p95':round(durations[int(len(durations)*.95)],1),'max':round(max(durations),1)},'http5xx':sum(status>=500 for _,status,_ in samples),'cases':results}
(ROOT/'.tools'/'saturation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='cases'},ensure_ascii=True),flush=True)
raise SystemExit(bool(report['failed']))
