# 配置检查

项目的示例配置位于 `configs/development.example.json`。当前值为：

```json
"data_use_status": "pending_authorization"
```

因此任何依赖 `ProjectConfig.training_is_permitted()` 的后续训练入口都应被阻止。

`configs/experiment_plan.example.json` 使用同一组状态值：
`pending_authorization`（待授权）、`authorized_research`（已明确授权研究用途）、
`authorized_deployment`（已明确授权部署用途）和 `prohibited`（禁止使用）。
实验计划不接受含糊的 `authorized`。只有在实际取得对应用途的授权后，
才能把状态改成相应的已授权值；状态字段本身不能证明已获授权。
即使状态为已授权，驾驶员分组、标签和联邦客户端等检查仍需分别通过。

在项目根目录运行：

```bash
.venv/bin/python scripts/check_config.py configs/development.example.json
```

该命令只读取 JSON 并打印状态；不会联网、下载数据、训练或写入文件。
