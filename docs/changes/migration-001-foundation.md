# migration-001-foundation

## 修改
- 新建 Java 21 编译目标的 Spring Boot 工程及 Vue 3 / TypeScript 工程。
- 从原仓库 Git HEAD 提取静态资源和模板，避免包含本机运行生成的文件。
- 首页复用原背景资源，提供 Java 接口连接状态。
- 保留原始代码作为业务参考，建立 Git 忽略规则及迁移记录约定。

## 边界
尚未迁移登录、数据库、交易及地图功能；不修改现有 test 数据库。

## 验证
- Vue TypeScript 检查和生产构建通过。
- Maven package 通过（JDK 24 运行，编译目标 Java 21）。
- Java 健康检查返回 UP。
- 经 Vite 代理访问 /api/platform 成功。
- 原背景图片 HTTP 200。
- 尚未执行完整业务验收。

## 下一步
数据库结构盘点及独立数据库迁移；用户认证、商品列表与详情迁移。

## 检查备注
原始参考代码数据库密码已脱敏；资源归档保留原有空白格式，diff check 的空白告警来自原始文件。
