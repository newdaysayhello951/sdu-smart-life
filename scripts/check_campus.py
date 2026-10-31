from check_auth import client,call
import uuid,json,urllib.request,urllib.error
c=client();token=json.loads(call(c,'/api/auth/csrf')[1])['token'];u={'username':'campus_'+uuid.uuid4().hex[:10],'password':uuid.uuid4().hex}
assert call(c,'/api/campus/places')[0]==401
assert call(c,'/api/auth/register',u,token)[0]==201
assert call(c,'/api/auth/login',u,token)[0]==200
places=json.loads(call(c,'/api/campus/places')[1]);assert places
path='/api/campus/places/'+str(places[0]['id'])+'/comments'
assert call(c,path,{'content':'   '},token)[0]==400
assert call(c,path,{'content':'x'*1001},token)[0]==400
assert call(c,'/api/campus/places/999999/comments')[0]==404
assert call(c,path+'?before=-1')[0]==400
assert call(c,path,{'content':'校园回归留言'},token)[0]==201
comments=json.loads(call(c,path)[1]);key=comments[0]['id'];assert comments[0]['username']==u['username']
other=client();ot=json.loads(call(other,'/api/auth/csrf')[1])['token'];v={'username':'campus_'+uuid.uuid4().hex[:10],'password':uuid.uuid4().hex}
assert call(other,'/api/auth/register',v,ot)[0]==201
assert call(other,'/api/auth/login',v,ot)[0]==200
def delete(a,t):
 r=urllib.request.Request('http://127.0.0.1:5173'+path+'/'+str(key),method='DELETE',headers={'X-XSRF-TOKEN':t})
 try:return a.open(r).status
 except urllib.error.HTTPError as e:return e.code
assert delete(other,ot)==404
assert delete(c,token)==204
assert all(x['id']!=key for x in json.loads(call(c,path)[1]))
print('PASS: campus login gate, list, comments, validation, cursor, missing place, owner-only deletion')
