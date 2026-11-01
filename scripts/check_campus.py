from check_auth import BASE,client,call
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
 r=urllib.request.Request(BASE+path+'/'+str(key),method='DELETE',headers={'X-XSRF-TOKEN':t})
 try:return a.open(r).status
 except urllib.error.HTTPError as e:return e.code
assert delete(other,ot)==404
assert delete(c,token)==204
assert next(x for x in json.loads(call(c,path)[1]) if x['id']==key)['content']=='（作者已删除）'
print('PASS: campus login gate, list, comments, validation, cursor, missing place, owner-only deletion')

mapped=[p for p in json.loads(call(c,'/api/campus/places')[1]) if p['mapX'] is not None]
assert len(mapped)>=134
assert all(0<=p['mapX']<100 and 0<=p['mapY']<100 and p['mapX']+p['mapWidth']<=100 and p['mapY']+p['mapHeight']<=100 for p in mapped)
p1,p2=mapped[0],mapped[1];path1='/api/campus/places/'+str(p1['id'])+'/comments'
assert call(c,path1,{'content':'地点问题'},token)[0]==201
question=json.loads(call(c,path1)[1])[0]
assert call(other,path1,{'content':'同学解答','parentId':question['id']},ot)[0]==201
answers=json.loads(call(c,path1)[1]);assert answers[0]['parentId']==question['id']
assert call(c,'/api/campus/places/'+str(p2['id'])+'/comments',{'content':'错误关联','parentId':question['id']},token)[0]==400
assert call(c,path1,{'content':'不支持多层回复','parentId':answers[0]['id']},token)[0]==400
new=next(p for p in json.loads(call(c,'/api/campus/places')[1]) if p['id']==p1['id']);assert new['commentCount']==p1['commentCount']+2
print('PASS: hotspot bounds, questions, replies, cross-place reply denial, live count')
