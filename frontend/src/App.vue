<script setup lang="ts">
import { ref } from 'vue';
const notice = ref('');
function openSection(name: string) { notice.value = `${name}正在迁移，完成后即可使用。`; }
</script>

<template>
 <main class="landing">
  <header class="navigation">
   <a class="brand" href="/" aria-label="智慧校园首页"><span class="brand-mark">山大</span><span>智慧校园<small>SDU SMART LIFE</small></span></a>
   <nav aria-label="主导航"><a href="/" class="active">首页</a><button @click="openSection('二手市场')">二手市场</button><button @click="openSection('校园地图')">校园地图</button><button @click="openSection('个人主页')">个人主页</button></nav>
   <button class="account" @click="openSection('登录功能')"><img src="/assets/legacy/picture/th1.jpg" alt="">登录 / 注册</button>
  </header>
  <section class="welcome">
   <p class="eyebrow"><span></span> SHANDONG UNIVERSITY · CAMPUS LIFE</p>
   <h1>在山大，<br>遇见生活的<span>更多可能。</span></h1>
   <p class="intro">让闲置好物继续陪伴，让熟悉的校园有新的发现。<br>你我的校园日常，在这里相连。</p>
   <div class="actions"><button class="primary" @click="openSection('二手市场')">逛逛二手市场 <span>↗</span></button><button class="secondary" @click="openSection('校园地图')">探索校园 <span>→</span></button></div>
  </section>
  <footer><div><span class="location-dot"></span>中国 · 山东大学<small>每一份热爱，都值得在这里相遇</small></div><span class="footer-note">SDU SMART LIFE <i> / </i> 让校园生活更有温度</span></footer>
  <div v-if="notice" class="notice" role="status">{{ notice }}<button aria-label="关闭提示" @click="notice = ''">×</button></div>
 </main>
</template>

<style>

*{box-sizing:border-box}body{margin:0;font-family:"Microsoft YaHei","PingFang SC",sans-serif;background:#18232b}button,a{-webkit-tap-highlight-color:transparent}button{font:inherit;cursor:pointer}button:focus-visible,a:focus-visible{outline:2px solid #edc990;outline-offset:6px}.landing{position:relative;isolation:isolate;min-height:100svh;color:#fff;display:flex;flex-direction:column;background:url('/assets/legacy/images/sdu.jpg') center center/cover no-repeat}.landing:before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(90deg,rgba(12,23,32,.76) 0%,rgba(12,23,32,.36) 55%,rgba(12,23,32,.12)),linear-gradient(0deg,rgba(7,18,28,.75),transparent 35%,transparent 75%,rgba(7,18,28,.4))}.navigation{height:106px;margin:0 5%;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #ffffff30;gap:25px}.brand{display:flex;align-items:center;gap:13px;text-decoration:none;color:white;font-size:22px;letter-spacing:3px;font-weight:600;white-space:nowrap}.brand-mark{display:grid;place-items:center;width:49px;height:49px;border:1px solid #ffffff80;border-radius:50%;font-family:serif;font-size:18px;letter-spacing:2px}.brand small{display:block;font-size:9px;letter-spacing:2px;font-weight:400;margin-top:7px;color:#ffffffb0}nav{display:flex;gap:36px;height:100%;align-items:center}nav a,nav button{position:relative;color:#ffffffe0;text-decoration:none;border:0;background:none;font-size:14px;padding:15px 0}nav .active:after{content:"";position:absolute;bottom:0;left:calc(50% - 10px);width:20px;height:2px;background:#efcf99}nav button:hover{color:#efcf99}.account{display:flex;align-items:center;gap:10px;background:none;border:0;color:white;font-size:13px;white-space:nowrap}.account img{width:30px;height:30px;border-radius:50%;object-fit:cover;border:1px solid #ffffff70}.welcome{width:90%;margin:auto; padding:75px 0 90px}.eyebrow{font-size:11px;letter-spacing:3px;color:#f0d5ac;display:flex;align-items:center;gap:14px}.eyebrow>span{height:1px;width:34px;background:#d9b789}h1{font-size:clamp(42px,4.6vw,72px);font-weight:500;line-height:1.4;letter-spacing:3px;margin:27px 0 24px;text-shadow:0 2px 25px #0002}h1 span{color:#f1d3a5}.intro{font-size:15px;line-height:2.1;color:#ffffffe0;letter-spacing:1px}.actions{display:flex;gap:16px;margin-top:38px}.actions button{height:49px;padding:0 25px;border-radius:3px;font-size:14px;letter-spacing:1px}.actions span{margin-left:30px}.primary{background:#eed4ac;border:1px solid #eed4ac;color:#28323a}.primary:hover{background:#f9e4c5}.secondary{background:#ffffff0a;border:1px solid #ffffff70;color:white;backdrop-filter:blur(6px)}.secondary:hover{background:#ffffff20}footer{margin:0 5%;padding:24px 0 27px;border-top:1px solid #ffffff30;display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#ffffffe0;letter-spacing:1px}footer small{margin-left:24px;color:#ffffff8c;font-size:11px}.location-dot{display:inline-block;width:6px;height:6px;background:#e9c795;border-radius:50%;margin-right:10px}.footer-note{font-size:10px;color:#ffffff9c;letter-spacing:2px}.footer-note i{margin:0 12px;font-style:normal;color:#e9c795}.notice{position:fixed;bottom:95px;left:50%;transform:translateX(-50%);background:#fff;color:#293744;padding:16px 20px;border-radius:6px;box-shadow:0 8px 35px #0003;display:flex;gap:20px;align-items:center;font-size:14px;max-width:90%;z-index:10}.notice button{border:0;background:none;font-size:22px;color:#61707a}@media(min-width:1700px){.welcome{padding-left:4%}}@media(max-width:850px){.navigation{height:90px;flex-wrap:wrap;padding:15px 0;gap:10px}.brand{font-size:18px}.brand-mark{width:38px;height:38px}nav{order:3;width:100%;height:auto;justify-content:center;gap:25px}nav a,nav button{font-size:12px;padding:5px 0}.navigation{height:125px}.welcome{padding:60px 0}.eyebrow{font-size:9px;letter-spacing:1.5px}h1{font-size:42px;letter-spacing:1px}.intro{font-size:13px}.actions button{padding:0 15px;font-size:12px}.actions span{margin-left:12px}.footer-note,footer small{display:none}footer{font-size:11px}.landing{background-position:58% center}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
</style>

