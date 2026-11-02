# 山海校园 · 独立手机端

Vue 3 + TypeScript + Vite + Capacitor 7.6.10，Android SDK 35 / Java 21。手机端有独立首页、登录界面、底部导航和样式；通过源码引用共用 `../frontend/src` 的业务组件，继续使用原 Java 后端与数据库。Capacitor 7 与本机已有的 SDK 35、Java 21 配套；不代表需要把 Java 后端降级或另建后端。

## 运行手机网页

先运行项目 Java 服务，再在本目录运行：

```powershell
npm ci
npm run dev
```

电脑访问 `http://127.0.0.1:5174`；同一 Wi-Fi 下手机访问 `http://电脑局域网IP:5174`。Vite 将 `/api` 代理到电脑的 8080，手机浏览器不填写 127.0.0.1 为后端地址。可以通过 `API_PROXY_TARGET` 改变代理目标。开发端口只用于可信局域网测试。

网页生产预览：`npm run build` 后 `npm run preview`。生产 Web 托管需为 `/api` 配置同源 HTTPS 反向代理，开发代理不属于 App 服务部署。

## 构建 Android

要求 Node.js 22、Java 21、Android SDK Platform 35，SDK Build Tools 由 Gradle 按配置解析。设置 `JAVA_HOME`（可用 Android Studio 的 `jbr` 目录）及 `ANDROID_HOME`，然后执行：

```powershell
./scripts/build-android.ps1
```

脚本先检查类型、构建调试网页并同步 Capacitor，再生成 `android/app/build/outputs/apk/debug/app-debug.apk`。可用 `-JavaHome`、`-AndroidSdk` 指定本地路径。可选 `-Proxy http://127.0.0.1:端口` 只影响该次 Gradle 下载，不修改系统设置；`-GradleCommand` 可指定已经安装的 Gradle 8.10.2。Gradle 缓存隔离在仓库 `.tools/mobile-gradle`。Wrapper 固定 8.10.2，并使用官方 SHA-256 校验。

安装调试包后，首次填写校园 Java 服务根地址：

- Android 模拟器：`http://10.0.2.2:8080`。
- 真机：`http://电脑局域网IP:8080`（需要电脑服务和防火墙允许访问，且位于同一网络）。
- 正式服务：自己的 `https://域名`，不要填写示例域名。

USB 调试或模拟器的宿主机地址连接受限时，可执行 `adb reverse tcp:8080 tcp:8080`，再在 App 填写 `http://127.0.0.1:8080`；该地址只在 ADB 映射存在时指向电脑。不要把这项开发连接当作其他同学可访问的服务地址。

只有调试网页构建和 Android debug manifest 允许局域网 HTTP；`npm run android:sync` 与 Release 构建要求 HTTPS。默认 APK 自带页面资源，不使用远程 `server.url` 加载整个网站。服务地址只保存在本机，不保存账号密码、模型密钥或业务数据库。

Release：`./scripts/build-android.ps1 -Configuration Release`，得到的是未签名产物；发布签名、商店审核与系统级后台推送尚未配置。签名文件、APK、构建缓存及复制到 Android 的网页资源均不提交 Git。

## 实现范围

- 首页、登录注册、自己的主页与他人主页、商品/求购、失物寻找/招领、搜索与分页、发布编辑、系统文件选择上传、私信、统一通知、地点讨论与回复、校园 RAG 助手。
- 样式适配手机；页面源代码复用业务组件，避免复制后功能分叉。地图使用分级高清切片，支持单指拖动和双指缩放。
- Android HTTP/XHR/上传使用 Capacitor 原生桥，复用服务端 Session 与 CSRF，不新增持久登录；退出和后端重启后会话按原规则失效。
- Android 受保护图片通过原生请求读取后显示为临时 Blob URL，卸载组件时释放；不会把用户图片永久写入 App 静态资源。
- `CampusStreamPlugin` 仅允许 `/api/events` GET 和 `/api/assistant/ask` POST，读取真实 SSE 流；不借用普通 HTTP 桥的缓冲响应冒充流式。连接并发限定为 2，退出前台关闭，通知返回前台重连并同步。
- 模型 API 与 RAG 继续完全由 Java 后端提供，APK 中没有模型 API 密钥。静态校园美术从原前端按构建复制，排除 40 MB 地图母图；手机普通预览与全屏切片按需读取。

App 退到后台或关闭后的系统通知，需要后续接入对应推送服务；当前仅保证前台 SSE 和回来后的同步。当前生成 Android 工程；iOS 原生工程和平台通信桥尚未实现，不能宣称直接支持 iPhone 安装。

## 测试

`npm test` 验证地址策略和 SSE 解析。`npm run build` 检查手机端与共用组件的 TypeScript 并打包。

Android 集成测试 `MobileBridgeTest` 在实际 WebView 内验证原生登录 Cookie、CSRF、图片显示、multipart 上传、SSE 和退出。它固定连接 `127.0.0.1:18080`，需要先执行 `adb reverse tcp:18080 tcp:18080`，且只允许先启动仓库独立 QA 后端，不能将该端口指向正式库。测试创建的数据随 QA 数据库整体清理。运行时保持模拟器启动，再执行 Gradle `connectedDebugAndroidTest`。如果环境的分包流式安装失败，可分别使用 `adb install --no-streaming -r` 安装 app-debug.apk 和 app-debug-androidTest.apk，再通过 `adb shell am instrument` 运行指定测试类。它不验证真实模型回复（QA 默认关闭 AI），也不能替代真实手机相册、系统键盘和弱网测试。

手机预览不要求 Android Studio；浏览器版本不能验证 Android 原生桥。
