# 架构与边界

## 当前可运行链路

```text
浏览器（5310）
  -> Vite /api 代理
  -> FastAPI（8100）
  -> 知识空间路由
  -> SQLite repository
  -> data/knowledge.db
```

`app/main.py` 创建应用，启动时仅初始化本地数据库。同步 SQLite 路由由 FastAPI 线程池执行，独立连接避免跨请求共享连接。SQL 参数化；知识空间名称不区分 ASCII 大小写去重。数据库版本迁移在引入文档表前补充，当前只有一张表。

## 规划中的问答链路

```text
文档上传 -> 校验与持久化 -> 解析 -> 分段 -> 向量索引
提问 -> 指定知识空间检索 -> 相关片段 -> 远程模型 -> 回答与引用
```

`services/contracts.py` 只有 DocumentParser、Retriever、AnswerGenerator 协议，没有实现。先从 TXT/Markdown 开始，验证数据链路后再引入 PDF/DOCX 及向量服务。优先 SQLite + 本地索引；是否需要 PostgreSQL/pgvector，应在数据量和检索评测明确后决定。

## 配置与运行约束

- `.env` 位于仓库根目录，`EKA_DATA_DIR` 相对路径始终相对于仓库根目录。
- 真实密钥只存在服务端环境中；状态接口最多返回“是否配置”的布尔值。
- API 采用同源代理；不开放全域 CORS，不默认监听 0.0.0.0。
- 当前尚无身份验证或权限隔离，只适用于本机开发。
- 后续远程调用必须显式超时；不得在健康检查或首次导入期间下载分词表、模型等资源。
- 不采集用户简历、浏览历史或其他工作目录文件。示例资料必须可公开使用。

## 前端边界

`views/KnowledgeWorkspace.vue` 承载真实可用的知识空间创建与列表；`api/client.ts` 统一超时和错误处理；`types.ts` 保存接口类型。尚未实现的模块只展示开发计划，不使用模拟回答或虚构业务统计。
