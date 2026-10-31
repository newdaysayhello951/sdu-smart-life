# SDU Smart Life
Vue 3 + TypeScript + Spring Boot + MyBatis + MySQL校园牵线平台。以信息发布、校园交流及私聊联系为主，双方自行约定线下交接，不处理付款、订单或收货确认。

## 本地运行
需要JDK21+、Maven3.9+、Node22、MySQL8。创建utf8mb4数据库sdu_smart_life，设置DB_PASSWORD；按需设置DB_USER、DB_URL。
后端：`mvn -f backend/pom.xml spring-boot:run`。
前端：进入frontend执行 `npm ci`、`npm run dev`，访问 http://127.0.0.1:5173 。
Flyway自动升级数据库。未登录展示登录注册入口；当前服务端内存会话重启后需重新登录。

## 主要页面
- `/market`：出售与求购两块轮播，每次加载3条；支持触摸/鼠标滑动、横向滚轮、前后按钮和进度点。
- `/market/{id}`：发布者头像、用户名和用户ID，联系发布者进入私聊。
- `/my/products`：自己的资料与发布管理。可发布出售或求购、上传图片、编辑和下架；求购参考图可选。
- `/people/{id}`：独立公开主页，展示资料及出售/求购，无管理控件。查看自己自动返回管理页。
- `/messages`、`/messages/{id}`：私聊列表和双向文字/Emoji消息，每3秒刷新，消息分页读取。
- `/notifications`：私信及校园回复通知、未读标记、单条已读和一键已读；顶部气泡每5秒更新，99及以上显示99。
- `/campus`：高清校园图片地图、134个热点、地点问答、图文回复及完整对话。

## 数据与权限
所有业务字段、用户头像、商品图片、讨论附件、求购、私聊、通知和已读状态均存MySQL。
固定背景、校园规划图等属于系统美术资源，仍由前端静态托管。运行不依赖旧上传目录。
图片读取需要登录；业务关系使用稳定用户ID，改名后商品、消息作者、对方名称和通知名称同步。
私聊只允许会话双方读写，主页仅公开指定资料，无密码或编辑接口。
旧交易API、页面及入口已退役；历史trade_order表和商品原状态完整保留，不自动取消、重上架或删除。历史商品缺少可靠发布者映射时不猜测身份，联系入口不可用。
数据库备份应包含BLOB。数据库密码、业务数据、依赖、日志和本地环境不提交Git。

## 迁移工具
安装PyMySQL、设置DB_PASSWORD，运行 `python scripts/import_legacy_products.py` 只读旧test库，将商品及图片导入新库。
文件存储旧版本可先运行 `python scripts/migrate_images_to_database.py`，核对入库后原文件保留本地备份。
旧Flask应用、HTML、CSS、JS已从当前树清理，可查Git历史。scripts内Python仅为迁移及回归工具。

## 验证
启动前后端后，运行 `python scripts/run_regression.py`，执行9组活跃回归并在任一失败时返回非零。
覆盖认证与CSRF、改名关联、资料/头像、商品图像与事务、市场分页、校园问答、公开主页、双向私聊、并发创建会话、通知读状态与越权边界。
脚本会创建专用随机测试账号、讨论及消息，部分测试商品会下架；不修改真实用户资料。

## Git与来源
开发分支migration/java-vue；每批中文提交附docs/changes内同名Markdown说明。
原美术资源来源：https://gitee.com/haha_49_0/sdu-database-experiment-three.git 。地图来源为用户提供的校园规划图；图纸名称不等于当前实地名称，原素材授权范围需核实。

## 统一消息与定位
消息中心整合私聊和校园回复；新校园通知带focus消息ID，跨分页自动加载后滚动到对应回复，位置稳定后短暂按压并灰化周围消息。旧私聊列表地址重定向到消息中心。`scripts/check_notification_focus.py` 验证跨50条分页的定位。
