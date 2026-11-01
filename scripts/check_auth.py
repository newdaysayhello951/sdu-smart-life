"""Run against a local server; creates one uniquely named verification account."""
import urllib.request, urllib.error, http.cookiejar, json, uuid, os
BASE = os.environ.get('TEST_BASE_URL','').rstrip('/')
if BASE != 'http://127.0.0.1:15173':
 raise SystemExit('Use the isolated QA runner; TEST_BASE_URL must be http://127.0.0.1:15173')
def client():
 return urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def call(c, path, data=None, token=None):
 headers={'Content-Type':'application/json'}
 if token: headers['X-XSRF-TOKEN']=token
 r=urllib.request.Request(BASE+path, data=json.dumps(data).encode() if data is not None else None, headers=headers)
 try:
  with c.open(r,timeout=30) as response: return response.status, response.read()
 except urllib.error.HTTPError as e: return e.code,e.read()
a,b=client(),client()
assert call(a,'/api/auth/me')[0]==401
status,body=call(a,'/api/auth/csrf');assert status==200
token=json.loads(body)['token']
user={'username':'check_'+uuid.uuid4().hex[:12],'password':uuid.uuid4().hex}
assert call(a,'/api/auth/register',user)[0]==403
assert call(a,'/api/auth/register',user,token)[0]==201
assert call(a,'/api/auth/register',user,token)[0]==409
assert call(a,'/api/auth/login',{**user,'password':'wrongpass'},token)[0]==401
assert call(a,'/api/auth/login',user,token)[0]==200
assert json.loads(call(a,'/api/auth/me')[1])['username']==user['username']
assert call(b,'/api/auth/me')[0]==401
status,body=call(a,'/api/auth/csrf');token=json.loads(body)['token']
assert call(a,'/api/auth/logout',{},token)[0]==204
assert call(a,'/api/auth/me')[0]==401
print('PASS: register, duplicate, wrong password, login, session isolation, CSRF, logout')
