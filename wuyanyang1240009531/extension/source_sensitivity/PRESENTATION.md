# Presentation and questions

## One-slide English draft

**Source sensitivity in a matched Linux project**

- Question. Would Linux defect patterns look similar if records came from an upstream tracker?
- Design. We compare publicly documented Ubuntu Launchpad and upstream GitHub systemd defects from the same report window. We apply the paper's taxonomy and verify issue and fix evidence.
- Observation. Environment-dependent triggers account for 3/5 Launchpad records and 0–1/6 GitHub records, depending on the unresolved trigger.
- Implication. The all-layer direction survives the sensitivity checks. Within-layer evidence is inconclusive because it depends on layer mapping and very small denominators.

**Speaker notes, about 30 seconds**

I examined source sensitivity using systemd defects from Ubuntu Launchpad and upstream GitHub, applying the paper's taxonomy over a common window. Environment-related triggers were confirmed in three of five Launchpad records and in none of six GitHub records, with one GitHub trigger unresolved. The overall difference survives that uncertainty within this sample. Within-layer comparisons depend on how we classify the records.

## 中文答辩提纲

上台前准备沿三份表解释同一个结果。先用 `results/environment_sensitivity.csv` 的 `all` 行确认分母和未知数，再用 `results/defects.csv` 筛出构成分子的三条 Launchpad 记录和一条触发未知的 GitHub 记录，最后从 `results/candidate_audit.csv` 找到原始链接及筛选依据。同层比较要同时看 `same_layer` 和 `same_layer_author_labels`，两行的下游分母分别为 4 和 1。

| 老师可能问 | 回答要点 |
|---|---|
| 你具体改变了什么？ | 我把论文 Linux 样本中的 Ubuntu systemd 记录，与同项目的 GitHub 上游记录对照。尽量固定时间窗、项目和分类词汇，核对不同采集渠道看到的分布。熊耀鹏的主变量是时间。 |
| 为什么不拿 GitHub 直接对比全部 Linux 500 条？ | 500 条混合了不同项目，而我的新增记录属于 systemd。限制项目能减少构成差异，结果的外推范围也相应缩小。 |
| 为什么候选 48 条只剩 6 条？ | 41 条排除，另 1 条集成测试来源的记录只进入敏感性分析。审计表逐条说明缺少唯一关联、日期、功能请求、测试范围和补丁规模等筛选理由。 |
| 报告日期与修复日期为什么分开？ | 两边按报告创建日期比较报告窗口，修复也要求位于同窗内。GitHub 的合并时间和 Ubuntu 的发布修复日期分别代表上游和下游事件，原始字段分别保留。 |
| 如何核实修复和去重？ | 检查缺陷 ID、提交 SHA、补丁和报告正文中的跨平台引用。LP #2052137 关联的上游报告和修复均在本次 GitHub 候选之外。没有明确链接的回移仍可能漏掉。 |
| 给一个实际例子。 | GitHub issue #27489 记录 journalctl 读损坏日志时卡住，PR #27499 改动 sd-journal 库，归入系统库、存储管理和边界条件。答辩时可以沿着两条链接演示证据。 |
| 为什么要复核层级？ | 三条下游层级重标和原标签不同。恢复原标签后，服务层从 4 对 3 变成 1 对 3，环境依赖比例的差距也变了。当前同层证据不足。 |
| 差距能证明来源造成差异吗？ | 在筛选后的样本里，Launchpad 的环境依赖占比高 43.3 至 60.0 个百分点，范围来自一条标签未知的记录。版本、报告人群和筛选机制也可能影响结果。 |
| 跑了三次为什么仍不确定？ | 三次运行同一冻结数据检验计算可重复性。上下界只体现未知标签的归类，对总体的推断需要另外的抽样设计。 |
| 这是漏洞复现吗？ | 我做的是公开缺陷记录、修复元数据和标签的统计验证。我用报告与补丁支持分类和纳入决定。 |

[上游示例报告](https://github.com/systemd/systemd/issues/27489) · [对应 PR](https://github.com/systemd/systemd/pull/27499)
