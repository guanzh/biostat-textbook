# Textbook Content Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 检查全书 22 章和 7 个附录，直接修正会误导统计判断的高优先级问题，并交付逐章审校记录。

**Architecture:** 先用源文件回归测试锁定已知错误，再按“推断基础、模型与生态应用、决策与现代方法”三组修改正文。最后对所有触及文件运行 humanizer 循环，并在审校报告中记录 30 个读者文件的检查结果。动画嵌入由独立计划处理。

**Tech Stack:** Quarto Markdown、Python `unittest`、R 教学代码、ripgrep、humanizer 2.8.0

## Global Constraints

- 保留案例推进、黑豹提醒和尖锐反例，只收紧统计错误、论证跳步和超过证据边界的绝对判断。
- 术语使用“稳定性（Robust）”，不用“鲁棒性”。
- 不使用破折号，不新增“值得注意的是”“综上所述”等模板句。
- 参考文献采用作者加年代；如需新增，中文在前、英文在后。
- 不修改渲染后的 HTML、TeX、日志、缓存和 `_site`。
- 不覆盖工作区已有的 `_quarto.yml`、旧设计说明和生成文件改动。
- 每个读者文件完成 draft、残留 AI 特征检查、final 三步 humanizer 循环。
- 提交前运行 `git diff --check`，并以项目根目录加入 `PYTHONPATH` 后运行测试。

---

### Task 1: 建立内容准确性回归测试

**Files:**
- Create: `tests/test_content_accuracy.py`
- Inspect: `chapters/*.qmd`
- Inspect: `appendices/*.qmd`

**Interfaces:**
- Consumes: 当前 22 章与 7 个附录的 UTF-8 文本。
- Produces: `ContentAccuracyTests`，后续任务以该测试判断已知误导表述是否清除。

- [ ] **Step 1: 写入会失败的源文件测试**

```python
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class ContentAccuracyTests(unittest.TestCase):
    def test_p_value_is_not_probability_of_observed_data(self):
        sources = "\n".join(
            read(path)
            for path in (
                "chapters/01-role-of-statistics.qmd",
                "chapters/08-two-group-comparison.qmd",
                "chapters/17-stats-to-action.qmd",
                "chapters/20-bayesian-intro.qmd",
            )
        )
        forbidden = (
            "观察到当前数据的概率",
            "如果零假设为真，数据的概率",
            'P 值回答"效应是否可能为零"',
        )
        for phrase in forbidden:
            self.assertNotIn(phrase, sources)
        self.assertIn("同样或更极端", sources)
        self.assertIn("不表示零假设为真的概率", sources)

    def test_rank_test_is_not_unconditionally_described_as_median_test(self):
        chapter = read("chapters/08-two-group-comparison.qmd")
        appendix = read("appendices/method-map.qmd")
        self.assertNotIn("检验的是两组的中位数是否相等", chapter)
        self.assertNotIn("它检验中位数差异", chapter)
        self.assertNotIn("数据严重偏态", appendix)
        self.assertIn("随机优势概率", chapter)
        self.assertIn("分布形状", chapter)

    def test_interaction_and_independence_claims_are_conditional(self):
        chapter = read("chapters/09-anova.qmd")
        self.assertNotIn("主效应不能被单独解释", chapter)
        self.assertNotIn("这由设计保证（随机化）", chapter)
        self.assertIn("简单效应", chapter)
        self.assertIn("干扰", chapter)

    def test_sampling_and_richness_claims_are_qualified(self):
        sampling = read("chapters/06-sampling-error.qmd")
        richness = read("chapters/15-biodiversity-data.qmd")
        self.assertIn("独立同分布", sampling)
        self.assertNotIn("必然多于调查 5 个样方", richness)
        self.assertNotIn("使它们可比", richness)

    def test_decision_rules_do_not_turn_intervals_into_commands(self):
        chapter = read("chapters/17-stats-to-action.qmd")
        self.assertNotIn("完全高于→行动", chapter)
        self.assertNotIn("完全低于→不行动", chapter)
        self.assertIn("损失", chapter)
        self.assertIn("可逆性", chapter)

    def test_bayesian_chapter_uses_current_rhat_guidance(self):
        chapter = read("chapters/20-bayesian-intro.qmd")
        self.assertNotIn("> 1.1 表示未收敛", chapter)
        self.assertIn("1.01", chapter)
        self.assertNotIn("频率学派不能回答这个问题", chapter)

    def test_every_reader_file_appears_in_audit_report(self):
        report = read("docs/reviews/2026-07-11-textbook-content-audit.md")
        reader_files = [ROOT / "index.qmd"]
        reader_files += sorted((ROOT / "chapters").glob("*.qmd"))
        reader_files += sorted((ROOT / "appendices").glob("*.qmd"))
        for path in reader_files:
            relative = path.relative_to(ROOT).as_posix()
            self.assertIn(f"`{relative}`", report)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认失败来自旧表述和缺失报告**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_content_accuracy -v`

Expected: 7 个测试中至少 6 个失败，失败信息包含当前错误短语或缺少 `docs/reviews/2026-07-11-textbook-content-audit.md`。

- [ ] **Step 3: 单独提交测试**

```powershell
git add -- tests/test_content_accuracy.py
git diff --cached --check
git commit -m "test: add textbook content accuracy contracts"
```

### Task 2: 修正推断基础章节

**Files:**
- Modify: `chapters/01-role-of-statistics.qmd`
- Modify: `chapters/05-descriptive-statistics.qmd`
- Modify: `chapters/06-sampling-error.qmd`
- Modify: `chapters/08-two-group-comparison.qmd`
- Modify: `chapters/09-anova.qmd`
- Modify: `chapters/11-correlation-regression.qmd`

**Interfaces:**
- Consumes: Task 1 的 P 值、秩检验、交互作用和标准误测试。
- Produces: 全书后续章节可复用的统计推断口径。

- [ ] **Step 1: 统一 P 值定义**

在第 1 章和第 8 章使用以下口径，具体案例名保持原文。

```markdown
在零假设成立、统计模型条件满足的前提下，P 值是在重复抽样的设想中，得到与当前检验统计量同样或更极端结果的概率。P 值较小，说明这组数据与零假设及其模型条件不太相容。它不表示零假设为真的概率，也不说明效应有多大。
```

第 8 章同步将双侧置换 P 值改为含有限次置换校正的写法，避免模拟 P 值为 0。

```r
p_perm <- (sum(abs(perm_diffs) >= abs(obs_diff)) + 1) / (n_perm + 1)
```

- [ ] **Step 2: 修正秩检验的被检验对象**

用以下三层说明替换“检验中位数”的绝对说法。

```markdown
Mann-Whitney U 检验（Wilcoxon 秩和检验）比较两组观测的相对位置。连续分布下，它可以表述为随机优势概率，即从一组随机抽取的值大于另一组随机值的概率是否偏离 0.5。只有再假设两组分布形状相同、主要差别是位置平移时，才适合把结果解释为位置或中位数差异。它不直接检验均值差。
```

- [ ] **Step 3: 给标准误和置信区间补上条件**

第 6 章把 `SE = SD / √n` 限定为独立同分布观测的简单样本均值，并把置信区间解释写成关于构造程序覆盖率的完整句子。第 11 章将回归均值置信区间改为“在相同设计下反复获得数据并重建区间”的口径，不把单次区间称为真值范围。

```markdown
对独立同分布观测的简单样本均值，标准误可估计为 SE = SD / √n。聚类、重复测量或不等概率抽样需要按设计重新计算，不能只把表格行数代入 n。
```

- [ ] **Step 4: 收紧正态性和交互作用表述**

第 5 章保留“不要用正态性检验机械选方法”的主张，但将“不要做变换”改为“不为通过检验而机械变换”；说明有科学含义的尺度变换仍可能合理。第 9 章改为先报告条件效应或简单效应，必要时再解释明确定义的边际主效应。

```markdown
交互作用存在时，单个主效应是对另一因素各水平取平均后的边际比较。这个平均量未必没有意义，但它可能掩盖方向或大小不同的条件效应。应先画出交互作用并报告简单效应，再判断边际主效应是否回答原研究问题。
```

将“随机化保证独立性”改为随机化支持独立性推断，但重复测量、空间相关和单位间干扰仍需由设计与模型处理。

- [ ] **Step 5: 运行推断基础测试**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_content_accuracy.ContentAccuracyTests.test_p_value_is_not_probability_of_observed_data tests.test_content_accuracy.ContentAccuracyTests.test_rank_test_is_not_unconditionally_described_as_median_test tests.test_content_accuracy.ContentAccuracyTests.test_interaction_and_independence_claims_are_conditional tests.test_content_accuracy.ContentAccuracyTests.test_sampling_and_richness_claims_are_qualified -v`

Expected: 前 3 个测试通过；丰富度测试仍可能因第 15 章未修改而失败。

- [ ] **Step 6: 提交推断基础修改**

```powershell
git add -- chapters/01-role-of-statistics.qmd chapters/05-descriptive-statistics.qmd chapters/06-sampling-error.qmd chapters/08-two-group-comparison.qmd chapters/09-anova.qmd chapters/11-correlation-regression.qmd
git diff --cached --check
git commit -m "fix: tighten statistical inference explanations"
```

### Task 3: 修正生态指标、决策与贝叶斯章节

**Files:**
- Modify: `chapters/15-biodiversity-data.qmd`
- Modify: `chapters/17-stats-to-action.qmd`
- Modify: `chapters/18-mixed-models.qmd`
- Modify: `chapters/20-bayesian-intro.qmd`
- Modify: `chapters/21-spatiotemporal.qmd`
- Modify: `appendices/method-map.qmd`

**Interfaces:**
- Consumes: Task 1 的丰富度、决策、R-hat 和方法地图测试。
- Produces: 不把指标、区间或诊断阈值写成自动决策的应用章节。

- [ ] **Step 1: 修正丰富度与稀释法边界**

```markdown
在同一批样方中逐步增加调查努力，累计物种数不会下降，但新增样方未必带来新物种。比较不同地点时，调查 20 个样方通常比调查 5 个样方记录到更多物种，因此原始丰富度不能脱离努力量解释。

稀释法把样本下采样到共同的个体数或样本覆盖度，用来比较标准化后的期望丰富度。它减少努力量不等造成的差异，但不能修复样本代表性、生境异质性或探测概率不同。
```

删除“10 种加 5 个零物种”的混乱示例，改用两个不同相对丰度向量可以产生相近 Shannon 指数的数值示例，并明确 Shannon 指数不能恢复物种身份。

- [ ] **Step 2: 把行动阈值从命令改为决策输入**

第 17 章先改正 P 值定义，再说明区间与阈值的关系不能单独决定行动。用以下表意替代箭头命令。

```markdown
区间整体高于阈值时，数据与模型较支持效果达到预设水平；整体低于阈值时，较支持效果未达到该水平；跨越阈值时，当前精度不足以区分两种状态。行动还取决于错误行动与延迟行动的损失、成本、风险、伦理和可逆性。
```

- [ ] **Step 3: 收紧层级与时空依赖的后果方向**

第 18、21 章将“忽略相关一定导致标准误更小、P 值更小”改为“常见的正相关下往往低估标准误，但方向取决于相关结构与设计”。保留伪重复案例的警示力度。

- [ ] **Step 4: 更新贝叶斯与 MCMC 诊断表述**

第 20 章删除重复的错误 P 值定义。保留标准贝叶斯后验概率解释，同时说明其依赖似然与先验。把“频率学派不能回答”改为“标准频率学派置信区间不直接给出参数后验概率；频率学派决策理论可以在损失函数下形成决策规则”。

```markdown
R-hat 比较链内与链间变异。它接近 1 是必要条件，不是收敛证明。实践中应以 1.01 左右作为警戒线，并结合秩标准化 R-hat、有效样本量、链图和发散诊断判断。
```

- [ ] **Step 5: 重写方法地图中的机械替代规则**

把“t 检验不满足正态就换秩检验”的两行改为先写目标量和设计条件。

```markdown
| 独立两组的位置或随机优势 | Mann-Whitney U / 置换方法 | 先说明目标量；只有分布形状相近时才解释为位置差异 |
| 配对差值的位置 | Wilcoxon 符号秩 / 配对置换 | 符号秩检验要求差值分布近似对称；配对置换必须尊重交换结构 |
```

- [ ] **Step 6: 运行应用章节测试**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_content_accuracy -v`

Expected: 除审校报告测试外全部通过。

- [ ] **Step 7: 提交应用章节修改**

```powershell
git add -- chapters/15-biodiversity-data.qmd chapters/17-stats-to-action.qmd chapters/18-mixed-models.qmd chapters/20-bayesian-intro.qmd chapters/21-spatiotemporal.qmd appendices/method-map.qmd
git diff --cached --check
git commit -m "fix: qualify ecological and decision claims"
```

### Task 4: 完成全书逐文件审校记录

**Files:**
- Create: `docs/reviews/2026-07-11-textbook-content-audit.md`
- Inspect: `index.qmd`
- Inspect: `chapters/*.qmd`
- Inspect: `appendices/*.qmd`

**Interfaces:**
- Consumes: 30 个读者文件、Tasks 2 至 3 已修复问题、审校证据。
- Produces: 30 个读者文件各一行的审校状态和可复用判断依据。

- [ ] **Step 1: 建立 30 文件审校表**

报告必须使用以下列，逐文件填写，不得以“其余章节同上”代替。

```markdown
| 文件 | 结论 | 已直接修改 | 保留给作者的建议 |
|---|---|---|---|
| `index.qmd` | 通过或问题摘要 | 无或具体位置 | 无或具体判断点 |
```

- [ ] **Step 2: 对每章执行四类检查**

逐文件检查统计目标量、独立单位、模型条件和结论边界。本轮已知的可验证问题由 Tasks 2 至 3 修改。其余问题写入报告，不在没有新增设计确认的情况下扩大正文修改范围。

- [ ] **Step 3: 对附录执行接口检查**

检查方法地图是否与正文一致，术语表是否使用相同定义，R 速查和可重复模板是否会诱导错误分析。seed 附录缺内容属于结构建议，不在本轮扩写。

- [ ] **Step 4: 运行全书审校覆盖测试**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_content_accuracy.ContentAccuracyTests.test_every_reader_file_appears_in_audit_report -v`

Expected: PASS。

- [ ] **Step 5: 提交审校报告和新增的局部修正**

```powershell
git add -- docs/reviews/2026-07-11-textbook-content-audit.md
git diff --cached --name-only
git diff --cached --check
git commit -m "docs: record full textbook content audit"
```

暂存列表只能包含报告，不得包含删除的旧 HTML、生成文件、`_quarto.yml` 或用户原有修改。

### Task 5: Humanizer 与内容验证

**Files:**
- Modify: every reader-facing file changed in Tasks 2 to 4
- Test: `tests/test_content_accuracy.py`
- Test: existing `tests/test_*.py`

**Interfaces:**
- Consumes: 全部内容修改。
- Produces: 可交付的自然中文和通过的项目测试。

- [ ] **Step 1: 对每个触及文件完成 humanizer draft**

逐段保留原信息，删除模板过渡、规则三连、过度加粗、空泛收束和未经限定的绝对词。不得把教材锐度磨成中性说明书。

- [ ] **Step 2: 回答残留检查问题并完成 final**

对每个文件回答“哪些段落仍明显像 AI 生成”，重点看均匀句长、镜像排比、连续的“关键/核心/致命”和每节机械小结。根据答案再修一次。

- [ ] **Step 3: 运行文本红线扫描**

Run: `rg -n "—|–|在.{0,20}背景下|值得注意的是|综上所述|鲁棒性" index.qmd chapters appendices -g "*.qmd"`

Expected: 不出现新命中；历史代码或数学负号命中逐条判断，不做无意义替换。

- [ ] **Step 4: 运行内容测试与项目测试**

Run: `$env:PYTHONPATH='.'; python -m unittest discover -s tests -v`

Expected: PASS；依赖 `_site` 但尚未重新渲染的测试可按其装饰器跳过，不能失败。

- [ ] **Step 5: 运行差异检查并提交 humanizer 修订**

```powershell
git diff --check
git add -- chapters/01-role-of-statistics.qmd chapters/05-descriptive-statistics.qmd chapters/06-sampling-error.qmd chapters/08-two-group-comparison.qmd chapters/09-anova.qmd chapters/11-correlation-regression.qmd chapters/15-biodiversity-data.qmd chapters/17-stats-to-action.qmd chapters/18-mixed-models.qmd chapters/20-bayesian-intro.qmd chapters/21-spatiotemporal.qmd appendices/method-map.qmd docs/reviews/2026-07-11-textbook-content-audit.md tests/test_content_accuracy.py
git diff --cached --check
git commit -m "edit: humanize audited textbook passages"
```
