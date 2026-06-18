# Chapter One Cover and Reading Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将第一章拆成“独立全屏封面页 → 正文阅读页”两个连续 Quarto 页面，并让正文完整采用已确认的“清爽自然手账”设计系统。

**Architecture:** 新建 `01-role-of-statistics-cover.qmd` 作为书内独立封面，通过 `_quarto.yml` 将它排在现有第一章正文之前；现有 `01-role-of-statistics.qmd` 保留正文职责并移除全部旧封面 CSS/HTML。全局组件继续集中在 `styles.css`，封面使用一张本地生成的手绘生态插图，正文使用可复用的路线、学习目标、观察问题、数据图、黑豹提醒、关键判断和练习组件。

**Tech Stack:** Quarto Book 1.9.37、Markdown/QMD、HTML/CSS、SVG 数据图、OpenAI Image Generation、Python `unittest`、Codex in-app Browser

---

## File Map

- Create: `chapters/01-role-of-statistics-cover.qmd` — 第一章独立封面与进入正文的链接。
- Modify: `chapters/01-role-of-statistics.qmd` — 删除旧封面，重排为第一章正文阅读页，并修正关键统计表述。
- Modify: `_quarto.yml` — 将封面页放在正文页之前，同时保留当前未提交的 EPUB/PDF 配置改动。
- Modify: `styles.css` — 增加封面与正文组件样式，修复全局阅读宽度作用域，移除在线字体依赖。
- Create: `images/chapter-openers/ch01-statistics-evidence.png` — 第一章章首手绘生态封面图。
- Create: `images/figures/ch01-flowering-paired-plot.svg` — 10 个固定样地两年开花个体数的配对变化示意图。
- Create: `tests/test_chapter_one_layout.py` — 页面顺序、组件使用、资源存在性和渲染结果的结构回归测试。

## Task 1: Add Failing Structural Tests

**Files:**
- Create: `tests/test_chapter_one_layout.py`
- Test: `tests/test_chapter_one_layout.py`

- [ ] **Step 1: Create the structure test file**

```python
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BOOK_CONFIG = ROOT / "_quarto.yml"
COVER_QMD = ROOT / "chapters" / "01-role-of-statistics-cover.qmd"
CONTENT_QMD = ROOT / "chapters" / "01-role-of-statistics.qmd"
STYLES = ROOT / "styles.css"
COVER_IMAGE = ROOT / "images" / "chapter-openers" / "ch01-statistics-evidence.png"
PAIRED_PLOT = ROOT / "images" / "figures" / "ch01-flowering-paired-plot.svg"


class ChapterOneSourceTests(unittest.TestCase):
    def test_cover_precedes_content_in_book(self):
        config = BOOK_CONFIG.read_text(encoding="utf-8")
        cover = "- chapters/01-role-of-statistics-cover.qmd"
        content = "- chapters/01-role-of-statistics.qmd"
        self.assertIn(cover, config)
        self.assertIn(content, config)
        self.assertLess(config.index(cover), config.index(content))

    def test_cover_page_links_to_reading_page(self):
        source = COVER_QMD.read_text(encoding="utf-8")
        self.assertIn("{.chapter-cover}", source)
        self.assertIn("01-role-of-statistics.qmd", source)
        self.assertIn("ch01-statistics-evidence.png", source)
        self.assertIn("toc: false", source)

    def test_content_uses_design_system_without_inline_css(self):
        source = CONTENT_QMD.read_text(encoding="utf-8")
        self.assertNotIn("<style>", source)
        self.assertNotIn("ch1-fig", source)
        for component in (
            "chapter-route",
            "learning-goals",
            "observation-question",
            "evidence-figure",
            "mascot-note",
            "key-judgment",
            "practice-block",
            "chapter-next",
        ):
            self.assertIn(component, source)

    def test_global_styles_define_cover_and_components(self):
        css = STYLES.read_text(encoding="utf-8")
        self.assertNotIn("fonts.googleapis.com", css)
        for selector in (
            ".chapter-cover",
            ".chapter-cover-copy",
            ".chapter-cover-enter",
            ".chapter-route",
            ".evidence-figure",
            ".mascot-note",
        ):
            self.assertIn(selector, css)

    def test_visual_assets_exist(self):
        self.assertGreater(COVER_IMAGE.stat().st_size, 100_000)
        self.assertGreater(PAIRED_PLOT.stat().st_size, 1_000)


class ChapterOneRenderedTests(unittest.TestCase):
    def test_rendered_pages_exist_and_link_forward(self):
        cover_html = ROOT / "_site" / "chapters" / "01-role-of-statistics-cover.html"
        content_html = ROOT / "_site" / "chapters" / "01-role-of-statistics.html"
        self.assertTrue(cover_html.exists())
        self.assertTrue(content_html.exists())
        rendered_cover = cover_html.read_text(encoding="utf-8")
        self.assertIn('href="01-role-of-statistics.html"', rendered_cover)
        self.assertIn("chapter-cover", rendered_cover)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify the expected failures**

Run:

```powershell
python -m unittest tests/test_chapter_one_layout.py -v
```

Expected: source tests fail because the cover QMD, cover image, paired plot and cover CSS do not exist; rendered tests fail because `_site` has not been generated.

## Task 2: Generate the Chapter Cover Illustration

**Files:**
- Create: `images/chapter-openers/ch01-statistics-evidence.png`
- Test: `tests/test_chapter_one_layout.py`

- [ ] **Step 1: Generate one landscape cover illustration with Image Generation**

Use this exact prompt:

```text
Wide 3:2 hand-drawn scientific field-notebook illustration for a Chinese conservation biostatistics textbook chapter cover. Show a clearly recognizable endangered flowering herb population inside several fixed quadrats in a mountain nature reserve; two conservation researchers quietly count flowering individuals and record observations on a clipboard; subtle visual hints of repeated monitoring and paired data points appear on the clipboard only as marks, with no readable text. Include the book's small black panther guide character at the far right edge, attentive but not dominant. Pencil-and-watercolor linework, clean natural observation journal style, white and very pale green paper background, forest green, moss, mustard yellow, lake blue and coral accents. Reserve calm light negative space on the left half for dark Chinese title text placed later in HTML. The plant, quadrats and researchers must be fully visible and scientifically plausible. No embedded words, no labels, no typography, no gradient, no dark mood, no blur, no decorative blobs, no border, no frame, no cropped subjects.
```

Save the generated result exactly as:

```text
images/chapter-openers/ch01-statistics-evidence.png
```

- [ ] **Step 2: Inspect the image**

Verify that the left side has sufficient quiet space for the chapter title, the ecological subject is visible without cropping, the black panther is secondary, and the image contains no generated text.

- [ ] **Step 3: Run the asset test**

Run:

```powershell
python -m unittest tests.test_chapter_one_layout.ChapterOneSourceTests.test_visual_assets_exist -v
```

Expected: still FAIL because the paired plot has not yet been created; the cover image itself must be larger than 100 KB.

## Task 3: Create the Standalone Cover Page and Book Route

**Files:**
- Create: `chapters/01-role-of-statistics-cover.qmd`
- Modify: `_quarto.yml`
- Test: `tests/test_chapter_one_layout.py`

- [ ] **Step 1: Create the standalone cover QMD**

```markdown
---
title: "第 1 章 统计学在保护中的角色"
maturity: budding
updated: 2026-06-18
toc: false
page-layout: full
---

:::: {.chapter-cover}
::: {.chapter-cover-media}
<img class="chapter-cover-image" src="../images/chapter-openers/ch01-statistics-evidence.png" alt="保护区内的濒危草本植物固定样地监测场景，研究人员正在记录开花个体数">
:::

::: {.chapter-cover-copy}
<span class="chapter-cover-kicker">第一篇 · 从保护问题进入统计</span>

<h1>第 1 章<br>统计学在保护中的角色</h1>

<p>从“我感觉花少了”，走向“我们有多强的证据”。</p>
:::

::: {.chapter-cover-foot}
[开始本章 →](01-role-of-statistics.qmd){.chapter-cover-enter}

<span>观察现象 · 识别不确定性 · 形成证据 · 支持行动</span>
:::
::::
```

- [ ] **Step 2: Insert the cover before the content page in `_quarto.yml`**

Change only the first part's chapter list to:

```yaml
    - part: "第一篇：从保护问题进入统计"
      chapters:
        - chapters/01-role-of-statistics-cover.qmd
        - chapters/01-role-of-statistics.qmd
        - chapters/02-variables-hypotheses.qmd
        - chapters/03-experimental-design.qmd
```

Do not revert the existing uncommitted change that keeps only `downloads: [epub]` and removes the PDF format.

- [ ] **Step 3: Run the route tests**

Run:

```powershell
python -m unittest tests.test_chapter_one_layout.ChapterOneSourceTests.test_cover_precedes_content_in_book tests.test_chapter_one_layout.ChapterOneSourceTests.test_cover_page_links_to_reading_page -v
```

Expected: PASS.

## Task 4: Convert the Existing File into the Reading Page

**Files:**
- Modify: `chapters/01-role-of-statistics.qmd`
- Test: `tests/test_chapter_one_layout.py`

- [ ] **Step 1: Change the page title and remove the legacy cover**

Change the YAML title to:

```yaml
title: "1.1 为什么保护工作需要统计学"
```

Delete the explanatory HTML comment and the complete raw HTML block from the opening ```` ```{=html} ```` line through its closing fence. The first content after YAML must be the chapter route below.

- [ ] **Step 2: Add the five-step route before learning goals**

```html
<div class="chapter-route" aria-label="本节学习路线">
  <div><strong>观察现象</strong><span>23 株降到 17 株</span></div>
  <div><strong>识别不确定性</strong><span>过程、抽样与检测</span></div>
  <div><strong>描述与估计</strong><span>变化有多大</span></div>
  <div><strong>推断与预测</strong><span>证据能走多远</span></div>
  <div><strong>支持行动</strong><span>证据不是决策</span></div>
</div>
```

Replace the existing learning goals with:

```markdown
::: {.learning-goals}
**学完本章后，你能够：**

1. 区分“样地中的开花个体减少”与“整个种群正在下降”两种结论。
2. 识别自然过程、抽样、测量与检测带来的不确定性。
3. 解释描述、估计、比较、推断和预测如何形成保护证据链。
4. 评价统计证据与保护行动之间的关系。
:::
```

- [ ] **Step 3: Tighten the opening case's scope of inference**

Replace the sentence `这个问题，就是统计学要回答的。` with:

```markdown
目前的数据首先说明：**这 10 个固定样地中的开花个体平均数下降了。** 它是否代表整个保护区的开花个体减少，是否进一步意味着种群数量下降，还取决于样地代表性、逐样地变化、检测过程和更长时间的监测。统计学能够帮助我们量化其中的证据，但不能独自决定结论和行动。
```

- [ ] **Step 4: Replace the four-role taxonomy with a coherent evidence chain**

Change the section title to:

```markdown
## 统计学怎样进入保护证据链
```

Replace the section's opening paragraph with:

```markdown
从观测到行动，统计学并不是一张互不相干的方法清单，而是一条反复更新的证据链。我们先描述看到了什么，再估计变化有多大；随后判断样本中的模式能否推广，或预测未来可能发生什么；最后把统计证据与成本、风险和保护目标放在一起考虑。
```

Use these four subsection titles:

```markdown
### 描述：现在是什么状态？
### 估计与比较：变化有多大？
### 推断与预测：证据能走多远？
### 支持行动：下一步该考虑什么？
```

Replace the first paragraph under `### 估计与比较：变化有多大？` with:

```markdown
保护工作中经常需要比较两个地方、两个时间点或两种处理，但比较不应只停留在“有没有差异”。我们还要估计差异有多大、方向是否稳定，以及这个差异的不确定范围。
```

After the corrected P-value paragraph in the next step, add:

```markdown
推断关注的是样本中的模式能否推广到更大的总体；预测关注的是在给定环境和模型条件下，未来或未观测地点可能出现什么。保护工作既需要判断当前证据，也经常需要预测种群趋势、病虫害风险和潜在分布变化。
```

In the final paragraph, refer to these as a repeating evidence chain rather than four statistical methods:

```markdown
这条证据链——描述、估计与比较、推断与预测、支持行动——不是一次性走完的直线流程。新的行动会产生新的监测数据，新的数据又会让我们重新描述状态、更新估计并修正判断。
```

- [ ] **Step 5: Replace the P-value explanation with an accurate first-chapter definition**

Use this text:

```markdown
在“处理没有真实效应”等零假设成立，并且统计模型条件满足的前提下，P 值表示观察到当前数据或更极端数据的概率。P 值较小，说明数据与零假设不太相容；它不表示零假设为真的概率，也不表示效应真实存在的概率，更不能说明效应有多大。

<div class="mascot-note">
  <img src="../images/mascot/cat-point.svg" alt="" class="mascot" aria-hidden="true">
  <div>
    <strong>黑豹提醒：P 值不是“结论正确的概率”</strong>
    <p>研究设计、样本代表性、模型条件和效应大小，都要与 P 值一起检查。</p>
  </div>
</div>
```

- [ ] **Step 6: Wrap exercises and next-page navigation in standard components**

Insert this opening fence immediately after the existing `## 练习` heading:

```markdown
:::: {.practice-block}
```

Insert this closing fence immediately after exercise 5 and immediately before the existing `## 继续学习` heading:

```markdown
::::
```

Do not alter the wording or order of the five existing exercises in this step.

Replace the current continuation link with:

```markdown
::: {.chapter-next}
下一步：把一个宽泛的保护问题拆成可以测量和检验的研究问题。

→ [第 2 章：研究问题、变量与假设](02-variables-hypotheses.qmd)
:::
```

- [ ] **Step 7: Run the content structure test**

Run:

```powershell
python -m unittest tests.test_chapter_one_layout.ChapterOneSourceTests.test_content_uses_design_system_without_inline_css -v
```

Expected: FAIL only on `evidence-figure` until Task 5 adds the paired plot.

## Task 5: Add the Paired Evidence Figure

**Files:**
- Create: `images/figures/ch01-flowering-paired-plot.svg`
- Modify: `chapters/01-role-of-statistics.qmd`
- Test: `tests/test_chapter_one_layout.py`

- [ ] **Step 1: Create an accessible SVG paired plot**

Use these illustrative fixed-plot counts so both means match the chapter case:

```text
样地:  1  2  3  4  5  6  7  8  9 10
去年: 18 20 21 22 23 23 24 25 27 27   平均 23
今年: 16 22 17 18 20 14 19 15 21  8   平均 17
```

Create `images/figures/ch01-flowering-paired-plot.svg` with this exact content:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 500" role="img" aria-labelledby="title desc">
  <title id="title">10个固定样地两年开花个体数的配对变化</title>
  <desc id="desc">去年平均每个样地23株，今年平均17株。10条连线表示同一样地两年的变化，其中9个样地下降，1个样地增加。</desc>
  <rect width="920" height="500" fill="#fcfdfc"/>
  <g font-family="Microsoft YaHei, PingFang SC, sans-serif" fill="#243129">
    <text x="80" y="42" font-size="22" font-weight="700">固定样地中的开花个体变化</text>
    <text x="80" y="68" font-size="14" fill="#59665e">每条线连接同一个样地；数据用于教学示意</text>
    <line x1="260" y1="80" x2="260" y2="430" stroke="#d6ddd8" stroke-width="2"/>
    <line x1="660" y1="80" x2="660" y2="430" stroke="#d6ddd8" stroke-width="2"/>
    <text x="260" y="466" font-size="18" text-anchor="middle" fill="#4d8294" font-weight="700">去年</text>
    <text x="660" y="466" font-size="18" text-anchor="middle" fill="#c86652" font-weight="700">今年</text>
    <g fill="#59665e" font-size="13" text-anchor="end">
      <text x="228" y="434">5</text>
      <text x="228" y="364">10</text>
      <text x="228" y="294">15</text>
      <text x="228" y="224">20</text>
      <text x="228" y="154">25</text>
      <text x="228" y="84">30</text>
    </g>
    <g stroke="#edf0ed" stroke-width="1">
      <line x1="235" y1="430" x2="685" y2="430"/>
      <line x1="235" y1="360" x2="685" y2="360"/>
      <line x1="235" y1="290" x2="685" y2="290"/>
      <line x1="235" y1="220" x2="685" y2="220"/>
      <line x1="235" y1="150" x2="685" y2="150"/>
      <line x1="235" y1="80" x2="685" y2="80"/>
    </g>
    <g stroke="#91a097" stroke-width="2" stroke-opacity="0.72">
      <line x1="246" y1="248" x2="646" y2="276"/>
      <line x1="249" y1="220" x2="649" y2="192"/>
      <line x1="252" y1="206" x2="652" y2="262"/>
      <line x1="255" y1="192" x2="655" y2="248"/>
      <line x1="258" y1="178" x2="658" y2="220"/>
      <line x1="261" y1="178" x2="661" y2="304"/>
      <line x1="264" y1="164" x2="664" y2="234"/>
      <line x1="267" y1="150" x2="667" y2="290"/>
      <line x1="270" y1="122" x2="670" y2="206"/>
      <line x1="273" y1="122" x2="673" y2="388"/>
    </g>
    <g fill="#4d8294" stroke="#ffffff" stroke-width="2">
      <circle cx="246" cy="248" r="6"/><circle cx="249" cy="220" r="6"/>
      <circle cx="252" cy="206" r="6"/><circle cx="255" cy="192" r="6"/>
      <circle cx="258" cy="178" r="6"/><circle cx="261" cy="178" r="6"/>
      <circle cx="264" cy="164" r="6"/><circle cx="267" cy="150" r="6"/>
      <circle cx="270" cy="122" r="6"/><circle cx="273" cy="122" r="6"/>
    </g>
    <g fill="#c86652" stroke="#ffffff" stroke-width="2">
      <circle cx="646" cy="276" r="6"/><circle cx="649" cy="192" r="6"/>
      <circle cx="652" cy="262" r="6"/><circle cx="655" cy="248" r="6"/>
      <circle cx="658" cy="220" r="6"/><circle cx="661" cy="304" r="6"/>
      <circle cx="664" cy="234" r="6"/><circle cx="667" cy="290" r="6"/>
      <circle cx="670" cy="206" r="6"/><circle cx="673" cy="388" r="6"/>
    </g>
    <line x1="228" y1="178" x2="292" y2="178" stroke="#4d8294" stroke-width="4"/>
    <text x="300" y="183" font-size="15" fill="#4d8294" font-weight="700">平均 23 株</text>
    <line x1="628" y1="262" x2="692" y2="262" stroke="#c86652" stroke-width="4"/>
    <text x="700" y="267" font-size="15" fill="#c86652" font-weight="700">平均 17 株</text>
    <text x="80" y="278" font-size="14" fill="#59665e" transform="rotate(-90 80 278)">开花个体数（株/样地）</text>
  </g>
</svg>
```

The axis labels identify the two years directly, so do not add a separate legend.

- [ ] **Step 2: Insert the figure after the opening observation question**

```html
<figure class="evidence-figure">
  <img src="../images/figures/ch01-flowering-paired-plot.svg" alt="10 个固定样地中，开花个体数从去年到今年的配对变化；多数样地下降，但变化幅度不同">
  <figcaption><strong>图 1.1：同样是“平均数从 23 降到 17”，逐样地变化提供了更多信息。</strong> 图中数据用于教学示意。固定样地应按配对方式观察，不能只比较两个孤立的均值。</figcaption>
</figure>
```

- [ ] **Step 3: Run all source tests**

Run:

```powershell
python -m unittest tests.test_chapter_one_layout.ChapterOneSourceTests -v
```

Expected: PASS.

## Task 6: Implement the Cover and Reading Styles

**Files:**
- Modify: `styles.css`
- Test: `tests/test_chapter_one_layout.py`

- [ ] **Step 1: Remove the online Google Fonts import**

Delete:

```css
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Architects+Daughter&family=Patrick+Hand&family=Gochi+Hand&display=swap');
```

Keep the local system-font fallbacks so older sketch components remain readable.

- [ ] **Step 2: Scope the reading width to the content column**

Replace:

```css
#quarto-content, main.content, .page-columns {
  max-width: var(--reading-width);
  margin-left: auto;
  margin-right: auto;
}
```

with:

```css
main.content {
  max-width: var(--reading-width);
  margin-left: auto;
  margin-right: auto;
}

main.content h2 {
  color: var(--ink);
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.35rem;
}
```

- [ ] **Step 3: Add the standalone cover styles**

```css
body:has(.chapter-cover) #title-block-header,
body:has(.chapter-cover) #quarto-margin-sidebar {
  display: none;
}

body:has(.chapter-cover) #quarto-content,
body:has(.chapter-cover) .page-columns,
body:has(.chapter-cover) main.content {
  max-width: none;
  width: 100%;
  margin: 0;
  padding: 0;
}

.chapter-cover {
  position: relative;
  min-height: calc(100vh - 54px);
  overflow: hidden;
  background: var(--paper-soft);
  color: var(--ink);
}

.chapter-cover-media,
.chapter-cover-media p {
  position: absolute;
  inset: 0;
  margin: 0;
}

.chapter-cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.chapter-cover-copy {
  position: absolute;
  z-index: 2;
  left: clamp(2rem, 8vw, 7rem);
  top: clamp(4rem, 16vh, 9rem);
  width: min(560px, 46vw);
}

.chapter-cover-kicker {
  display: block;
  color: var(--forest);
  font-size: 0.8rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.chapter-cover-copy h1 {
  margin: 0;
  color: var(--ink);
  font-size: clamp(2.35rem, 4.8vw, 4.8rem);
  line-height: 1.16;
  letter-spacing: 0;
}

.chapter-cover-copy p {
  margin-top: 1.2rem;
  color: var(--ink-muted);
  font-size: clamp(1rem, 1.35vw, 1.25rem);
  line-height: 1.7;
}

.chapter-cover-foot {
  position: absolute;
  z-index: 2;
  left: clamp(2rem, 8vw, 7rem);
  right: clamp(2rem, 6vw, 5rem);
  bottom: clamp(1.4rem, 5vh, 3rem);
  display: flex;
  align-items: center;
  gap: 1.5rem;
  color: var(--ink-muted);
  font-size: 0.85rem;
}

.chapter-cover-enter {
  color: var(--forest);
  font-size: 1rem;
  font-weight: 700;
  text-decoration: none;
  border-bottom: 2px solid var(--mustard);
  padding-bottom: 0.2rem;
}

.chapter-cover-enter:hover,
.chapter-cover-enter:focus-visible {
  color: var(--ink);
  border-bottom-color: var(--coral);
}
```

- [ ] **Step 4: Add the cover mobile layout**

```css
@media (max-width: 720px) {
  .chapter-cover {
    min-height: auto;
    display: flex;
    flex-direction: column;
  }

  .chapter-cover-media,
  .chapter-cover-media p {
    position: relative;
    inset: auto;
  }

  .chapter-cover-image {
    height: 46vh;
    min-height: 320px;
    object-position: 68% center;
  }

  .chapter-cover-copy,
  .chapter-cover-foot {
    position: relative;
    left: auto;
    right: auto;
    top: auto;
    bottom: auto;
    width: auto;
    padding-left: 1.25rem;
    padding-right: 1.25rem;
  }

  .chapter-cover-copy {
    padding-top: 1.5rem;
  }

  .chapter-cover-copy h1 {
    font-size: 2.15rem;
  }

  .chapter-cover-foot {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.7rem;
    padding-top: 1.3rem;
    padding-bottom: 2rem;
  }
}
```

- [ ] **Step 5: Improve the reading components' responsive layout**

Add these exact breakpoint rules after the base component styles:

```css
@media (min-width: 721px) and (max-width: 1099px) {
  .chapter-route {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .chapter-route {
    grid-template-columns: 1fr;
    gap: 0.3rem;
  }
}

@media (max-width: 420px) {
  .mascot-note {
    grid-template-columns: 1fr;
  }

  .mascot-note img.mascot {
    width: 44px;
    height: 44px;
  }
}
```

Keep every component border radius at or below 8 px.

- [ ] **Step 6: Run the CSS source test**

Run:

```powershell
python -m unittest tests.test_chapter_one_layout.ChapterOneSourceTests.test_global_styles_define_cover_and_components -v
```

Expected: PASS.

## Task 7: Render and Verify the Two-Page Flow

**Files:**
- Generated: `_site/chapters/01-role-of-statistics-cover.html`
- Generated: `_site/chapters/01-role-of-statistics.html`
- Test: `tests/test_chapter_one_layout.py`

- [ ] **Step 1: Use the same Quarto version as CI**

Use Quarto `1.9.37`, matching `.github/workflows/publish.yml`. If `quarto` is not installed, download the pinned portable release to a unique temporary directory and render with it:

```powershell
$quartoCommand = Get-Command quarto -ErrorAction SilentlyContinue
if ($quartoCommand) {
  & $quartoCommand.Source render --no-execute --to html
} else {
  $archive = Join-Path $env:TEMP "quarto-1.9.37-win.zip"
  $installRoot = Join-Path $env:TEMP "quarto-cli-1.9.37-$PID"
  Invoke-WebRequest "https://github.com/quarto-dev/quarto-cli/releases/download/v1.9.37/quarto-1.9.37-win.zip" -OutFile $archive
  Expand-Archive -LiteralPath $archive -DestinationPath $installRoot
  $quartoCommand = Get-ChildItem $installRoot -Recurse -Filter "quarto.cmd" | Select-Object -First 1
  if (-not $quartoCommand) { throw "Quarto 1.9.37 executable was not found after extraction." }
  & $quartoCommand.FullName render --no-execute --to html
}
```

Expected: exit code 0 and both chapter-one HTML files appear under `_site/chapters/`.

- [ ] **Step 2: Run all automated tests**

```powershell
python -m unittest tests/test_chapter_one_layout.py -v
```

Expected: all tests PASS.

- [ ] **Step 3: Serve the rendered book locally**

```powershell
$server = Start-Process -FilePath python -ArgumentList '-m','http.server','4310','--directory','_site' -WindowStyle Hidden -PassThru
```

Expected: `http://127.0.0.1:4310/chapters/01-role-of-statistics-cover.html` loads.

- [ ] **Step 4: Verify desktop layout in the in-app browser**

At 1280 × 900 verify:

- the cover is visually full-page and unframed;
- the title sits in the image's quiet left area without a card or gradient;
- the plant, quadrats, researchers and black panther remain visible;
- “开始本章” is visible without scrolling;
- clicking “开始本章” opens the reading page;
- the reading page has no duplicate title and no legacy sketch infographic;
- the right table of contents and book navigation remain usable;
- body text stays within a comfortable reading column.

- [ ] **Step 5: Verify mobile layout in the in-app browser**

At 390 × 844 verify:

- image, title and entry link stack in natural order;
- no Chinese title is clipped;
- the five-step route becomes one column;
- the paired plot remains readable without horizontal page overflow;
- the mascot reminder does not overlap text;
- page navigation remains reachable.

- [ ] **Step 6: Check browser errors**

Expected: no missing image, CSS, SVG or font requests; no console errors caused by the new pages.

## Task 8: Review and Commit Only This Feature

**Files:**
- All files listed in the File Map

- [ ] **Step 1: Review the diff without touching unrelated work**

```powershell
git status --short
git diff -- chapters/01-role-of-statistics-cover.qmd chapters/01-role-of-statistics.qmd styles.css images/chapter-openers/ch01-statistics-evidence.png images/figures/ch01-flowering-paired-plot.svg tests/test_chapter_one_layout.py _quarto.yml
```

Confirm that the existing modifications in Chapters 2–22, `index.log`, `index.tex` and `.hermes/` remain untouched.

- [ ] **Step 2: Stage feature-owned files**

Stage the feature files except `_quarto.yml`:

```powershell
git add -- chapters/01-role-of-statistics-cover.qmd chapters/01-role-of-statistics.qmd styles.css images/chapter-openers/ch01-statistics-evidence.png images/figures/ch01-flowering-paired-plot.svg tests/test_chapter_one_layout.py
```

Then stage only the cover-route insertion from `_quarto.yml`, leaving the user's EPUB/PDF working-tree change unstaged:

```powershell
$coverRoutePatch = @'
diff --git a/_quarto.yml b/_quarto.yml
--- a/_quarto.yml
+++ b/_quarto.yml
@@ -16,0 +17 @@
+        - chapters/01-role-of-statistics-cover.qmd
'@
$coverRoutePatch | git apply --cached --unidiff-zero --whitespace=nowarn -
```

Verify the staged `_quarto.yml` diff contains only the new cover entry:

```powershell
git diff --cached -- _quarto.yml
```

- [ ] **Step 3: Run the staged-diff check**

```powershell
git diff --cached --check
git diff --cached --stat
```

Expected: no whitespace errors; the staged files belong only to the chapter-one cover and reading-page feature.

- [ ] **Step 4: Commit**

```powershell
git commit -m "feat(ch01): split cover and reading page"
```

Expected: commit succeeds while unrelated working-tree changes remain present and unstaged.
