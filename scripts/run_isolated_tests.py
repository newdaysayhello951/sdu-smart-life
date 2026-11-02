"""Run tests on a new QA database/ports, never on the active application database.
Requires PyMySQL, a built backend JAR and installed frontend dependencies.
"""
import argparse,json,os,socket,subprocess,sys,time,urllib.request,uuid,tempfile
from pathlib import Path
import pymysql

ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--keep',action='store_true',help='Keep QA servers/database for browser verification');p.add_argument('--stress',action='store_true');p.add_argument('--soak',action='store_true');p.add_argument('--jar',type=Path,default=ROOT/'.tools/qa-build/target/smart-life-0.1.0-SNAPSHOT.jar');options=p.parse_args()
 if not options.jar.is_file():raise RuntimeError('Build the isolated QA JAR first; see README')
 for port in (18080,15173):
  with socket.socket() as probe:probe.bind(('127.0.0.1',port))
 name='sdu_smart_life_qa_'+uuid.uuid4().hex[:12]
 connection=pymysql.connect(host='127.0.0.1',user=os.getenv('DB_USER','root'),password=os.environ['DB_PASSWORD'])
 with connection.cursor() as cursor:cursor.execute('CREATE DATABASE `'+name+'` CHARACTER SET utf8mb4')
 env=dict(os.environ,DB_URL='jdbc:mysql://127.0.0.1:3306/'+name+'?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai',TEST_DATABASE=name,TEST_BASE_URL='http://127.0.0.1:15173',API_PROXY_TARGET='http://127.0.0.1:18080')
 logs=[];processes=[];success=False
 temp=Path(tempfile.gettempdir())/'sdu-campus-ai-native';temp.mkdir(exist_ok=True)
 try:
  for label,args in [('backend',[os.getenv('QA_JAVA_EXECUTABLE','java'),'-Djava.io.tmpdir='+str(temp),'-jar',str(options.jar),'--server.port=18080']),('frontend',['node','frontend/node_modules/vite/bin/vite.js','--config','frontend/vite.config.ts','--host','127.0.0.1','--port','15173','--strictPort'])]:
   log=(ROOT/'.tools'/('qa-'+label+'.log')).open('wb');logs.append(log)
   if label=='frontend':args=['node','node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','15173','--strictPort']
   processes.append(subprocess.Popen(args,cwd=ROOT if label=='backend' else ROOT/'frontend',env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)))
  metadata={'database':name,'baseUrl':env['TEST_BASE_URL'],'backendPid':processes[0].pid,'frontendPid':processes[1].pid}
  (ROOT/'.tools'/'qa-runtime.json').write_text(json.dumps(metadata,indent=2))
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  for attempt in range(100):
   if any(process.poll() is not None for process in processes):raise RuntimeError('QA server failed; inspect .tools/qa-*.log')
   try:
    with opener.open(env['TEST_BASE_URL']+'/actuator/health',timeout=2) as response:
     if json.load(response)['status']=='UP':break
   except (OSError,ValueError):time.sleep(.3)
  else:raise RuntimeError('QA servers did not become ready')
  result=subprocess.run([sys.executable,str(ROOT/'scripts/run_regression.py')],cwd=ROOT,env=env)
  if result.returncode:raise RuntimeError('Baseline regression failed')
  if options.stress:subprocess.run([sys.executable,str(ROOT/'scripts/check_saturation.py')],cwd=ROOT,env=env,check=True)
  if options.soak:subprocess.run([sys.executable,str(ROOT/'scripts/check_soak.py')],cwd=ROOT,env=env,check=True)
  success=True
 finally:
  if options.keep and len(processes)==2 and all(process.poll() is None for process in processes):
   print('QA retained for verification: '+name,flush=True)
  else:
   for process in reversed(processes):
    if os.name=='nt':subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    else:process.terminate()
    try:process.wait(timeout=10)
    except subprocess.TimeoutExpired:process.kill();process.wait()
   for log in logs:log.close()
   assert name.startswith('sdu_smart_life_qa_') and len(name)==30
   with connection.cursor() as cursor:cursor.execute('DROP DATABASE `'+name+'`')
  connection.close()
 if not success:sys.exit(1)

if __name__=='__main__':main()
