# API v1

基础地址：`http://127.0.0.1:8100/api/v1`；OpenAPI：`http://127.0.0.1:8100/docs`。

| 方法 | 路径 | 行为 |
| --- | --- | --- |
| GET | `/health` | 本地数据库健康检查，无外网请求 |
| GET | `/status` | 实现阶段、模块状态及模型配置布尔状态，无密钥 |
| GET | `/knowledge-bases` | 知识空间列表 |
| POST | `/knowledge-bases` | 创建空间，返回 201 |
| GET | `/knowledge-bases/{uuid}` | 空间详情，不存在返回 404 |
| POST | `/chat` | 预留契约，当前返回 501，不调用模型 |

创建示例：

```powershell
$body = @{name='IT 运维手册';description='办公设备与网络故障资料'} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8100/api/v1/knowledge-bases -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($body))
```

名称自动去除首尾空白，长度 1–80；说明最长 500。重复名称返回 409，非法输入返回 422。不存在的空间返回 404。前端代理路径为 `/api/v1/...`。

未来问答请求契约为 `{knowledge_base_id, question}`。当前返回 `501` 是有意声明尚未实现，不能作为生成结果使用。
