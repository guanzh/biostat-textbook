# 三专业分版说明

本书按野保 / 森保 / 植保三个方向分版渲染。三个方向共用同一套章节源文件，差异只在于章节组合。

## 渲染命令

```bash
export PATH="/d/Program Files/R/R-4.6.1/bin:/d/Program Files/RStudio/resources/app/bin/quarto/bin:$PATH"
quarto render --profile wildlife   # 野保版 → _site-wildlife/
quarto render --profile forest     # 森保版 → _site-forest/
quarto render --profile plant      # 植保版 → _site-plant/
```

不带 `--profile` 的 `quarto render` 只出共享核心（第一至三篇），不是完整书。

## 章节组合

| 章 | 野保 | 森保 | 植保 |
|---|---|---|---|
| 第 1–12 章（第一至三篇） | ✓ | ✓ | ✓ |
| 第 13 章 森林病虫害防治试验 | — | ✓ | — |
| 第 13 章 植物保护田间药效试验 | — | — | ✓ |
| 第 14 章 野生动物调查与监测 | ✓ | — | — |
| 第 15 章 生物多样性与群落数据 | ✓ | ✓ | — |
| 第 16 章 措施效果与保护评估 | ✓ | ✓ | ✓ |
| 第 17 章 从统计结果到保护行动 | ✓ | ✓ | ✓ |
| 第 18–22 章（第五篇） | ✓ | ✓ | ✓ |
| 附录 ×7 | ✓ | ✓ | ✓ |

## 结构规则

- 基础 `_quarto.yml` 只放三个方向共用的第一至三篇；各 profile（`_quarto-wildlife.yml` / `_quarto-forest.yml` / `_quarto-plant.yml`）**追加**自己的第四篇、第五篇和附录。Quarto 对 profile 的章节列表是拼接而非替换——不要在 profile 里重复基础清单。
- 章节号保留硬编码（`tests/test_chapter_three_layout.py` 锁定了这一约定）。跨版本跳号是有意的：缺掉的号代表"那是别的专业的章"。
- 拆分出来的两个第 13 章共用编号，它们永远不会出现在同一本书里。
- 共享章节里引用别的版本才有的章时，带版本标注，例如「第 14 章（野保版）」。
- 版本结构契约在 `tests/test_book_versions.py`；改章节组合时同步更新它。
- 三个 profile 的第五篇和附录清单必须逐字一致（测试强制）。
- 植保章数据集 `data/teaching/plant_trial_long.csv`（项目 E，生成种子 `20260815`）已纳入 `DATA_DICTIONARY.md` 第 6 节和 `test_teaching_data_contract.py`。
