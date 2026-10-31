import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import { createRouter, createWebHistory } from 'vue-router';
import Market from './Market.vue';
const router = createRouter({history:createWebHistory(),routes:[{path:'/',component:{template:'<div />'}},{path:'/market',component:Market},{path:'/market/:id(\\d+)',component:Market}]});
createApp(App).use(createPinia()).use(router).mount('#app');
