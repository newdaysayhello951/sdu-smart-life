import {ref} from 'vue';
import axios from 'axios';

export interface RealtimeUpdate {kind:'chat'|'reply'|'read'|'resync';chatId?:number}
export const realtimeStatus=ref<'offline'|'connecting'|'connected'|'reconnecting'>('offline');
let source:EventSource|null=null,checking=false,lastCheck=0;
function dispatch(update:RealtimeUpdate){window.dispatchEvent(new CustomEvent('realtime-update',{detail:update}));}
export function stopRealtime(){source?.close();source=null;realtimeStatus.value='offline';}
export function startRealtime(){
 stopRealtime();realtimeStatus.value='connecting';
 const connection=new EventSource('/api/events');source=connection;
 connection.addEventListener('ready',()=>{if(source===connection){realtimeStatus.value='connected';dispatch({kind:'resync'});}});
 connection.addEventListener('update',event=>{if(source!==connection)return;try{dispatch(JSON.parse((event as MessageEvent).data));}catch{/* Ignore malformed hints; the next reconnect resyncs from MySQL. */}});
 connection.onerror=async()=>{
  if(source!==connection)return;realtimeStatus.value='reconnecting';
  // Browser reconnects automatically; check authentication without periodic polling.
  if(checking||Date.now()-lastCheck<10000)return;checking=true;lastCheck=Date.now();
  try{await axios.get('/api/auth/me');}catch(e){if(axios.isAxiosError(e)&&e.response?.status===401)stopRealtime();}finally{checking=false;}
 };
}
