import {defineConfig} from 'vite';
import vue from '@vitejs/plugin-vue';
import {fileURLToPath} from 'node:url';
import {resolve,dirname} from 'node:path';
import {existsSync,cpSync,mkdirSync,createReadStream,statSync} from 'node:fs';
const root=dirname(fileURLToPath(import.meta.url));
const artwork=resolve(root,'../frontend/public/assets');
// Assets stay owned by the web project; the APK receives a filtered build copy.
export default defineConfig(({mode})=>({
 define:{'import.meta.env.VITE_ALLOW_LAN_HTTP':JSON.stringify(mode==='debug'?'true':'false')},
 plugins:[{
  name:'mobile-shared-assets',enforce:'pre',
  transform(code,id){if(id.endsWith('.vue'))return code.replace(/:src=/g,'v-mobile-src=');},
  configureServer(server){server.middlewares.use((req,res,next)=>{if(!req.url?.startsWith('/assets/'))return next();try{const path=resolve(artwork,decodeURIComponent(req.url.split('?')[0].slice(8)));if(!path.startsWith(artwork+'/')&&!path.startsWith(artwork+'\\'))return next();if(!statSync(path).isFile())return next();const ext=path.split('.').pop()||'';res.setHeader('Content-Type',({webp:'image/webp',png:'image/png',jpg:'image/jpeg',jpeg:'image/jpeg',gif:'image/gif',svg:'image/svg+xml',json:'application/json'} as Record<string,string>)[ext]||'application/octet-stream');createReadStream(path).pipe(res);}catch{next();}});},
  closeBundle(){const dest=resolve(root,'dist/assets');mkdirSync(dest,{recursive:true});for(const name of ['legacy','assistant','campus']){const source=resolve(artwork,name);if(existsSync(source))cpSync(source,resolve(dest,name),{recursive:true,filter:p=>!p.endsWith('qingdao-campus.jpg')});}},
 },vue({template:{transformAssetUrls:{includeAbsolute:false}}})],
 resolve:{dedupe:['vue','vue-router','axios'],alias:{axios:resolve(root,'node_modules/axios/index.js'),'@campus':resolve(root,'../frontend/src')}},
 server:{fs:{allow:[resolve(root,'..')]},proxy:{'/api':{target:process.env.API_PROXY_TARGET||'http://127.0.0.1:8080',changeOrigin:true}}},
 preview:{proxy:{'/api':{target:process.env.API_PROXY_TARGET||'http://127.0.0.1:8080',changeOrigin:true}}},
}));
