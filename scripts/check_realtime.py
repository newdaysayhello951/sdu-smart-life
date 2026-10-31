"""SSE integration through the frontend proxy; random isolated users and messages."""
from check_auth import client,call
import json,queue,threading,uuid,urllib.request

def account():
 c=client();token=json.loads(call(c,'/api/auth/csrf')[1])['token']
 user={'username':'realtime_'+uuid.uuid4().hex[:10],'password':uuid.uuid4().hex}
 assert call(c,'/api/auth/register',user,token)[0]==201
 assert call(c,'/api/auth/login',user,token)[0]==200
 return c,json.loads(call(c,'/api/auth/csrf')[1])['token'],json.loads(call(c,'/api/people/me')[1])['id']

class Stream:
 def __init__(self,c):
  self.queue=queue.Queue();self.closed=threading.Event()
  self.response=c.open('http://127.0.0.1:5173/api/events',timeout=30)
  assert self.response.headers['Content-Type'].startswith('text/event-stream')
  self.thread=threading.Thread(target=self.read,daemon=True);self.thread.start()
  assert self.event('ready')['resync'] is True
 def read(self):
  event='message';data=[]
  try:
   while True:
    line=self.response.readline()
    if not line:break
    line=line.decode().strip()
    if line.startswith('event:'):event=line[6:]
    elif line.startswith('data:'):data.append(line[5:])
    elif not line and data:self.queue.put((event,json.loads('\n'.join(data))));event='message';data=[]
  except (OSError,ValueError):pass
  finally:self.closed.set()
 def event(self,name,kind=None):
  import time
  end=time.monotonic()+8
  while time.monotonic()<end:
   event,data=self.queue.get(timeout=max(.01,end-time.monotonic()))
   if event==name and (kind is None or data.get('kind')==kind):return data
  raise AssertionError('Expected SSE event was not delivered')

assert call(client(),'/api/events')[0]==401
a,at,aid=account();b,bt,bid=account();outsider,ot,oid=account()
sa,sb,sbtab,so=Stream(a),Stream(b),Stream(b),Stream(outsider)
chat=json.loads(call(a,'/api/chats/with/'+str(bid),{},at)[1])['id']
assert call(a,f'/api/chats/{chat}/messages',{'content':'实时消息回归'},at)[0]==201
for stream in [sa,sb,sbtab]:assert stream.event('update','chat')=={'kind':'chat','chatId':chat}
messages=json.loads(call(b,f'/api/chats/{chat}/messages')[1]);assert len(messages)==1
assert call(b,f'/api/chats/{chat}/read?through='+str(messages[0]['id']),{},bt)[0]==200
for stream in [sb,sbtab]:assert stream.event('update','read')['chatId']==chat
try:
 while True:
  event,data=so.queue.get(timeout=.5)
  assert event!='update','Unrelated user received a private update'
except queue.Empty:pass
# Reconnect fetches durable missed messages, even though hints themselves are not replayed.
reconnected=Stream(b)
assert json.loads(call(b,f'/api/chats/{chat}/messages')[1])[0]['content']=='实时消息回归'
# Campus reply notifications use the same authenticated stream.
def post(c,token,message):
 boundary='check_'+uuid.uuid4().hex
 body=(f'--{boundary}\r\nContent-Disposition: form-data; name="message"\r\nContent-Type: application/json\r\n\r\n'+json.dumps(message)+f'\r\n--{boundary}--\r\n').encode()
 with c.open(urllib.request.Request('http://127.0.0.1:5173/api/conversations',data=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary,'X-XSRF-TOKEN':token})) as r:return json.loads(r.read())
place=json.loads(call(a,'/api/campus/places')[1])[0]['id']
root=post(a,at,{'placeId':place,'content':'实时回复测试'})['id']
post(b,bt,{'placeId':place,'parentId':root,'content':'收到回复'})
assert sa.event('update','reply')=={'kind':'reply'}
assert call(a,'/api/auth/logout',{},at)[0]==204
assert sa.closed.wait(5),'Logout did not close the stream'
assert call(a,'/api/events')[0]==401
print('PASS: SSE auth, commit visibility, two-way private hints, multi-tab read sync, outsider isolation, reconnect resync, campus replies and logout closure')
