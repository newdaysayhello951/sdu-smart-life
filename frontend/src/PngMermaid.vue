<script setup lang="ts">
import {ref,onMounted,onUnmounted} from 'vue';
const ready=ref(false);
const canvas=ref<HTMLCanvasElement|null>(null);let frame=0,dead=false,gl:WebGLRenderingContext|null=null;
onMounted(()=>{
 const el=canvas.value!;gl=el.getContext('webgl',{alpha:true,premultipliedAlpha:false,antialias:true});if(!gl)return;const g=gl;
 function shader(type:number,source:string){const s=g.createShader(type)!;g.shaderSource(s,source);g.compileShader(s);if(!g.getShaderParameter(s,g.COMPILE_STATUS))throw new Error('角色网格着色器编译失败');return s;}
 const vs=shader(g.VERTEX_SHADER,`attribute vec2 a;varying vec2 uv;uniform float time;uniform float motion;
 void main(){uv=a;vec2 p=a;
 float tail=smoothstep(.61,.95,a.y);float hair=(1.-smoothstep(.43,.62,a.y))*smoothstep(.19,.39,abs(a.x-.5));
 float arm=exp(-pow((a.x-.33)/.12,2.)-pow((a.y-.47)/.10,2.));
 p.x+=motion*(tail*(.024*sin(time*2.3-a.y*7.)+.008*sin(time*3.7-a.y*11.))+hair*.009*sin(time*1.7+a.y*8.)+arm*.009*sin(time*2.));
 p.y+=motion*(tail*.008*sin(time*2.3-a.y*7.+1.2)+hair*.005*sin(time*1.7+a.x*9.)+arm*.007*sin(time*2.+.8));
 gl_Position=vec4(p.x*2.-1.,1.-p.y*2.,0.,1.);}`);
 const fs=shader(g.FRAGMENT_SHADER,`precision mediump float;varying vec2 uv;uniform sampler2D image;void main(){gl_FragColor=texture2D(image,uv);}`);
 const program=g.createProgram()!;g.attachShader(program,vs);g.attachShader(program,fs);g.linkProgram(program);g.useProgram(program);
 const vertices:number[]=[];const cols=36,rows=48;
 for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){const l=x/cols,r=(x+1)/cols,t=y/rows,b=(y+1)/rows;vertices.push(l,t,r,t,l,b,r,t,r,b,l,b);}
 const buffer=g.createBuffer();g.bindBuffer(g.ARRAY_BUFFER,buffer);g.bufferData(g.ARRAY_BUFFER,new Float32Array(vertices),g.STATIC_DRAW);const loc=g.getAttribLocation(program,'a');g.enableVertexAttribArray(loc);g.vertexAttribPointer(loc,2,g.FLOAT,false,0,0);
 const image=new Image();image.src='/assets/assistant/sea-sprite-clean.png';image.onload=()=>{if(dead)return;
 const texture=g.createTexture();g.bindTexture(g.TEXTURE_2D,texture);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_S,g.CLAMP_TO_EDGE);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_T,g.CLAMP_TO_EDGE);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MIN_FILTER,g.LINEAR);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MAG_FILTER,g.LINEAR);g.texImage2D(g.TEXTURE_2D,0,g.RGBA,g.RGBA,g.UNSIGNED_BYTE,image);
 ready.value=true;const t=g.getUniformLocation(program,'time'),m=g.getUniformLocation(program,'motion');const start=performance.now();const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
 function draw(now:number){if(dead)return;const paused=el.closest('.dragging')!==null;g.viewport(0,0,el.width,el.height);g.clearColor(0,0,0,0);g.clear(g.COLOR_BUFFER_BIT);g.uniform1f(t,(now-start)/1000);g.uniform1f(m,reduced.matches||paused?0:1);g.drawArrays(g.TRIANGLES,0,vertices.length/2);frame=requestAnimationFrame(draw);}frame=requestAnimationFrame(draw);
 };
});
onUnmounted(()=>{dead=true;cancelAnimationFrame(frame);gl?.getExtension('WEBGL_lose_context')?.loseContext();});
</script>
<template><span class="png-rig"><img v-if="!ready" src="/assets/assistant/sea-sprite-clean.png" alt="汐月人鱼"><canvas ref="canvas" width="456" height="600" aria-label="PNG人鱼发梢与鱼尾网格动画"/></span></template>
<style scoped>.png-rig{display:block;width:100%;height:100%;position:relative}.png-rig img,.png-rig canvas{position:absolute;inset:0;width:100%;height:100%;object-fit:fill}.png-rig canvas{pointer-events:none}.png-rig img{z-index:-1}</style>
