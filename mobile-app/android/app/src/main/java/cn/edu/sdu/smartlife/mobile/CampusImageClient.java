package cn.edu.sdu.smartlife.mobile;
import android.webkit.*;
import android.webkit.CookieManager;
import android.content.pm.ApplicationInfo;
import com.getcapacitor.*;
import java.net.*;
import java.io.*;
import java.util.*;
/** Authenticated binary images stay in WebView/native code, never cross the JS bridge as Base64. */
public final class CampusImageClient extends BridgeWebViewClient {
 private final boolean debug;
 private record Entry(byte[] data,String mime,long at){}
 private final Map<String,Entry> cache=Collections.synchronizedMap(new LinkedHashMap<>());
 public CampusImageClient(Bridge bridge){super(bridge);debug=(bridge.getContext().getApplicationInfo().flags&ApplicationInfo.FLAG_DEBUGGABLE)!=0;}
 private Map<String,String> headers(){var headers=new HashMap<String,String>();headers.put("Cache-Control","no-store");headers.put("X-Content-Type-Options","nosniff");return headers;}
 private WebResourceResponse response(int status,String mime,byte[] bytes){return new WebResourceResponse(mime,null,status,status==200?"OK":"Unavailable",headers(),new ByteArrayInputStream(bytes));}
 @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request){
  var uri=request.getUrl();if(!"localhost".equals(uri.getHost())||!"/_campus-image".equals(uri.getPath()))return super.shouldInterceptRequest(view,request);
  HttpURLConnection http=null;
  try{
   URI origin=URI.create(uri.getQueryParameter("server"));String path=uri.getQueryParameter("path"),host=origin.getHost();
   boolean lan=host!=null&&(host.equals("127.0.0.1")||host.equals("localhost")||host.matches("10\\.\\d+\\.\\d+\\.\\d+|192\\.168\\.\\d+\\.\\d+|172\\.(1[6-9]|2\\d|3[01])\\.\\d+\\.\\d+"));
   if(host==null||origin.getUserInfo()!=null||origin.getQuery()!=null||origin.getFragment()!=null||!(origin.getPath().isEmpty()||origin.getPath().equals("/"))||!("https".equals(origin.getScheme())||debug&&lan&&"http".equals(origin.getScheme())))return response(400,"text/plain",new byte[0]);
   if(path==null||!path.matches("/api/(profile/avatar|conversations/avatars/\\d+|conversations/\\d+/image|images/product/\\d+)(\\?[^\\r\\n\\\\]*)?"))return response(400,"text/plain",new byte[0]);
   String url=origin.resolve(path).toString(),cookie=CookieManager.getInstance().getCookie(url);
   String key=url+"|"+cookie+"|"+uri.getQueryParameter("epoch");
   Entry entry=cache.get(key);if(entry!=null&&System.currentTimeMillis()-entry.at<30000)return response(200,entry.mime,entry.data);
   http=(HttpURLConnection)new URL(url).openConnection();http.setConnectTimeout(10000);http.setReadTimeout(20000);http.setInstanceFollowRedirects(false);if(cookie!=null)http.setRequestProperty("Cookie",cookie);
   int status=http.getResponseCode();if(status!=200)return response(status>=400?status:502,"text/plain",new byte[0]);
   String mime=http.getContentType();if(mime==null||!mime.startsWith("image/"))return response(415,"text/plain",new byte[0]);mime=mime.split(";")[0];
   var out=new ByteArrayOutputStream();try(var in=http.getInputStream()){byte[] block=new byte[16384];int n;while((n=in.read(block))!=-1){out.write(block,0,n);if(out.size()>20*1024*1024)return response(413,"text/plain",new byte[0]);}}
   byte[] data=out.toByteArray();if(data.length<=256*1024){synchronized(cache){cache.put(key,new Entry(data,mime,System.currentTimeMillis()));while(cache.size()>24)cache.remove(cache.keySet().iterator().next());}}
   return response(200,mime,data);
  }catch(Exception e){return response(502,"text/plain",new byte[0]);}finally{if(http!=null)http.disconnect();}
 }
}
