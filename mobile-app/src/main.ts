import {createApp} from 'vue';
import {createRouter,createWebHashHistory} from 'vue-router';
import {App as NativeApp} from '@capacitor/app';
import App from './App.vue';
import {installTransport,mobileSrc,native} from './transport';
import './mobile.css';
import Market from '../../frontend/src/Market.vue';
import Campus from '../../frontend/src/Campus.vue';
import ConversationPage from '../../frontend/src/ConversationPage.vue';
import MyProducts from '../../frontend/src/MyProducts.vue';
import PublicProfile from '../../frontend/src/PublicProfile.vue';
import Messages from '../../frontend/src/Messages.vue';
import Notifications from '../../frontend/src/Notifications.vue';
installTransport();
const router=createRouter({history:createWebHashHistory(),scrollBehavior:()=>({top:0}),routes:[
 {path:'/',component:{template:'<div />'}},{path:'/market',component:Market},{path:'/market/:id(\\d+)',component:Market},
 {path:'/lost-found',component:Market},{path:'/lost-found/:id(\\d+)',component:Market},{path:'/campus',component:Campus},
 {path:'/campus/:placeId/conversations/:rootId',component:ConversationPage},{path:'/my/products',component:MyProducts},
 {path:'/people/:id',component:PublicProfile},{path:'/notifications',component:Notifications},{path:'/messages',redirect:'/notifications'},
 {path:'/messages/:id',component:Messages},{path:'/:pathMatch(.*)*',redirect:'/'},
]});
createApp(App).provide('campus-listing-page-size',1).use(router).directive('mobile-src',mobileSrc).mount('#app');
document.addEventListener('click',event=>{const link=(event.target as Element)?.closest<HTMLAnchorElement>('a[href]');if(!link)return;const url=new URL(link.href,location.href);if(url.origin===location.origin&&/^\/(market|lost-found|campus|notifications)([/?]|$)/.test(url.pathname)){event.preventDefault();void router.push(url.pathname+url.search);}});
if(native){
 void NativeApp.addListener('backButton',()=>{const dialog=document.querySelector<HTMLDialogElement>('dialog[open]');if(dialog){dialog.dispatchEvent(new Event('cancel',{cancelable:true}))&&dialog.close();return;}const chat=document.querySelector<HTMLButtonElement>('.sea-header button[aria-label="关闭问答弹窗"]');if(chat){chat.click();return;}if(router.currentRoute.value.path!=='/')router.back();else void NativeApp.minimizeApp();});
 void NativeApp.addListener('appStateChange',state=>window.dispatchEvent(new CustomEvent('mobile-app-state',{detail:state.isActive})));
}
