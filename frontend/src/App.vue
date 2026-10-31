<script setup lang="ts">
import { onMounted, ref } from 'vue';
import axios from 'axios';
const status = ref('正在连接 Java 服务…');
onMounted(async () => {
 try { const { data } = await axios.get('/api/platform'); status.value = data.message; }
 catch { status.value = 'Java 服务暂未连接，请启动后端'; }
});
</script>
<template>
 <header><a class="brand" href="/">SDU · 智慧校园</a><span>校园生活，从这里连接</span></header>
 <main><section class="hero"><p class="eyebrow">SMART CAMPUS / SMART LIFE</p><h1>让校园里的好物<br>与生活相遇。</h1><p>延续熟悉的校园风景，连接二手好物、校园地点与同学们的日常。</p><div class="status">{{ status }}</div></section>
 <section class="modules"><article><span>01 / MARKET</span><h2>校园二手市场</h2><p>闲置流转，让每件好物找到新的主人。</p><small>商品功能迁移中</small></article><article><span>02 / CAMPUS</span><h2>探索校园</h2><p>熟悉的地点，新的故事与交流。</p><small>地图功能迁移中</small></article><article><span>03 / COMMUNITY</span><h2>我的校园生活</h2><p>管理发布、求购与交易记录。</p><small>用户功能迁移中</small></article></section>
 </main><footer>SDU Smart Life · Vue 3 + Spring Boot</footer>
</template>
<style>
*{box-sizing:border-box}body{margin:0;background:#f7f5ef;color:#243a34;font-family:"Microsoft YaHei",sans-serif}header{height:84px;display:flex;align-items:center;justify-content:space-between;max-width:1200px;margin:auto;padding:0 28px}.brand{font-size:23px;font-weight:700;text-decoration:none;color:inherit}header span{font-size:13px;color:#6a7971}main{max-width:1200px;margin:auto;padding:0 28px}.hero{padding:80px 54px;border-radius:24px;background:linear-gradient(90deg,rgba(238,243,225,.97),rgba(238,243,225,.65)),url('/assets/legacy/images/bg.jpg') center/cover}.eyebrow{letter-spacing:3px;font-size:12px}h1{font-size:54px;line-height:1.35;margin:25px 0}.hero>p:not(.eyebrow){line-height:1.9;max-width:540px}.status{display:inline-block;margin-top:24px;padding:12px 20px;background:#264f42;color:white;border-radius:8px;font-size:13px}.modules{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin:32px 0}article{padding:30px;background:white;border:1px solid #e6e9df;border-radius:16px}article>span{font-size:11px;letter-spacing:2px;color:#7d8e77}article p{font-size:14px;line-height:1.8;color:#68776e}small{color:#8b7960}footer{text-align:center;padding:25px;color:#7c877e;font-size:12px}@media(max-width:700px){header span{display:none}.hero{padding:40px 24px}h1{font-size:36px}.modules{grid-template-columns:1fr}}
</style>
