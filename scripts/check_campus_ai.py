"""Campus AI access/history regression; optional real-provider checks in isolated QA only."""
from check_auth import client,call,BASE
import json,uuid,os,time,urllib.request,urllib.error
from pathlib import Path

def account():
 c=client();t=json.loads(call(c,'/api/auth/csrf')[1])['token'];u={'username':'aiqa_'+uuid.uuid4().hex[:10],'password':uuid.uuid4().hex}
 assert call(c,'/api/auth/register',u,t)[0]==201
 assert call(c,'/api/auth/login',u,t)[0]==200
 return c,json.loads(call(c,'/api/auth/csrf')[1])['token'],u
assert call(client(),'/api/assistant/status')[0]==401
c,t,u=account();other,ot,_=account();status=json.loads(call(c,'/api/assistant/status')[1]);assert call(c,'/api/assistant/conversations',{},None)[0]==403
cid=json.loads(call(c,'/api/assistant/conversations',{},t)[1])['id']
assert call(other,'/api/assistant/conversations/'+cid)[0]==404
assert call(other,'/api/assistant/ask',{'conversationId':cid,'question':'越权'},ot)[0]==404
assert call(c,'/api/assistant/ask',{'conversationId':cid,'question':''},t)[0]==400
assert call(c,'/api/assistant/ask',{'conversationId':cid,'question':'x'*2001},t)[0]==400
assert json.loads(call(c,'/api/assistant/conversations/'+cid)[1])==[]
if os.getenv('AI_LIVE_TESTS')=='1':
 assert status['enabled']
 for attempt in range(100):
  status=json.loads(call(c,'/api/assistant/status')[1])
  if status['knowledge']['documents']>=3 and not status['knowledge']['syncing']:break
  time.sleep(2)
 print('KNOWLEDGE',status['knowledge'],flush=True)
 assert status['knowledge']['documents']>=3
 root=Path(__file__).resolve().parents[1];(root/'.tools/ai-ui-fixture.json').write_text(json.dumps({**u,'conversationId':cid}))
 report=[]
 def ask(q):
  req=urllib.request.Request(BASE+'/api/assistant/ask',data=json.dumps({'conversationId':cid,'question':q}).encode(),headers={'Content-Type':'application/json','X-XSRF-TOKEN':t})
  with c.open(req,timeout=175) as r:raw=r.read().decode()
  events=[]
  for block in raw.replace('\r\n','\n').split('\n\n'):
   name='';data=''
   for line in block.splitlines():
    if line.startswith('event:'):name=line[6:].strip()
    if line.startswith('data:'):data+=line[5:].strip()
   if data:events.append((name,json.loads(data)))
  assert any(n=='done' for n,d in events),[(n,d) for n,d in events if n=='error']
  text=''.join(d['text'] for n,d in events if n=='token');assert len(text)>20
  sources=next((d for n,d in events if n=='sources'),[]);cards=next((d for n,d in events if n=='cards'),[])
  report.append({'question':q,'answer':text,'sources':sources,'cards':cards,'steps':[d for n,d in events if n=='step']})
  print('ANSWER',text[:100].replace('\n',' '),'CARDS',len(cards),'SOURCES',len(sources),flush=True)
  return text,sources,cards
 text,sources,cards=ask('根据官方资料，山大本科生图书可以借多久？请引用出处。');assert sources and '30' in text
 text,sources,cards=ask('请使用地点查询工具查找图书馆，给我地图入口。');assert any(x['url'].startswith('/campus?place=') for x in cards)
 text,sources,cards=ask('请使用通知工具查看我自己的未读通知。');assert any(x['url']=='/notifications' for x in cards)
 assert call(c,'/api/my/products',{'title':'海棠钥匙','description':'测试拾物，私聊核验','price':'0','location':'图书馆','kind':'FOUND'},t)[0]==201
 text,sources,cards=ask('请用商品失物查询工具，kind=FOUND，query=海棠钥匙，找拾物招领信息。');assert any(x['url'].startswith('/lost-found/') for x in cards)
 history=json.loads(call(c,'/api/assistant/conversations/'+cid)[1]);assert len(history)==8 and history[-1]['metadata'].get('cards')
 time.sleep(2)
 req=urllib.request.Request(BASE+'/api/assistant/ask',data=json.dumps({'conversationId':cid,'question':'请详细介绍校园网络服务'}).encode(),headers={'Content-Type':'application/json','X-XSRF-TOKEN':t})
 stream=c.open(req,timeout=175);assert stream.readline().startswith(b'event:')
 assert call(c,'/api/assistant/ask',{'conversationId':cid,'question':'重复并发请求'},t)[0]==429
 assert call(c,'/api/assistant/cancel',{},t)[0]==204
 stream.close()
 for attempt in range(20):
  latest=json.loads(call(c,'/api/assistant/conversations/'+cid)[1])
  if latest[-1]['role']=='assistant' and latest[-1]['metadata'].get('interrupted'):break
  time.sleep(.5)
 else:raise AssertionError('Cancellation did not persist interrupted history')
 (root/'.tools/ai-live-report.json').write_text(json.dumps({'status':status,'runs':report},ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: assistant login/CSRF, scoped conversations, invalid requests'+(' and live RAG/tools/stream/history' if os.getenv('AI_LIVE_TESTS')=='1' else ''))
