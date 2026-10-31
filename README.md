# SDU Smart Life
校园二手交易与社区平台，正在从 Flask 迁移至 Vue 3 + Spring Boot。

## 当前状态
已完成工程基础、校园首页和用户注册/登录/退出。商品、地图及交易功能仍待迁移。

## 本地运行
需要 JDK 21+、Maven 3.9+、Node.js 22。

后端：`cd backend` 后执行 `mvn spring-boot:run`。
前端：`cd frontend` 后执行 `npm ci`、`npm run dev`。
访问 http://127.0.0.1:5173，后端端口为 8080，健康检查 `/actuator/health`。

## 目录
- backend：Java 服务，编译目标 Java 21。
- frontend：Vue 前端；public/assets/legacy 保存原仓库静态资源。
- reference：原始 Flask 代码和模板，仅用于业务迁移对照，不作为新系统运行依赖。
- docs/changes：每次推送的修改说明，文件名与该次提交主题一致。

## Git 约定
使用功能分支，提交前检查构建和差异；不提交密码、依赖目录、日志或本地环境。
每批推送使用唯一提交主题，附上同名 Markdown 说明，记录范围、验证和待办。

资源来源：https://gitee.com/haha_49_0/sdu-database-experiment-three.git 。保留来源说明；原仓库资源的授权范围仍需核实。

## 用户认证配置
先创建独立 MySQL 数据库 `sdu_smart_life`（utf8mb4），启动前设置环境变量 `DB_PASSWORD`；可通过 `DB_USER`、`DB_URL` 覆盖连接配置。密码不写入仓库。
Flyway 启动时创建用户表；原 `test` 数据库不变。旧账号尚未导入，请注册新账号。
用户名为 3–32 位字母、数字、下划线或短横线，密码 8–64 位。当前使用服务端 HttpSession，Redis 会话将在后续接入。
运行 `python scripts/check_auth.py` 可验证认证、会话隔离和 CSRF（会创建一个唯一测试账号）。
