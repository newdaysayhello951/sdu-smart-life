import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import { createRouter, createWebHistory } from 'vue-router';
import Market from './Market.vue';
import Campus from './Campus.vue';
import MyProducts from './MyProducts.vue';
const router = createRouter({history:createWebHistory(),routes:[{path:'/campus',component:Campus},{path:'/my/products',component:MyProducts},{path:'/',component:{template:'<div />'}},{path:'/market',component:Market},{path:'/market/:id(\\d+)',component:Market}]});
createApp(App).use(createPinia()).use(router).mount('#app');
