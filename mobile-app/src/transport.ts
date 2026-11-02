import axios from 'axios';
import {Capacitor,CapacitorHttp,registerPlugin,type PluginListenerHandle} from '@capacitor/core';
import type {ObjectDirective} from 'vue';
import {normalizeServer,isApiPath,parseSse} from './network-policy.mjs';

export const native=Capacitor.isNativePlatform();
export function serverOrigin(){return native?localStorage.getItem('campus-server')||'':'';}
export function saveServer(value:string){const origin=normalizeServer(value,import.meta.env.DEV||import.meta.env.VITE_ALLOW_LAN_HTTP==='true');localStorage.setItem('campus-server',origin);return origin;}
export function apiUrl(path:string){if(!isApiPath(path))throw Error('无效的校园接口路径');const origin=serverOrigin();if(native&&!origin)throw Error('请先设置校园服务地址');return origin+path;}
interface StreamEvent{id:string;type:'open'|'chunk'|'end'|'error';status?:number;text?:string}
interface StreamPlugin{start(options:{id:string;origin:string;path:string;method:string;headers:Record<string,string>;body?:string}):Promise<void>;stop(options:{id:string}):Promise<void>;addListener(event:'stream',listener:(event:StreamEvent)=>void):Promise<PluginListenerHandle>}
const streams=registerPlugin<StreamPlugin>('CampusStream');
const webFetch=window.fetch.bind(window);

// Native HTTP preserves the backend's session cookie. SSE uses a streaming bridge
// because the standard Capacitor HTTP bridge buffers responses before returning.
async function streamedFetch(path:string,init:RequestInit={}):Promise<Response>{
 const id=crypto.randomUUID();let listener:PluginListenerHandle|undefined,closed=false,controller:ReadableStreamDefaultController<Uint8Array>|undefined;
 const encoder=new TextEncoder();let resolveResponse:(r:Response)=>void=()=>{},rejectResponse:(e:Error)=>void=()=>{};
 const result=new Promise<Response>((resolve,reject)=>{resolveResponse=resolve;rejectResponse=reject;});
 const cleanup=()=>{if(closed)return;closed=true;init.signal?.removeEventListener('abort',abort);void listener?.remove();void streams.stop({id});};
 const abort=()=>{const e=new DOMException('已停止请求','AbortError');rejectResponse(e);try{controller?.error(e);}catch{}cleanup();};
 if(init.signal?.aborted)throw new DOMException('已停止请求','AbortError');
 const body=new ReadableStream<Uint8Array>({start(c){controller=c;},cancel:cleanup});
 listener=await streams.addListener('stream',event=>{if(event.id!==id||closed)return;
  if(event.type==='open')resolveResponse(new Response(body,{status:event.status||200,headers:{'Content-Type':'text/event-stream'}}));
  else if(event.type==='chunk')controller?.enqueue(encoder.encode(event.text||''));
  else if(event.type==='end'){controller?.close();cleanup();}
  else{const e=Error('实时连接中断，请检查网络');rejectResponse(e);try{controller?.error(e);}catch{}cleanup();}
 });
 init.signal?.addEventListener('abort',abort,{once:true});if(init.signal?.aborted){abort();return result;}
 try{await streams.start({id,origin:serverOrigin(),path,method:init.method||'GET',headers:Object.fromEntries(new Headers(init.headers).entries()),body:typeof init.body==='string'?init.body:undefined});}catch(e){rejectResponse(e instanceof Error?e:Error('连接失败'));cleanup();}
 return result;
}

class NativeEventSource extends EventTarget {
 static readonly CONNECTING=0;static readonly OPEN=1;static readonly CLOSED=2;
 readonly CONNECTING=0;readonly OPEN=1;readonly CLOSED=2;readonly withCredentials=true;readyState=0;url:string;
 onerror:((event:Event)=>unknown)|null=null;onopen:((event:Event)=>unknown)|null=null;onmessage:((event:MessageEvent)=>unknown)|null=null;
 private aborter?:AbortController;private timer?:ReturnType<typeof setTimeout>;private closed=false;private retry=1000;
 constructor(url:string){super();this.url=url;void this.connect();}
 close(){this.closed=true;this.readyState=2;clearTimeout(this.timer);this.aborter?.abort();}
 private async connect(){if(this.closed)return;this.readyState=0;this.aborter=new AbortController();try{
  const response=await streamedFetch(this.url,{signal:this.aborter.signal});if(!response.ok||!response.body)throw Error();this.readyState=1;this.retry=1000;const opened=new Event('open');this.dispatchEvent(opened);this.onopen?.(opened);
  const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='';while(!this.closed){const {done,value}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true}).replace(/\r\n/g,'\n');let end;while((end=buffer.indexOf('\n\n'))>=0){const item=parseSse(buffer.slice(0,end));buffer=buffer.slice(end+2);if(item){const event=new MessageEvent(item.event,{data:item.data});this.dispatchEvent(event);if(item.event==='message')this.onmessage?.(event);}}}
 }catch{}finally{this.aborter?.abort();if(!this.closed){this.readyState=0;const event=new Event('error');this.dispatchEvent(event);this.onerror?.(event);if(!this.closed){this.timer=setTimeout(()=>void this.connect(),this.retry);this.retry=Math.min(15000,this.retry*2);}}}}
}

export function installTransport(){
 axios.defaults.withCredentials=true;axios.defaults.timeout=25000;
 if(!native)return;
 axios.interceptors.request.use(config=>{if(config.url?.startsWith('/api/'))config.url=apiUrl(config.url);return config;});
 window.EventSource=NativeEventSource as unknown as typeof EventSource;
 window.fetch=((input:RequestInfo|URL,init?:RequestInit)=>{const path=typeof input==='string'?input:input instanceof URL?input.href:input.url;if(path==='/api/assistant/ask')return streamedFetch(path,init);if(path.startsWith('/api/'))return webFetch(apiUrl(path),init);return webFetch(input,init);}) as typeof fetch;
}

type ImageState={version:number;objectUrl?:string;path?:string};
const imageState=new WeakMap<HTMLImageElement,ImageState>();
async function updateImage(el:HTMLImageElement,value:unknown){const path=String(value||'');let state=imageState.get(el);if(!state){state={version:0};imageState.set(el,state);}if(state.path===path)return;state.path=path;const n=++state.version;if(state.objectUrl){URL.revokeObjectURL(state.objectUrl);state.objectUrl=undefined;}el.removeAttribute('src');
 if(!path)return;if(!native||!isApiPath(path)){el.src=path;return;}
 try{const result=await CapacitorHttp.get({url:apiUrl(path),responseType:'arraybuffer',connectTimeout:10000,readTimeout:20000,disableRedirects:true});if(state.version!==n||result.status!==200)return;const type=Object.entries(result.headers).find(([k])=>k.toLowerCase()==='content-type')?.[1]||'image/png';if(!type.startsWith('image/'))return;const bytes=Uint8Array.from(atob(result.data),c=>c.charCodeAt(0));state.objectUrl=URL.createObjectURL(new Blob([bytes],{type}));el.src=state.objectUrl;}catch{el.alt=el.alt||'图片加载失败';}}
export const mobileSrc:ObjectDirective<HTMLImageElement,unknown>={mounted(el,b){void updateImage(el,b.value);},updated(el,b){void updateImage(el,b.value);},unmounted(el){const state=imageState.get(el);if(state){state.version++;if(state.objectUrl)URL.revokeObjectURL(state.objectUrl);}imageState.delete(el);}};
