import type {CapacitorConfig} from '@capacitor/cli';
const config:CapacitorConfig={
  appId:'cn.edu.sdu.smartlife.mobile',appName:'山海校园',webDir:'dist',
  android:{backgroundColor:'#f6f4ee',allowMixedContent:false},
  plugins:{CapacitorHttp:{enabled:true},CapacitorCookies:{enabled:true}},
};
export default config;
