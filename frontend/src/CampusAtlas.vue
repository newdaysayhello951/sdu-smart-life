<script setup lang="ts">
import {ref,onUnmounted,nextTick} from 'vue';
import CampusMapSurface from './CampusMapSurface.vue';
interface Place{id:number;name:string;description:string;mapX:number|null;mapY:number|null;mapWidth:number|null;mapHeight:number|null;commentCount:number}
defineProps<{places:Place[]}>();
const emit=defineEmits<{enter:[place:Place]}>();
const modal=ref<HTMLDialogElement>(),surface=ref<InstanceType<typeof CampusMapSurface>>(),scale=ref(1),active=ref<Place|null>(null),opened=ref(false);
async function open(){active.value=null;scale.value=1;opened.value=true;modal.value?.showModal();await nextTick();surface.value?.reset();}
function closed(){opened.value=false;active.value=null;}
function close(){modal.value?.close();closed();}
function enter(){if(active.value){const p=active.value;close();emit('enter',p);}}
onUnmounted(close);defineExpose({open});
</script>
<template>
<Teleport to="body"><dialog ref="modal" class="campus-atlas" aria-label="山海校园全屏地图" @close="closed">
  <div class="atlas-glow"></div><div class="atlas-orbit orbit-one"></div><div class="atlas-orbit orbit-two"></div>
  <header class="atlas-header"><div><span>SHANDONG UNIVERSITY · QINGDAO</span><h2>山海之间 · 校园舆图</h2></div><button @click="close" aria-label="关闭全屏地图">关闭 ✕</button></header>
  <CampusMapSurface v-if="opened" ref="surface" :places="places" :active-id="active?.id" @select="active=$event" @zoom="scale=$event"/>
  <div class="atlas-compass" aria-hidden="true"><span>北</span>✧</div>
  <section v-if="active" class="atlas-place" aria-live="polite"><small>校园足迹 / CAMPUS STORIES</small><h3>{{active.name}}</h3><p>{{active.commentCount}} 条讨论 · 每个地点都有故事</p><button @click="enter">进入地点讨论 →</button></section>
  <footer class="atlas-footer"><span>拖动探索 · 滚轮缩放 · 原图细节查看建筑小字</span><div><button @click="surface?.zoom(scale/1.5)" :disabled="scale<=1" aria-label="缩小">−</button><span>{{Math.round(scale*100)}}%</span><button @click="surface?.zoom(scale*1.5)" :disabled="scale>=24" aria-label="放大">＋</button><button @click="surface?.actualPixels()">原图细节</button><button @click="surface?.reset();active=null">全图</button></div></footer>
</dialog></Teleport>
</template>
<style scoped>
.campus-atlas{position:fixed;inset:0;width:100vw;height:100dvh;max-width:none;max-height:none;margin:0;padding:0;border:0;background:#101f29;color:#f4e5c5;overflow:hidden;isolation:isolate;animation:atlas-arrive .85s cubic-bezier(.16,1,.3,1)}
.campus-atlas::backdrop{background:#08141d}.atlas-glow{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 50% 40%,#3f77775c,transparent 65%),radial-gradient(ellipse at bottom,#99805b33,transparent 70%);box-shadow:inset 0 0 140px #040d18}
.atlas-orbit{position:absolute;width:85vmin;height:85vmin;border:1px solid #cfb77a20;border-radius:50%;left:calc(50% - 42.5vmin);top:calc(50% - 42.5vmin);pointer-events:none}.orbit-one:after{content:'';position:absolute;inset:24px;border:1px dashed #cfb77a30;border-radius:50%}.orbit-two{transform:scale(1.45)}
.atlas-header{position:absolute;z-index:3;top:0;left:0;right:0;padding:24px 36px;display:flex;justify-content:space-between;align-items:center;background:linear-gradient(#101f29f0,transparent);pointer-events:none}.atlas-header button{pointer-events:auto}.atlas-header span{font-size:10px;letter-spacing:4px;color:#c2ac7c}.atlas-header h2{font-family:serif;font-size:27px;letter-spacing:5px;margin:10px 0;text-shadow:0 2px 20px #dfbd7470}
button{font:inherit;cursor:pointer;border:1px solid #c2ac7c66;color:#f4e5c5;background:#1c333be8;border-radius:4px;padding:10px 17px}button:hover{background:#476166}button:focus-visible{outline:2px solid #ffe2a0;outline-offset:3px}button:disabled{opacity:.35;cursor:default}
.atlas-compass{position:absolute;top:140px;right:45px;font-size:70px;color:#d6bb7f;pointer-events:none;filter:drop-shadow(0 0 14px #e6bf6655)}.atlas-compass span{display:block;text-align:center;font-size:12px;letter-spacing:2px}.atlas-place{position:absolute;right:30px;bottom:110px;width:280px;padding:24px;background:linear-gradient(135deg,#243c43f5,#142630f5);border:1px solid #bc9e646b;box-shadow:0 16px 55px #0005;animation:card-arrive .2s ease-out}.atlas-place small{font-size:9px;letter-spacing:2px;color:#c6b082}.atlas-place h3{font-family:serif;font-size:23px;margin:16px 0}.atlas-place p{color:#b1bfba;font-size:12px;line-height:1.8}.atlas-place button{width:100%;margin-top:8px;background:#d5c097;color:#172e35}
.atlas-footer{position:absolute;bottom:0;left:0;right:0;display:flex;justify-content:space-between;align-items:center;gap:16px;padding:22px 36px;background:linear-gradient(transparent,#101f29);font-size:12px;color:#bac6c0}.atlas-footer>div{display:flex;align-items:center;gap:14px}.atlas-footer>div>span{min-width:42px;text-align:center}
@keyframes atlas-arrive{from{opacity:0}to{opacity:1}}@keyframes card-arrive{from{opacity:0;translate:0 8px}to{opacity:1;translate:0 0}}
@media(max-width:700px){.atlas-header{padding:18px}.atlas-header h2{font-size:18px;letter-spacing:2px}.atlas-header span{font-size:8px;letter-spacing:1px}.atlas-compass{right:20px;top:110px;font-size:45px}.atlas-place{right:14px;bottom:100px;width:220px;padding:16px}.atlas-footer{padding:16px;flex-wrap:wrap}.atlas-footer>span{font-size:10px}}
@media(prefers-reduced-motion:reduce){.campus-atlas,.atlas-place{animation:none}}
</style>
