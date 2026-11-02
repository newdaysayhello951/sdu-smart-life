<script setup lang="ts">
import {ref,computed,onMounted,onUnmounted} from 'vue';
interface Place{id:number;name:string;description:string;mapX:number|null;mapY:number|null;mapWidth:number|null;mapHeight:number|null;commentCount:number}
interface Level{width:number;height:number}
interface Manifest{width:number;height:number;tileSize:number;levels:Level[]}
const props=defineProps<{places:Place[];activeId?:number}>();
const emit=defineEmits<{select:[place:Place];zoom:[value:number]}>();
const host=ref<HTMLElement>(),canvas=ref<HTMLCanvasElement>(),width=ref(1),height=ref(1),scale=ref(1),x=ref(0),y=ref(0),dragging=ref(false),failed=ref(false);
const baseWidth=computed(()=>Math.min(width.value,height.value*8410/11890));
const mapWidth=computed(()=>baseWidth.value*scale.value),mapHeight=computed(()=>mapWidth.value*11890/8410);
const left=computed(()=>(width.value-mapWidth.value)/2+x.value),top=computed(()=>(height.value-mapHeight.value)/2+y.value);
const visiblePlaces=computed(()=>props.places.map(p=>({p,l:left.value+(p.mapX||0)*mapWidth.value/100,t:top.value+(p.mapY||0)*mapHeight.value/100,w:(p.mapWidth||0)*mapWidth.value/100,h:(p.mapHeight||0)*mapHeight.value/100})).filter(p=>p.l+p.w>=0&&p.t+p.h>=0&&p.l<=width.value&&p.t<=height.value));
let manifest:Manifest|undefined,preview:HTMLImageElement|undefined,observer:ResizeObserver|undefined,frame=0,disposed=false,running=0,dpr=1,needed=new Set<string>(),queue:string[]=[],qualityTimer:ReturnType<typeof setTimeout>|undefined,interacting=false;
const cache=new Map<string,HTMLImageElement>(),loading=new Map<string,HTMLImageElement>(),bad=new Set<string>();
let startX=0,startY=0,originX=0,originY=0,moved=false,pointerX=0,pointerY=0,panPending=false,wheelDelta=0,wheelX=0,wheelY=0;
function constrain(){const lx=Math.max(0,(mapWidth.value-width.value)/2),ly=Math.max(0,(mapHeight.value-height.value)/2);x.value=Math.max(-lx,Math.min(lx,x.value));y.value=Math.max(-ly,Math.min(ly,y.value));}
function settle(){interacting=true;clearTimeout(qualityTimer);qualityTimer=setTimeout(()=>{interacting=false;schedule();},140);}
function zoom(value:number,anchorX=0,anchorY=0){const old=scale.value;scale.value=Math.max(1,Math.min(24,value));x.value=anchorX-(anchorX-x.value)*scale.value/old;y.value=anchorY-(anchorY-y.value)*scale.value/old;constrain();emit('zoom',scale.value);settle();schedule();}
function reset(){x.value=0;y.value=0;zoom(1);}
function actualPixels(){zoom(8410/dpr/baseWidth.value);}
function down(e:PointerEvent){if(e.button!==0)return;startX=e.clientX;startY=e.clientY;originX=x.value;originY=y.value;moved=false;dragging.value=true;host.value?.setPointerCapture(e.pointerId);}
function move(e:PointerEvent){if(!dragging.value)return;pointerX=e.clientX;pointerY=e.clientY;if(Math.hypot(pointerX-startX,pointerY-startY)>5)moved=true;if(moved){panPending=true;settle();schedule();}}
function up(e:PointerEvent){if(!dragging.value)return;move(e);dragging.value=false;if(!moved){const rect=host.value!.getBoundingClientRect(),px=e.clientX-rect.left,py=e.clientY-rect.top;const hit=visiblePlaces.value.find(v=>px>=v.l&&px<=v.l+v.w&&py>=v.t&&py<=v.t+v.h);if(hit)emit('select',hit.p);}schedule();}
function wheel(e:WheelEvent){const r=host.value!.getBoundingClientRect();wheelX=e.clientX-r.left-width.value/2;wheelY=e.clientY-r.top-height.value/2;wheelDelta+=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?height.value:1);schedule();}
function schedule(){if(!disposed&&!frame)frame=requestAnimationFrame(()=>{frame=0;if(panPending){panPending=false;x.value=originX+pointerX-startX;y.value=originY+pointerY-startY;constrain();}if(wheelDelta){const delta=wheelDelta;wheelDelta=0;zoom(scale.value*Math.exp(-delta*.002),wheelX,wheelY);}draw();});}
function trim(){for(const key of cache.keys()){if(cache.size<=128)break;if(!needed.has(key))cache.delete(key);}}
function pump(){while(!disposed&&running<6&&queue.length){const key=queue.shift()!;if(!needed.has(key)||cache.has(key)||loading.has(key)||bad.has(key))continue;const img=new Image();img.decoding='async';running++;loading.set(key,img);img.onload=()=>{running--;loading.delete(key);if(disposed)return;cache.set(key,img);trim();if(needed.has(key))schedule();pump();};img.onerror=()=>{running--;loading.delete(key);bad.add(key);if(!disposed)pump();};img.src='/assets/campus/tiles/'+key+'.webp';}}
function draw(){const ctx=canvas.value?.getContext('2d');if(!ctx)return;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,width.value,height.value);ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality=interacting?'low':'high';const mw=mapWidth.value,mh=mapHeight.value,l=left.value,t=top.value;
  if(preview?.complete&&preview.naturalWidth)ctx.drawImage(preview,l,t,mw,mh);
  if(!manifest)return;const target=mw*dpr;let level=manifest.levels.findIndex(v=>v.width>=target);if(level<0)level=manifest.levels.length-1;const info=manifest.levels[level],size=manifest.tileSize;
  const minCol=Math.max(0,Math.floor(-l/mw*info.width/size)),maxCol=Math.min(Math.ceil(info.width/size)-1,Math.floor((width.value-l)/mw*info.width/size));
  const minRow=Math.max(0,Math.floor(-t/mh*info.height/size)),maxRow=Math.min(Math.ceil(info.height/size)-1,Math.floor((height.value-t)/mh*info.height/size));
  needed=new Set<string>();queue=[];
  for(let row=minRow;row<=maxRow;row++)for(let col=minCol;col<=maxCol;col++){const key=`${level}/${col}-${row}`;needed.add(key);const img=cache.get(key);if(img){ctx.drawImage(img,l+col*size/info.width*mw,t+row*size/info.height*mh,img.naturalWidth/info.width*mw,img.naturalHeight/info.height*mh);}else queue.push(key);}
  trim();pump();
}
onMounted(()=>{preview=new Image();preview.decoding='async';preview.onload=schedule;preview.onerror=()=>{failed.value=true;};preview.src='/assets/campus/qingdao-preview.webp';fetch('/assets/campus/tiles/manifest.json').then(r=>{if(!r.ok)throw Error();return r.json();}).then((m:Manifest)=>{if(!disposed){manifest=m;schedule();}}).catch(()=>{if(!disposed)failed.value=true;});observer=new ResizeObserver(()=>{if(!host.value||!canvas.value)return;width.value=host.value.clientWidth;height.value=host.value.clientHeight;dpr=Math.min(window.devicePixelRatio||1,2,Math.sqrt(4_000_000/(width.value*height.value)));canvas.value.width=Math.max(1,Math.round(width.value*dpr));canvas.value.height=Math.max(1,Math.round(height.value*dpr));constrain();schedule();});observer.observe(host.value!);});
onUnmounted(()=>{disposed=true;observer?.disconnect();cancelAnimationFrame(frame);clearTimeout(qualityTimer);if(preview){preview.onload=null;preview.onerror=null;preview.src='';}for(const img of loading.values()){img.onload=null;img.onerror=null;img.src='';}loading.clear();cache.clear();queue=[];});
defineExpose({zoom,reset,actualPixels});
</script>
<template><div ref="host" class="map-surface" :class="{dragging}" @wheel.prevent="wheel" @pointerdown="down" @pointermove="move" @pointerup="up" @pointercancel="dragging=false;panPending=false">
  <canvas ref="canvas" role="img" aria-label="山东大学青岛校区高清分级地图"></canvas>
  <button v-for="v in visiblePlaces" :key="v.p.id" class="surface-hotspot" :class="{selected:activeId===v.p.id}" :style="{left:v.l+'px',top:v.t+'px',width:v.w+'px',height:v.h+'px'}" :aria-label="v.p.name" @mouseenter="!dragging&&emit('select',v.p)" @focus="emit('select',v.p)" @click="($event.detail===0)&&emit('select',v.p)"></button>
  <p v-if="failed" class="surface-error" role="alert">地图资源加载失败，请刷新后重试。</p>
</div></template>
<style scoped>
.map-surface{position:absolute;inset:110px 16px 90px;overflow:hidden;touch-action:none;cursor:grab;contain:strict}.map-surface.dragging{cursor:grabbing}.map-surface canvas{display:block;width:100%;height:100%;pointer-events:none}.surface-hotspot{position:absolute;padding:0;border:1px solid transparent;border-radius:2px;background:transparent;cursor:inherit}.surface-hotspot:hover,.surface-hotspot.selected,.surface-hotspot:focus-visible{background:#ffcb4d45;border-color:#dba738;outline:0}.surface-hotspot:focus-visible{outline:2px solid #ffe2a0;outline-offset:2px}.surface-error{position:absolute;top:10px;left:20px;background:#172e35;color:#fff;padding:12px}@media(max-width:700px){.map-surface{inset:95px 10px 120px}}
</style>
