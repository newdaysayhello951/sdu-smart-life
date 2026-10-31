from check_auth import client,call
import json,uuid,urllib.request,urllib.error
receiver=client();rt=json.loads(call(receiver,'/api/auth/csrf')[1])['token'];receiver_user={'username':'focus_owner_'+uuid.uuid4().hex[:9],'password':uuid.uuid4().hex};assert call(receiver,'/api/auth/register',receiver_user,rt)[0]==201;assert call(receiver,'/api/auth/login',receiver_user,rt)[0]==200
sender=client();st=json.loads(call(sender,'/api/auth/csrf')[1])['token'];u={'username':'focus_'+uuid.uuid4().hex[:10],'password':uuid.uuid4().hex};assert call(sender,'/api/auth/register',u,st)[0]==201;assert call(sender,'/api/auth/login',u,st)[0]==200
place=json.loads(call(receiver,'/api/campus/places')[1])[0]['id']
def post(c,t,parent,text):
 boundary=uuid.uuid4().hex
 body=(f'--{boundary}\r\nContent-Disposition: form-data; name="message"\r\nContent-Type: application/json\r\n\r\n'+json.dumps({'placeId':place,'content':text,'parentId':parent})+f'\r\n--{boundary}--\r\n').encode()
 r=urllib.request.Request('http://127.0.0.1:5173/api/conversations',data=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary,'X-XSRF-TOKEN':t})
 with c.open(r) as response:return json.loads(response.read())['id']
root=post(receiver,rt,None,'通知定位回归主题')
for i in range(55):target=post(sender,st,root,'定位回复 '+str(i+1))
notifications=json.loads(call(receiver,'/api/notifications')[1]);notice=next(n for n in notifications if '?focus='+str(target) in n['link'])
assert notice['link']==f'/campus/{place}/conversations/{root}?focus={target}'
assert call(receiver,f'/api/conversations/{root}/target/{target}')[0]==204
assert call(receiver,f'/api/conversations/{root}/target/999999999')[0]==404
assert call(sender,f'/api/conversations/{target}/target/{root}')[0]==404
first=json.loads(call(receiver,'/api/conversations/'+str(root))[1]);assert len(first['replies'])==50 and all(r['id']!=target for r in first['replies'])
second=json.loads(call(receiver,'/api/conversations/'+str(root)+'?after='+str(first['replies'][-1]['id']))[1]);assert any(r['id']==target for r in second['replies'])
from pathlib import Path
(rootpath:=Path(__file__).resolve().parents[1]/'.tools/focus-fixture.json').write_text(json.dumps({'link':notice['link'],'target':target}),encoding='utf-8')
print('PASS: exact notification target, cross-thread rejection, target after first50, full paging')
print(notice['link'])
