package cn.edu.sdu.smartlife.mobile;

import android.content.pm.ApplicationInfo;
import android.webkit.CookieManager;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

/** Streams only the two campus SSE endpoints, using the same cookie jar as native HTTP. */
@CapacitorPlugin(name = "CampusStream")
public class CampusStreamPlugin extends Plugin {
    private final ExecutorService workers = Executors.newFixedThreadPool(2);
    private final ConcurrentHashMap<String, Connection> connections = new ConcurrentHashMap<>();
    private static class Connection {
        volatile boolean cancelled;
        volatile HttpURLConnection http;
        void close() { cancelled = true; if (http != null) http.disconnect(); }
    }

    @PluginMethod
    public synchronized void start(PluginCall call) {
        String id = call.getString("id"), origin = call.getString("origin", ""), path = call.getString("path", "");
        String method = call.getString("method", "GET");
        try {
            URI base = URI.create(origin);
            String host = base.getHost();
            boolean debug = (getContext().getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0;
            boolean local = host != null && (host.equals("localhost") || host.equals("127.0.0.1") || host.matches("10\\.\\d+\\.\\d+\\.\\d+|192\\.168\\.\\d+\\.\\d+|172\\.(1[6-9]|2\\d|3[01])\\.\\d+\\.\\d+"));
            if (host == null || base.getUserInfo() != null || base.getRawQuery() != null || base.getRawFragment() != null || !(base.getPath().isEmpty() || base.getPath().equals("/")) || !("https".equals(base.getScheme()) || debug && local && "http".equals(base.getScheme()))) throw new IllegalArgumentException();
            if (!(path.equals("/api/events") && method.equals("GET") || path.equals("/api/assistant/ask") && method.equals("POST"))) throw new IllegalArgumentException();
            String body = call.getString("body", "");
            if (id == null || id.length() > 80 || connections.containsKey(id) || connections.size() >= 2 || body.length() > 10000) throw new IllegalArgumentException();
            JSObject headers = call.getObject("headers", new JSObject());
            Connection state = new Connection(); connections.put(id, state);
            String url = base.resolve(path).toString();
            workers.execute(() -> runStream(id, state, url, method, headers, body));
            call.resolve();
        } catch (Exception e) { call.reject("校园实时连接配置无效或连接过多"); }
    }

    private void event(String id, String type, String text, int status) {
        JSObject data = new JSObject(); data.put("id", id); data.put("type", type);
        if (text != null) data.put("text", text);
        if (status > 0) data.put("status", status);
        notifyListeners("stream", data);
    }

    private void runStream(String id, Connection state, String url, String method, JSObject headers, String body) {
        try {
            if (state.cancelled) return;
            HttpURLConnection http = (HttpURLConnection) URI.create(url).toURL().openConnection();
            state.http = http; if (state.cancelled) return;
            http.setConnectTimeout(12000); http.setReadTimeout(65000); http.setInstanceFollowRedirects(false);
            http.setRequestMethod(method); http.setRequestProperty("Accept", "text/event-stream");
            String cookie = CookieManager.getInstance().getCookie(url);
            if (cookie != null) http.setRequestProperty("Cookie", cookie);
            String token = headers.optString("x-xsrf-token", headers.optString("X-XSRF-TOKEN", ""));
            if (!token.isEmpty()) http.setRequestProperty("X-XSRF-TOKEN", token);
            if (method.equals("POST")) {
                http.setDoOutput(true); http.setRequestProperty("Content-Type", "application/json");
                try (var out = http.getOutputStream()) { out.write(body.getBytes(StandardCharsets.UTF_8)); }
            }
            int status = http.getResponseCode();
            if (state.cancelled) return;
            event(id, "open", null, status);
            if (status < 200 || status >= 300) { event(id, "end", null, 0); return; }
            String type = http.getContentType();
            if (type == null || !type.startsWith("text/event-stream")) throw new IllegalArgumentException();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(http.getInputStream(), StandardCharsets.UTF_8))) {
                String line; StringBuilder block = new StringBuilder();
                while (!state.cancelled && (line = reader.readLine()) != null) {
                    if (line.length() > 131072 || block.length() > 262144) throw new IllegalArgumentException();
                    block.append(line).append('\n');
                    if (line.isEmpty()) { event(id, "chunk", block.toString(), 0); block.setLength(0); }
                }
                if (!state.cancelled && block.length() > 0) event(id, "chunk", block.toString(), 0);
            }
            if (!state.cancelled) event(id, "end", null, 0);
        } catch (Exception e) { if (!state.cancelled) event(id, "error", null, 0); }
        finally { state.close(); connections.remove(id, state); }
    }

    @PluginMethod
    public void stop(PluginCall call) {
        String id = call.getString("id");
        if (id != null) { Connection state = connections.remove(id); if (state != null) state.close(); }
        call.resolve();
    }

    @Override protected void handleOnPause() {
        for (var entry : connections.entrySet()) { event(entry.getKey(), "end", null, 0); entry.getValue().close(); }
        connections.clear();
    }
    @Override protected void handleOnDestroy() { handleOnPause(); workers.shutdownNow(); }
}
