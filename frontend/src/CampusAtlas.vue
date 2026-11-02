<script setup lang="ts">
import {ref,onUnmounted,computed,nextTick} from 'vue';
interface Place{id:number;name:string;description:string;mapX:number|null;mapY:number|null;mapWidth:number|null;mapHeight:number|null;commentCount:number}
defineProps<{places:Place[]}>();
const emit=defineEmits<{enter:[place:Place]}>();
const modal=ref<HTMLDialogElement>(),scale=ref(1),x=ref(0),y=ref(0),active=ref<Place|null>(null),dragging=ref(false);
const viewport=ref<HTMLElement>(),viewWidth=ref(1),viewHeight=ref(1);
const baseWidth=computed(()=>Math.min(viewWidth.value,viewHeight.value*8410/11890));
const mapWidth=computed(()=>baseWidth.value*scale.value);
const mapHeight=computed(()=>mapWidth.value*11890/8410);
let resizeObserver:ResizeObserver|undefined;
let startX=0,startY=0,originX=0,originY=0,moved=false;
function reset(){scale.value=1;x.value=0;y.value=0;active.value=null;}
async function open(){reset();modal.value?.showModal();await nextTick();resizeObserver?.disconnect();resizeObserver=new ResizeObserver(()=>{if(viewport.value){viewWidth.value=viewport.value.clientWidth;viewHeight.value=viewport.value.clientHeight;constrain();}});if(viewport.value)resizeObserver.observe(viewport.value);}
function close(){modal.value?.close();active.value=null;dragging.value=false;}
function constrain(){const limitX=Math.max(0,(mapWidth.value-viewWidth.value)/2),limitY=Math.max(0,(mapHeight.value-viewHeight.value)/2);x.value=Math.max(-limitX,Math.min(limitX,x.value));y.value=Math.max(-limitY,Math.min(limitY,y.value));}
function zoom(value:number,event?:WheelEvent){const old=scale.value;scale.value=Math.max(1,Math.min(24,value));const rect=viewport.value?.getBoundingClientRect();const anchorX=event&&rect?event.clientX-rect.left-rect.width/2:0,anchorY=event&&rect?event.clientY-rect.top-rect.height/2:0;x.value=anchorX-(anchorX-x.value)*scale.value/old;y.value=anchorY-(anchorY-y.value)*scale.value/old;constrain();active.value=null;}
function actualPixels(){zoom(8410/(window.devicePixelRatio||1)/baseWidth.value);}
function down(e:PointerEvent){if((e.target as HTMLElement).closest('button'))return;startX=e.clientX;startY=e.clientY;originX=x.value;originY=y.value;moved=false;dragging.value=true;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);}
function move(e:PointerEvent){if(!dragging.value)return;const dx=e.clientX-startX,dy=e.clientY-startY;if(Math.hypot(dx,dy)>5)moved=true;x.value=originX+dx;y.value=originY+dy;constrain();}
function select(p:Place){if(moved){moved=false;return;}active.value=p;}
function enter(){if(active.value){const p=active.value;close();emit('enter',p);}}
onUnmounted(()=>{resizeObserver?.disconnect();close();});defineExpose({open});
</script>
<template>
<Teleport to="body"><dialog ref="modal" class="campus-atlas" aria-label="山海校园全屏地图" @close="active=null">
  <div class="atlas-glow"></div><div class="atlas-orbit orbit-one"></div><div class="atlas-orbit orbit-two"></div>
  <header class="atlas-header"><div><span>SHANDONG UNIVERSITY · QINGDAO</span><h2>山海之间 · 校园舆图</h2></div><button @click="close" aria-label="关闭全屏地图">关闭 ✕</button></header>
  <div ref="viewport" class="atlas-viewport" @wheel.prevent="zoom(scale*Math.exp(-$event.deltaY*.002),$event)" @pointerdown="down" @pointermove="move" @pointerup="dragging=false" @pointercancel="dragging=false" :class="{dragging}">
    <div class="atlas-sheet" :style="{width:mapWidth+'px',height:mapHeight+'px',transform:`translate(${x}px,${y}px)`}">
      <img src="/assets/campus/qingdao-campus.jpg" alt="山东大学青岛校区建筑规划地图" draggable="false">
      <button v-for="p in places" :key="p.id" class="atlas-hotspot" :class="{selected:active?.id===p.id}" :style="{left:p.mapX+'%',top:p.mapY+'%',width:p.mapWidth+'%',height:p.mapHeight+'%'}" :aria-label="p.name" @mouseenter="active=p" @focus="active=p" @click="select(p)"></button>
    </div>
  </div>
  <div class="atlas-compass" aria-hidden="true"><span>北</span>✧</div>
  <section v-if="active" class="atlas-place" aria-live="polite"><small>校园足迹 / CAMPUS STORIES</small><h3>{{active.name}}</h3><p>{{active.commentCount}} 条讨论 · 每个地点都有故事</p><button @click="enter">进入地点讨论 →</button></section>
  <footer class="atlas-footer"><span>拖动探索 · 滚轮缩放 · 原图细节查看建筑小字</span><div><button @click="zoom(scale/1.5)" :disabled="scale<=1" aria-label="缩小">−</button><span>{{Math.round(scale*100)}}%</span><button @click="zoom(scale*1.5)" :disabled="scale>=24" aria-label="放大">＋</button><button @click="actualPixels">原图细节</button><button @click="reset">全图</button></div></footer>
</dialog></Teleport>
</template>
<style scoped>
.campus-atlas{position:fixed;inset:0;width:100vw;height:100dvh;max-width:none;max-height:none;margin:0;padding:0;border:0;background:#101f29;color:#f4e5c5;overflow:hidden;isolation:isolate;animation:atlas-arrive .85s cubic-bezier(.16,1,.3,1)}
.campus-atlas::backdrop{background:#08141d}.atlas-glow{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 50% 40%,#3f77775c,transparent 65%),radial-gradient(ellipse at bottom,#99805b33,transparent 70%);box-shadow:inset 0 0 140px #040d18}
.atlas-orbit{position:absolute;width:85vmin;height:85vmin;border:1px solid #cfb77a20;border-radius:50%;left:calc(50% - 42.5vmin);top:calc(50% - 42.5vmin);pointer-events:none}.orbit-one:after{content:'';position:absolute;inset:24px;border:1px dashed #cfb77a30;border-radius:50%}.orbit-two{transform:scale(1.45)}
.atlas-header{position:absolute;z-index:3;top:0;left:0;right:0;padding:24px 36px;display:flex;justify-content:space-between;align-items:center;background:linear-gradient(#101f29f0,transparent);pointer-events:none}.atlas-header button{pointer-events:auto}.atlas-header span{font-size:10px;letter-spacing:4px;color:#c2ac7c}.atlas-header h2{font-family:serif;font-size:27px;letter-spacing:5px;margin:10px 0;text-shadow:0 2px 20px #dfbd7470}
button{font:inherit;cursor:pointer;border:1px solid #c2ac7c66;color:#f4e5c5;background:#1c333be8;border-radius:4px;padding:10px 17px}button:hover{background:#476166}button:focus-visible{outline:2px solid #ffe2a0;outline-offset:3px}button:disabled{opacity:.35;cursor:default}
.atlas-viewport{position:absolute;inset:110px 16px 90px;display:flex;align-items:center;justify-content:center;cursor:grab;touch-action:none;overflow:hidden}.atlas-viewport.dragging{cursor:grabbing}.atlas-sheet{position:relative;flex-shrink:0;box-shadow:0 0 0 1px #d9bc7780,0 0 35px #bfa97240,0 25px 70px #0009;animation:map-unfold 1.2s cubic-bezier(.16,1,.3,1)}.atlas-sheet>img{width:100%;height:100%;display:block;user-select:none}.atlas-hotspot{position:absolute;padding:0;background:transparent;border:1px solid transparent;border-radius:2px}.atlas-hotspot:hover,.atlas-hotspot.selected,.atlas-hotspot:focus-visible{background:#ffcb4d45;border-color:#dba738;box-shadow:0 0 12px #f6c35d99}
.atlas-compass{position:absolute;top:140px;right:45px;font-size:70px;color:#d6bb7f;pointer-events:none;filter:drop-shadow(0 0 14px #e6bf6655)}.atlas-compass span{display:block;text-align:center;font-size:12px;letter-spacing:2px}.atlas-place{position:absolute;right:30px;bottom:110px;width:280px;padding:24px;background:linear-gradient(135deg,#243c43f5,#142630f5);border:1px solid #bc9e646b;box-shadow:0 16px 55px #0005;animation:card-arrive .2s ease-out}.atlas-place small{font-size:9px;letter-spacing:2px;color:#c6b082}.atlas-place h3{font-family:serif;font-size:23px;margin:16px 0}.atlas-place p{color:#b1bfba;font-size:12px;line-height:1.8}.atlas-place button{width:100%;margin-top:8px;background:#d5c097;color:#172e35}
.atlas-footer{position:absolute;bottom:0;left:0;right:0;display:flex;justify-content:space-between;align-items:center;gap:16px;padding:22px 36px;background:linear-gradient(transparent,#101f29);font-size:12px;color:#bac6c0}.atlas-footer>div{display:flex;align-items:center;gap:14px}.atlas-footer>div>span{min-width:42px;text-align:center}
@keyframes atlas-arrive{from{opacity:0}to{opacity:1}}@keyframes map-unfold{from{opacity:0;translate:0 35px}to{opacity:1;translate:0 0}}@keyframes card-arrive{from{opacity:0;translate:0 8px}to{opacity:1;translate:0 0}}
@media(max-width:700px){.atlas-header{padding:18px}.atlas-header h2{font-size:18px;letter-spacing:2px}.atlas-header span{font-size:8px;letter-spacing:1px}.atlas-compass{right:20px;top:110px;font-size:45px}.atlas-place{right:14px;bottom:100px;width:220px;padding:16px}.atlas-footer{padding:16px;flex-wrap:wrap}.atlas-footer>span{font-size:10px}.atlas-viewport{inset:95px 10px 120px}}
@media(prefers-reduced-motion:reduce){.campus-atlas,.atlas-sheet,.atlas-place{animation:none}}
</style>
