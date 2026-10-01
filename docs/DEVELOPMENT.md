# 第一阶段代码骨架

本阶段只使用 Python 标准库，不安装机器学习、联邦学习或数据处理依赖。

## 本地验证

在项目根目录运行：

```bash
bash scripts/test.sh
```

该命令使用 `.venv/bin/python` 运行 `unittest`；它不会下载数据、联网或启动训练。

## 当前代码边界

- `DataUseStatus` 默认是 `pending_authorization`，因此训练被明确禁止。
- `ModelUpdate` 只存储元数据，不包含原始样本和模型权重。
- `UpdateAggregator` 只是接口定义，尚未实现任何训练或参数聚合。
