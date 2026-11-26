# 提交清单 — 层级构成分析（闻瑞宝 1240016315）

按组里「统一交付结构」逐项对应，交这一个压缩包即可。

## 1. 对应关系

| 组里要求 | 文件 |
| --- | --- |
| 问题与方法说明 | `docs/METHODS.md`（完整方法）、`ONE_PAGER.md`（一页英文稿）、`LAYER_ANALYSIS.md`（含结论与局限） |
| 数据与来源 | `docs/METHODS.md` §Data；沿用组内 1,500 条已发布记录（`PROVENANCE.json` 在仓库 `data/`） |
| 可运行代码 | `layer_analysis.py`、`run_layer_triplicate.py`、`tests/test_layer_rules.py` |
| 完整结果表 | `results/` 6 个 CSV + `determinism.json` |
| 核心图 | `figures/layer_composition.{png,svg}`、`layer_distance_adjustment.{png,svg}` |
| 结论与局限 | `LAYER_ANALYSIS.md` §Findings / §Limitations，`REPORT.md` §5–7 |
| 一页英文展示稿 | `ONE_PAGER.md` |
| 个人贡献 / AI 使用 | `docs/MEMBER_CONTRIBUTION.md`、`docs/AI_USAGE.md` |
| 并入组报告 | `docs/GROUP_INTEGRATION.md` |
| 改动清单 | `docs/FILES_CHANGED.md` |

## 2. 沿用 vs 本轮新增

**沿用**：1,500 条缺陷数据及 provenance、标签映射、OS 层/功能/触发场景类别定义、Table II 的分布口径。

**新增**：层级构成表、同层分布比较（带 n）、pooled/uniform 两种权重标准化、调整前后距离分解、2 张图（PNG+SVG）、3 次运行哈希一致性、12 个单元测试，以及「层级构成影响在三种配对间不对称」的结论。

## 3. 结果文件

| 文件 | 内容 | 行数 |
| --- | --- | ---: |
| `results/layer_composition.csv` | 3 系统 × 6 层级的样本数、占比、合并占比、是否纳入 | 18 |
| `results/layer_within_function.csv` | 每系统每层内 8 类功能分布 | 144 |
| `results/layer_within_trigger.csv` | 每系统每层内 7 类触发场景分布 | 126 |
| `results/layer_pairwise_function.csv` | 5 个共同层内三对系统的功能 JSD | 15 |
| `results/layer_pairwise_trigger.csv` | 同上，触发场景 | 15 |
| `results/layer_distances.csv` | 三对 × 两维：原始 / pooled / uniform / 同层平均 / 解释比例 | 6 |
| `results/determinism.json` | 3 次运行、逐文件哈希、耗时 | — |

## 4. 复现

```bash
python layer_analysis.py            # 生成 results/ 与 figures/
python run_layer_triplicate.py      # 3 次运行 + 哈希一致性
python -m unittest discover -s tests  # 12 个单元测试
```

无第三方依赖，Python 3.10+。

## 5. 一句话结论

层级构成解释了 Android–HarmonyOS 差异的约一半（43% / 48%），但对涉及 Linux 的两个配对不降反升——原始比较反而低估了层内差异；「三个系统不同」的结论在控制层级后仍然成立，但两两差距的大小和排序对层级构成敏感。
