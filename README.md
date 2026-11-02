# SDU Smart Life · 智慧校园

基于 Java 21、Spring Boot 3.5、Spring Security、MyBatis-Plus、Flyway、MySQL 8、Vue 3、TypeScript 与 Vite 的校园牵线平台。复用原项目的校园美术资源，提供出售/求购、校园地点交流及私聊联系。双方自行约定线下交接，平台不处理订单、付款或收货确认。

## 本地运行

需要 JDK 21+、Maven 3.9+、Node.js 22 与 MySQL 8。先创建空数据库：

```sql
CREATE DATABASE sdu_smart_life CHARACTER SET utf8mb4;
```

PowerShell 第一个终端设置数据库连接并启动后端（密码填写自己的本地配置，不写入代码）：

```powershell
$env:DB_USER = 'root'
$env:DB_PASSWORD = '你的本地数据库密码'
mvn -f backend/pom.xml spring-boot:run
```

可通过 DB_URL 指定完整 JDBC 地址，默认连接 127.0.0.1:3306/sdu_smart_life。Flyway 启动时自动升级数据库；不要修改已经应用的迁移脚本。

第二个终端启动前端：

```powershell
cd frontend
npm ci
npm run dev
```

访问 http://127.0.0.1:5173 。Vite 将 `/api` 代理到后端 8080 端口。后端健康检查为 http://127.0.0.1:8080/actuator/health 。

登录会话仍保存在服务端内存；普通刷新保持登录，后端重启或会话过期后需要重新登录。账号及业务数据不受影响。

## 当前功能与页面

| 地址 | 功能 |
| --- | --- |
| `/` | 原校园背景首页、登录注册入口、固定导航及全局消息气泡 |
| `/market` | 出售与求购两个独立轮播，支持搜索；每次加载3条，支持滑动、按钮和进度点 |
| `/market/{id}` | 商品/求购详情、发布者头像和用户ID、公开主页及私聊入口 |
| `/my/products` | 自己的资料管理，以及出售/求购发布、编辑、图片修改和下架弹窗 |
| `/people/{id}` | 他人的公开资料与出售/求购，不能编辑；查看自己会转到管理页 |
| `/messages/{id}` | 私聊：本人消息靠右，对方靠左，支持文字与Emoji，以及通知消息定位 |
| `/notifications` | 统一私信/校园回复通知，支持分类、已读跳转、一键已读及继续加载 |
| `/campus` | 高清青岛校区图片地图、134个热点、地点名称搜索与地点讨论弹窗 |
| `/campus/{placeId}/conversations/{rootId}` | 完整对话、回复及回复的回复，支持图片/GIF、Emoji和通知定位 |

`/messages` 统一跳转到消息中心；不再单独展示聊天对象头像列表。消息气泡未读数低于99显示具体数量，达到99显示99。

地点讨论外层显示最早两条回复，完整对话按每页50条继续加载。讨论图片以缩略图展示，可打开原图；上传校验与显示尺寸限制相互独立。地图名称依据用户提供的规划图，图纸编号和名称不等于当前实际命名。

## 实时消息

登录后，前端为当前页面建立一条 `/api/events` SSE 连接。私信和校园回复写入 MySQL 并提交后，再向相关用户发送更新提示；客户端通过有权限的接口取回内容。全局未读数、消息中心和当前私聊不再通过3秒/5秒定时轮询更新。

- 同一账号的多个标签页同步收到消息和已读变化。
- 网络断开后自动重连；每次连接成功从数据库同步状态，补取错过的私信及通知。
- 后端每20秒发送保活，不传聊天内容；连接最长15分钟后自动重新建立。
- SSE 绑定当前登录用户，退出登录关闭连接；无关用户收不到私信更新。
- 通知使用稳定的消息ID定位，已读通知也可跳转。校园回复跨分页加载后滚动定位，短暂按压突出并灰化周围发言；私聊定位同样突出目标消息。

当前推送服务适用于单个后端实例；没有引入 Redis、持久化登录会话或跨实例消息广播。

## 数据、资源及权限

用户资料、头像、商品图片、出售/求购、校园讨论附件、私聊、通知与已读状态均存 MySQL；用户上传图片以 BLOB 保存，通过鉴权接口读取。系统背景及校园地图属于固定美术资源，保留前端静态托管。

商品、发言、私聊和用户资料通过稳定用户ID关联，改用户名不会改变归属。私聊仅会话双方可读写，公开主页不返回密码或管理权限。旧交易功能已退役，历史表和原商品状态保留。

旧 Flask 应用及 HTML/CSS/JS 已从当前应用树清理。`scripts/` 中 Python 仅作迁移和回归验证，应用运行不依赖 Python。旧数据工具包括：

- `scripts/import_legacy_products.py`：只读旧库，导入商品及图片；未可靠映射的旧发布者不猜测归属。
- `scripts/migrate_images_to_database.py`：把早期文件存储图片迁入数据库，保留原文件备份。

两者需要 PyMySQL 和环境变量配置，执行前阅读脚本；不代表旧账号、旧求购、评论和聊天已全部导入。数据库内容、密码、依赖、日志和本地截图不提交 Git。

## 构建与隔离验证

测试使用全新QA数据库和18080/15173端口，不向日常使用的数据库写入测试数据。需要本地MySQL、Python及PyMySQL；数据库账号需有创建/删除测试库的权限。先安装前端依赖并构建独立后端，避免覆盖正在运行的JAR：

```powershell
npm --prefix frontend ci
npm --prefix frontend run build
$qaBuild = Join-Path (Get-Location) '.tools/qa-build/target'
mvn -f backend/pom.xml "-Dsmartlife.build.directory=$qaBuild" package
python -m pip install PyMySQL
$env:DB_USER = 'root'
$env:DB_PASSWORD = '你的本地数据库密码'
python scripts/run_isolated_tests.py --stress --soak
```

Maven执行4项单元测试；隔离脚本自动创建全新数据库、启动独立服务，执行11组业务回归、14组并发专项和最长45秒的64并发混合读写。结束后停止QA服务并删除本次测试库，不删除真实数据库。`--keep` 可供开发者暂留QA环境进行浏览器验收，使用后需停止对应QA进程并删除该次QA数据库。

原有 `run_regression.py` 及 `check_*.py` 要求显式配置隔离测试地址，不再默认向5173端口写测试数据。测试产物和日志存于本地 `.tools/`，不提交Git。市场测试自行创建样本，不依赖已清除的旧商品。

已覆盖认证/CSRF、改名关联、资料/头像、商品与图片事务、出售/求购、校园图文多层回复、公开主页、私聊和通知、游标定位、并发会话创建、提交乱序、实时连接隔离/重连/退出，以及持续读写后数据库消息和通知数量的一致性。浏览器验收包含桌面及320/390像素窄屏。

本机测试结果见 [全功能测试报告](docs/testing/2026-10-31-全功能测试报告.md)。市场分页返回snapshot边界，轮播翻页沿用该边界，避免新增发布挤动已打开的分页。后端断线连接清理不会阻断其他用户的推送或心跳。

## Git与来源

开发分支 `migration/java-vue`；每批中文提交附 `docs/changes/` 下同名 Markdown 说明。

原美术资源来源：https://gitee.com/haha_49_0/sdu-database-experiment-three.git 。高清地图由用户提供，原素材授权范围需核实。


### 失物回家
- 登录后导航进入 `/lost-found`；上方「失物寻找」，下方「宝贝回家」，每组分页滑动加载并显示进度点。
- 在自己的个人主页点击「失物寻找与招领」（山大印章、海棠猫图案），弹窗选择寻找失物或寻找失主；填写名称、描述、地点，可附图片。时间、物品特征填写在描述中。
- 支持按名称、描述或地点搜索；详情显示发布者，可访问公开主页和私聊核验。
- 个人主页可编辑、替换图片、结束寻找。失物类型 LOST/FOUND 与 SELL/WANTED 分开展示，复用现有发布及权限接口；失物金额固定为 0，页面不显示价格。
- 业务信息和用户上传图片均存 MySQL；按钮装饰为前端 SVG。无需新增数据库迁移。
- `scripts/check_lost_found.py` 已纳入隔离回归（12 组），不得直接针对实际业务库运行。


### 校园智慧问答助手「汐月」
Java 21 / Spring Boot 3.5.7 / Spring AI 1.1.0；独立 multilingual-e5-small ONNX 模型（Java ONNX Runtime 1.20.0、DJL Tokenizers），Qdrant 1.15.4 + BM25 + RRF 混合检索。MySQL 保存官方知识原文、片段、向量、来源时间及用户隔离的聊天历史，Qdrant 仅保存可重建索引。无 Python AI 服务、无其他项目数据库连接。

1. `python scripts/setup_campus_ai.py` 安装校园项目独立模型和 Qdrant，默认从公开上游下载；Hugging Face 直连不可用时可设置 `HF_MIRROR=1` 使用镜像。
2. 按 `.env.example` 在仓库根目录创建 `.env.ai`，填写自己的模型 API；只读取 LLM_BASE_URL、LLM_MODEL、LLM_API_KEY / DEEPSEEK_API_KEY，不复制其他项目环境、业务数据或服务。
3. Maven 构建后，设置 `DB_PASSWORD`，运行 `powershell -ExecutionPolicy Bypass -File scripts/start_campus_ai.ps1 -StartBackend`。确保 8080 没有旧服务占用。单独启动依赖时不传 -StartBackend。
4. 登录后点击可拖动的小海妖打开对话。海棠、山大红飘带与书本、青岛海鸥/海浪/贝壳装饰；眨眼、招手、摆尾、悬停及拖动反馈，不自动左右移动，可收起。

首次启动按 `campus-knowledge-sources.json` 低频采集山大官方公开指导资料；默认每天更新，失败保留已有版本。回答带来源、适用校区和采集时间。没有实时人数能力，重要政策应核对官方通知。只读 Agent 工具查询知识、地点、在发布商品/失物和本人通知；不会代发私信、修改资料或交易。每人一个并发回答，全局上限4，工具最多6次、规划最多3轮，支持取消和超时。界面安全渲染 Markdown，禁用HTML和图片注入，链接限制为本站业务入口和山大官方 HTTPS。

常规隔离回归为13组；设置 `AI_LIVE_TESTS=1` 并启用AI后，`scripts/check_campus_ai.py` 可验证真实模型（会产生模型调用费用），仅允许15173 QA端口。测试集合应使用独立 `CAMPUS_AI_COLLECTION`，不得混用实际知识索引。
