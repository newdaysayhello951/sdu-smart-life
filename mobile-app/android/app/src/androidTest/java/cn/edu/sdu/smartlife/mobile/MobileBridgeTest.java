package cn.edu.sdu.smartlife.mobile;

import android.app.Instrumentation;
import android.content.Intent;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import static org.junit.Assert.*;

/** Real WebView/native HTTP integration. Requires adb reverse tcp:18080 tcp:18080 and the disposable QA backend. */
@RunWith(AndroidJUnit4.class)
public class MobileBridgeTest {
    private MainActivity activity;
    private final Instrumentation instrumentation = InstrumentationRegistry.getInstrumentation();
    private String js(String script) throws Exception {
        CompletableFuture<String> result = new CompletableFuture<>();
        instrumentation.runOnMainSync(() -> activity.getBridge().getWebView().evaluateJavascript(script, result::complete));
        return result.get(10, TimeUnit.SECONDS);
    }
    private void until(String predicate) throws Exception {
        long deadline = System.currentTimeMillis() + 45000;
        while (System.currentTimeMillis() < deadline) { if ("true".equals(js(predicate))) return; Thread.sleep(150); }
        fail("WebView condition did not complete: " + predicate + "; " + js("document.body.innerText.slice(-1600)"));
    }

    @Test public void nativeSessionUploadsImagesAndRealtime() throws Exception {
        // The test has no configurable production URL: all traffic stays on the QA port.
        activity = (MainActivity) instrumentation.startActivitySync(new Intent(instrumentation.getTargetContext(), MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
        try {
            until("!!document.querySelector('.mobile-auth,.mobile-settings')");
            js("window.qaBootstrap='old';localStorage.setItem('campus-server','http://127.0.0.1:18080');location.reload();true");
            until("window.qaBootstrap===undefined&&!!document.querySelector('.mobile-auth input[autocomplete=username]')");
            js("window.qaState='starting';window.qaUser='mobile_bridge_'+Date.now();(async()=>{let r=await fetch('/api/auth/csrf');let t=(await r.json()).token;r=await fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json','X-XSRF-TOKEN':t},body:JSON.stringify({username:window.qaUser,password:'QA_mobile_bridge_12345'})});if(r.status!==201)throw Error('register '+r.status);window.qaState='registered';})().catch(e=>window.qaState='ERROR '+e.message);true");
            until("window.qaState==='registered'||String(window.qaState).startsWith('ERROR')");
            assertEquals("\"registered\"",js("window.qaState"));
            js("let f=document.querySelector('.mobile-auth form');let u=f.querySelector('input[autocomplete=username]'),p=f.querySelector('input[type=password]');u.value=window.qaUser;u.dispatchEvent(new Event('input',{bubbles:true}));p.value='QA_mobile_bridge_12345';p.dispatchEvent(new Event('input',{bubbles:true}));f.requestSubmit();true");
            until("!!document.querySelector('.mobile-header')");
            js("location.hash='/my/products';true");
            until("!!document.querySelector('.mobile-account img')&&document.querySelector('.mobile-account img').naturalWidth>0");
            js("window.qaState='uploading';(async()=>{let t=(await(await fetch('/api/auth/csrf')).json()).token;let c=document.createElement('canvas');c.width=32;c.height=32;c.getContext('2d').fillRect(0,0,32,32);let blob=await new Promise(r=>c.toBlob(r,'image/png'));let form=new FormData();form.append('product',new Blob([JSON.stringify({title:'Mobile native QA',description:'Independent emulator verification',price:10,location:'QA only',kind:'SELL'})],{type:'application/json'}));form.append('file',blob,'qa.png');let r=await fetch('/api/my/products/publish',{method:'POST',headers:{'X-XSRF-TOKEN':t},body:form});if(r.status!==201)throw Error('upload '+r.status);window.qaState='uploaded';})().catch(e=>window.qaState='ERROR '+e.message);true");
            until("window.qaState==='uploaded'||String(window.qaState).startsWith('ERROR')");
            assertEquals("\"uploaded\"",js("window.qaState"));
            js("window.qaState='connecting';window.qaSource=new EventSource('/api/events');window.qaSource.addEventListener('ready',()=>{window.qaState='realtime';window.qaSource.close();});true");
            until("window.qaState==='realtime'");
            js("document.querySelector('.mobile-account button').click();true");
            until("!!document.querySelector('.mobile-auth')");
            js("window.qaState='checking';fetch('/api/auth/me').then(r=>window.qaState='status '+r.status);true");
            until("window.qaState==='status 401'");
        } finally { instrumentation.runOnMainSync(() -> activity.finish()); }
    }
}
