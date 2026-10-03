# 本机 DMD 数据检查流程

本文件说明当前轻薄本可以执行的 DMD 本地检查流程。流程只读取元数据、生成本地忽略的样本清单，并对已授权且本机可访问的少量视频执行边界探测；它不会启动模型训练。

## 前提

在 Ubuntu 终端中进入项目并激活虚拟环境：

```bash
cd ~/projects/federated-driving-system
source .venv/bin/activate
```

数据路径示例：

```text
/mnt/d/datasets/DMD/pilot
```

其中 `metadata` 保存 JSON 标注，`.tar.gz` 保存原始数据压缩包。数据文件不进入 Git。

## 1 检查标注

```bash
python scripts/inspect_dmd_annotations.py /mnt/d/datasets/DMD/pilot/metadata
```

输出每个 JSON 文件的帧数、驾驶员数、动作区间数和动作帧数。该命令只读 JSON，不读取视频，也不训练。

## 2 检查任务定义和标签覆盖

```bash
python scripts/check_task_spec.py configs/distraction_task.example.json
python scripts/check_task_coverage.py /mnt/d/datasets/DMD/pilot/metadata configs/distraction_task.example.json
```

第一条验证任务配置；第二条检查原始动作可以映射到哪些目标标签。当前任务将 `driver_actions/safe_drive` 映射为 `safe_drive`，将一组已明确的驾驶分心动作映射为 `distraction`，并排除 `driver_actions/unclassified`。

## 3 检查驾驶员组

```bash
python scripts/check_driver_groups.py /mnt/d/datasets/DMD/pilot/metadata configs/distraction_task.example.json
```

当前任务要求至少 3 个不同驾驶员组。现有 pilot 只有 ID 为 `1` 的驾驶员，因此本步骤会报告组数不足。不要绕过此限制来进行正式按驾驶员训练。

## 4 规划候选样本并建立清单

```bash
python scripts/plan_dmd_samples.py /mnt/d/datasets/DMD/pilot/metadata configs/distraction_task.example.json configs/sample_index.example.json
python scripts/build_candidate_manifest.py /mnt/d/datasets/DMD/pilot/metadata configs/distraction_task.example.json configs/sample_index.example.json outputs/pilot_candidate_manifest.csv
```

第一条按采样规则统计候选帧数量；第二条写出本地 CSV 清单。清单包含会话、标注文件、视频文件名、驾驶员 ID、帧号和目标标签。输出文件放在 `outputs/`，不会提交 Git。

## 5 按实际视频帧数过滤

只有已在本机合规提取的视频可用于本步骤。示例：

```bash
python scripts/filter_manifest_by_video_bounds.py outputs/pilot_candidate_manifest.csv data/pilot_validation outputs/pilot_validation_manifest.csv
python scripts/check_manifest.py outputs/pilot_validation_manifest.csv
```

过滤脚本通过 `ffprobe` 获取每个视频的实际帧数，移除缺少视频的行以及超过该视频帧数的行。当前本机仅提取了少量 s3 视频作验证，因此大量候选行因本地不存在对应视频而被排除，这是预期行为。

## 6 检查训练前条件

```bash
python scripts/check_training_readiness.py outputs/pilot_validation_manifest.csv configs/distraction_task.example.json
```

该命令不会训练，只会检查清单是否为空、是否包含所有目标标签，以及驾驶员组数是否达到任务配置要求。

当前 pilot 的预期结论：

```text
ready_for_grouped_training: False
reasons: ('requires 3 driver groups, found 1',)
Training: NOT STARTED
```

## 7 规划驾驶员级训练 验证 测试组

多驾驶员数据通过训练前条件检查后，再执行：

```bash
python scripts/plan_group_split.py outputs/authorized_manifest.csv configs/distraction_task.example.json 20261003
```

解释：

- `outputs/authorized_manifest.csv` 是未来多驾驶员数据经视频边界过滤后的本地清单示例，不是当前 pilot 文件。
- `configs/distraction_task.example.json` 提供至少 3 个驾驶员组的规则。
- `20261003` 是记录在实验日志中的随机种子；相同清单和种子会得到相同的组分配。
- 输出仅列出训练、验证、测试对应的驾驶员 ID，不写出新清单、不读取视频，也不启动训练。
- 当前 pilot 只有 1 个驾驶员，因此运行它会明确报出组数不足。

只有在数据授权已确认、拥有至少 3 个不同驾驶员组、清单含有两个目标标签，并且台式机硬件与依赖环境已核对后，才进入下一阶段：单机基线训练设计。


## 8 写出本地训练 验证 测试清单

只在多驾驶员数据通过第 6 步后执行：

```bash
python scripts/write_group_split_manifests.py outputs/authorized_manifest.csv configs/distraction_task.example.json 20261003 outputs/authorized_splits
```

解释：

- 本命令读取已通过视频边界过滤的本地清单。
- 它按驾驶员 ID 生成互不重叠的 `train.csv`、`validation.csv` 和 `test.csv`。
- 每个拆分都必须含有任务所需的两个目标标签；缺少标签时工具会报错，不会生成不完整的实验清单。
- `outputs/authorized_splits` 是本地输出目录，Git 会忽略其中的 CSV 文件。
- 命令只写本地 CSV，不读取视频，不训练模型。
