<<<<<<< HEAD
# 联邦学习驾驶员行为监测隐私保护系统

吉利资助的学生创新项目，目标是探索驾驶员行为监测与联邦学习隐私保护，并逐步验证实际应用可行性。

## 当前状态

本仓库目前仅为协作骨架：没有行为识别模型、联邦训练实现、数据集或可启动应用。`requirements.txt` 有意保持为空；`pip check` 通过不能证明业务依赖已经齐全。

拟使用 DMD Driver Monitoring Dataset，尚未下载。具体标签、可用数据范围和任务定义需在数据检查后确定，不预设分类数量。

## 数据与应用边界

Vicomtech DMD 官方仓库当前标注 CC BY-NC-ND 4.0。企业资助研究、团队数据共享、模型交付和商业使用范围需要向数据方明确，不将公开下载等同于商用授权。参考：https://github.com/Vicomtech/DMD-Driver-Monitoring-Dataset

数据授权尚未确认。本项目尚未完成实车验证，不能声称已具备商用、安全认证或自动驾驶控制能力。联邦学习仅让原始数据保留于客户端，并不自动消除模型更新泄露风险；隐私威胁模型和保护方法待设计。

## 双人协作

- 轻薄本：需求、数据检查脚本、界面、文档、CPU 小样本测试。
- 伙伴台式机：硬件确认后承担完整训练和较大实验。
- 两台电脑分别建立虚拟环境，不共享 `.venv`。
- Git 共享源码、配置模板、标签映射、数据划分规则和文档。
- 原始数据、模型权重、训练输出不提交 Git；另行通过有访问权限的存储交接，并遵守授权。
- 一台电脑可以模拟多个联邦客户端；协作者人数不等于客户端数量。

## 环境准备（Ubuntu / WSL）

已有 `.venv` 时保留，不需要重新创建。伙伴首次获取项目后可运行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

当前依赖文件为空，安装命令不会安装业务依赖。Python 支持版本、训练框架和 GPU 依赖待伙伴硬件确认后选择，并记录验证过的版本。不要直接将一台机器的完整环境列表当作 CPU/GPU 通用依赖清单。

## 文件结构

```text
src/                 后续源码
notebooks/           探索性实验（输出中不保留敏感数据）
configs/             可共享配置示例
data/                本地数据，不跟踪实际数据
models/              本地模型权重
outputs/             本地训练输出
docs/COLLABORATION.md 协作和实验交接约定
PROGRESS.md          进度与待办
AGENTS.md            AI 编码协作约定
```

`configs/paths.example.json` 是未来程序的配置格式示例，当前没有程序读取它。各机器复制为 `configs/paths.local.json`，填写各自路径；本地配置不提交。

## 远程仓库

https://github.com/huang-xin-ning/federated-driving-system

代码仓库访问权限与 GitHub Projects 看板权限分别管理。上传前检查 `git status` 和暂存差异；不要强制推送或覆盖远程已有提交。

## 下一步

确认数据授权和伙伴硬件 → 确定首个行为识别任务 → 数据检查与按驾驶员划分 → 单机基线 → 联邦基线 → 隐私机制及评估 → 演示与实际场景验证。

尚无应用启动命令。请勿使用虚构的 `app.py` 或训练入口。
=======
# federated-driving-system
Federated learning based driving system
>>>>>>> origin/main
