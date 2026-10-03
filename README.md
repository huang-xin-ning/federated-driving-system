# 联邦学习驾驶员行为监测隐私保护系统

本项目探索驾驶员行为监测、数据最小化和联邦学习的研究原型。当前仓库完成了 DMD 数据元数据检查、二分类任务定义、候选样本规划、视频帧边界过滤和训练前条件检查；尚未包含行为识别模型、正式单机训练、联邦训练或可部署应用。

## 当前结论

已在本机对 DMD pilot 数据完成只读检查。pilot 元数据中只有 1 个驾驶员组，因此**不满足**本项目按驾驶员划分训练、验证和测试所需的最少 3 个驾驶员组。训练前条件脚本会明确阻止把这份 pilot 数据当作正式分组训练数据。

这不是代码故障。后续需要获得已授权的多驾驶员数据，并重新运行训练前条件检查，才能进入正式训练阶段。

## 已实现的本地检查流程

- 解析 OpenLABEL JSON 标注，汇总帧数、动作区间和动作帧数。
- 定义首个二分类任务：`safe_drive` 与 `distraction`；明确排除 `driver_actions/unclassified`。
- 按固定采样间隔生成候选帧，避免重叠或冲突标签。
- 从标注中提取驾驶员组，并检查任务要求的最少组数。
- 从 DMD 压缩包元数据检查会话、视频与标注文件是否匹配。
- 使用 `ffprobe` 将候选样本与本地已提取视频的实际帧数对齐；缺少视频或越界的行不会进入验证清单。
- 汇总清单标签、驾驶员和样本数量，并给出训练前条件报告。
- 通过自动测试保护上述逻辑。

这些步骤不会启动训练，也不会将原始视频、样本图像或训练输出提交到 Git。

## 数据与应用边界

DMD 原始数据、压缩包、模型权重、训练输出、SSH 私钥和 Token 不提交 Git。每台机器分别创建自己的 `.venv` 环境。

数据授权尚未确认。项目尚未完成实车验证，不能声称具备商用、安全认证或自动驾驶控制能力。联邦学习使原始数据可以保留在客户端，但模型更新仍可能存在泄露风险；隐私威胁模型、保护机制和评估方法将在训练基线稳定后设计。

## 本机环境

本项目位于 WSL Ubuntu：

```text
/home/ning/projects/federated-driving-system
```

激活已有虚拟环境：

```bash
cd ~/projects/federated-driving-system
source .venv/bin/activate
```

解释：

- `cd` 进入项目目录。
- `source .venv/bin/activate` 激活项目虚拟环境；成功后提示符前出现 `(.venv)`。

运行全部自动测试：

```bash
./scripts/test.sh
```

解释：运行项目单元测试。当前应显示 `Ran 25 tests` 和 `OK`。

## DMD 本地检查示例

以下路径仅为本机示例。请按实际机器的数据位置替换，且不要把本地路径写入共享配置或提交 Git。

```bash
python scripts/inspect_dmd_annotations.py /mnt/d/datasets/DMD/pilot/metadata
python scripts/check_task_spec.py configs/distraction_task.example.json
python scripts/check_driver_groups.py /mnt/d/datasets/DMD/pilot/metadata configs/distraction_task.example.json
python scripts/check_training_readiness.py outputs/pilot_validation_manifest.csv configs/distraction_task.example.json
```

解释：

- 第 1 条只读取 JSON 标注并输出统计结果。
- 第 2 条检查安全驾驶与分心驾驶任务的标签映射。
- 第 3 条统计不同驾驶员组；当前 pilot 预期只会找到 1 组。
- 第 4 条检查清单是否具备进入按驾驶员分组训练的条件；当前 pilot 预期为 `ready_for_grouped_training: False`，并说明组数不足。
- 四条命令都不会启动训练。

完整的本地数据清单流程见 [docs/LOCAL_DATA_PIPELINE.md](docs/LOCAL_DATA_PIPELINE.md)。

## 双人协作

- 轻薄本：需求澄清、数据检查脚本、文档、CPU 小样本验证与流程记录。
- 伙伴台式机：核对 GPU、驱动、内存和存储；在数据授权和多驾驶员数据齐备后承担正式训练与较大实验。
- Git 共享源代码、测试、配置模板、标签映射、数据划分规则和文档。
- 开始工作前执行 `git pull origin main`；完成一组完整且测试通过的修改后，再检查暂存内容、提交并推送。
- 不要使用 Windows Git 直接操作 `\\wsl.localhost` 下的仓库；请在 Ubuntu 终端内执行 Git 命令，避免 Windows 与 Linux 的换行符差异造成大量伪修改。

## 下一步

1. 将本次训练前条件检查与文档更新作为一个批次提交。
2. 伙伴台式机完成硬件核查、独立环境和 GitHub 协作配置。
3. 确认 DMD 数据授权、共享范围和多驾驶员数据可用性。
4. 在至少 3 个驾驶员组的数据上重新构建清单，并通过训练前条件检查。
5. 根据台式机实际 GPU、驱动和 Python 版本确定训练框架和依赖版本。
6. 实现可复现的单机基线，再实现联邦客户端模拟与聚合基线。
