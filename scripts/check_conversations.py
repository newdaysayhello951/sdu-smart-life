from check_auth import client,call
import json,uuid,urllib.request,urllib.error,base64
from pathlib import Path
c=client();token=json.loads(call(c,'/api/auth/csrf')[1])['token'];u={'username':'thread_'+uuid.uuid4().hex[:10],'password':uuid.uuid4().hex}
assert call(c,'/api/auth/register',u,token)[0]==201
assert call(c,'/api/auth/login',u,token)[0]==200
places=json.loads(call(c,'/api/campus/places')[1]);names={p['name'] for p in places};assert '凤凰居1号楼（一多书院）' in names and '凤凰居2号楼（从文书院）' in names
place=places[0]['id'];other=places[1]['id']
def post(text,parent=None,file=None,place_id=place):
 boundary=uuid.uuid4().hex
 body=(f'--{boundary}\r\nContent-Disposition: form-data; name="message"\r\nContent-Type: application/json\r\n\r\n'+json.dumps({'placeId':place_id,'content':text,'parentId':parent})+'\r\n').encode()
 if file is not None:body+=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="image.gif"\r\nContent-Type: image/gif\r\n\r\n').encode()+file+b'\r\n'
 body+=f'--{boundary}--\r\n'.encode()
 req=urllib.request.Request('http://127.0.0.1:5173/api/conversations',data=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary,'X-XSRF-TOKEN':token})
 try:
  with c.open(req) as r:return r.status,json.loads(r.read())
 except urllib.error.HTTPError as e:return e.code,None
assert post('   ')[0]==400
assert post('invalid image',file=b'no image')[0]==400
status,data=post('主题😊');assert status==201;root=data['id']
ids=[]
for i in range(4):
 status,data=post('回复'+str(i),root if i==0 else ids[-1]);assert status==201;ids.append(data['id'])
thread=next(t for t in json.loads(call(c,'/api/conversations?placeId='+str(place))[1]) if t['message']['id']==root)
assert [r['id'] for r in thread['replies']]==ids[:2]
assert thread['message']['replyCount']==4
full=json.loads(call(c,'/api/conversations/'+str(root))[1]);assert [r['id'] for r in full['replies']]==ids
assert full['replies'][1]['parentId']==ids[0]
assert post('wrong place',root,place_id=other)[0]==400
assert post('missing parent',999999999)[0]==400
assert call(client(),'/api/conversations/'+str(root))[0]==401
assert call(c,'/api/conversations/avatars/'+str(full['message']['userId']))[0]==200
photo=(Path(__file__).resolve().parents[1]/'frontend/public/assets/legacy/images/sdu.jpg').read_bytes()
status,data=post('',root,file=photo);assert status==201
image=call(c,'/api/conversations/'+str(data['id'])+'/image');assert image[0]==200 and image[1].startswith(b'\x89PNG')
assert call(client(),'/api/conversations/'+str(data['id'])+'/image')[0]==401
gif=base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
status,data=post('表情',root,file=gif);assert status==201
assert call(c,'/api/conversations/'+str(data['id'])+'/image')[1]==gif
assert call(c,'/api/conversations/'+str(root)+'?after='+str(ids[1]))[0]==200
print('PASS: corrected names, nested replies, earliest two previews, complete thread, reply targeting, avatars, images, GIF, auth and invalid inputs')
