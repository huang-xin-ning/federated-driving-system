# 配置检查

项目的示例配置位于 `configs/development.example.json`。当前值为：

```json
"data_use_status": "pending_authorization"
```

因此任何依赖 `ProjectConfig.training_is_permitted()` 的后续训练入口都应被阻止。

在项目根目录运行：

```bash
.venv/bin/python scripts/check_config.py configs/development.example.json
```

该命令只读取 JSON 并打印状态；不会联网、下载数据、训练或写入文件。
