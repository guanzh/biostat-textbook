# Teaching Animations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修订 2 个现有 huashu-design 动画，新增 4 个 10 秒教学动画，并响应式嵌入第 3、5、6、8、16、19 章。

**Architecture:** 每个动画保持单文件、无网络依赖的 Canvas HTML，沿用同一逻辑画布、时间轴、播放控件和录制接口。Quarto 章节只通过统一 `.teaching-animation` 容器嵌入，正文负责概念定义与边界，动画只展示一个动态关系。源文件测试验证技术契约、关键教学文字和嵌入位置，整书渲染验证资源复制。

**Tech Stack:** HTML5 Canvas、原生 JavaScript、CSS、Quarto raw HTML、Python `unittest`

## Global Constraints

- 6 个动画均为单文件 HTML，不加载字体、脚本、样式或媒体网络资源。
- 逻辑画布固定为 1920×1080，主叙事固定为 10 秒。
- 视觉风格沿用 `animations/normal-distribution.html` 和 `animations/p-value.html` 的深灰背景、陶土色强调、中文无衬线字体和右下角 `Created by Huashu-Design` 水印。
- 每个文件提供播放、暂停、重播、时间显示、拖动、空格键、R 键和左右方向键。
- 每个文件设置 `window.__ready`，并在 `window.__recording` 为真时停在结尾帧。
- Canvas 提供文本后备说明；iframe 提供 `title` 和新窗口链接。
- 动画不播放声音，不在章节加载时自动夺取键盘焦点。
- 不提交 `_site`、渲染 HTML、TeX、日志或缓存。
- 不覆盖工作区已有的 `_quarto.yml` 改动；只有资源复制失败且无法通过链接发现解决时才单独报告。

---

### Task 1: 建立动画技术与教学契约测试

**Files:**
- Create: `tests/test_teaching_animations.py`
- Inspect: `animations/*.html`
- Inspect: target `chapters/*.qmd`
- Inspect: `styles.css`

**Interfaces:**
- Consumes: 6 个固定动画文件名和 6 个固定章节嵌入点。
- Produces: `TeachingAnimationSourceTests`，后续每个动画任务都运行对应测试。

- [ ] **Step 1: 写入会失败的动画契约测试**

```python
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANIMATIONS = {
    "experimental-unit.html": ("实验单位", "32", "160"),
    "normal-distribution.html": ("正态分布", "μ", "σ"),
    "sampling-distribution.html": ("抽样分布", "标准误", "√n"),
    "p-value.html": ("双侧 p 值", "同样或更极端", "效应大小"),
    "baci-interaction.html": ("BACI", "变化之差", "共同时间趋势"),
    "occupancy-detection.html": ("占域与探测", "(1 − p)ᴷ", "重复调查"),
}
EMBEDS = {
    "chapters/03-experimental-design.qmd": "experimental-unit.html",
    "chapters/05-descriptive-statistics.qmd": "normal-distribution.html",
    "chapters/06-sampling-error.qmd": "sampling-distribution.html",
    "chapters/08-two-group-comparison.qmd": "p-value.html",
    "chapters/16-treatment-evaluation.qmd": "baci-interaction.html",
    "chapters/19-ecological-processes.qmd": "occupancy-detection.html",
}


class TeachingAnimationSourceTests(unittest.TestCase):
    def test_all_animation_files_follow_runtime_contract(self):
        for filename, labels in ANIMATIONS.items():
            path = ROOT / "animations" / filename
            self.assertTrue(path.exists(), filename)
            html = path.read_text(encoding="utf-8")
            self.assertIn("const STAGE_W", html)
            self.assertRegex(html, r"STAGE_W\s*=\s*1920")
            self.assertRegex(html, r"STAGE_H\s*=\s*1080")
            self.assertRegex(html, r"DURATION\s*=\s*10")
            self.assertIn("window.__ready", html)
            self.assertIn("window.__recording", html)
            self.assertIn("Created by Huashu-Design", html)
            self.assertIn('id="btnPlay"', html)
            self.assertIn('id="btnReplay"', html)
            self.assertIn('id="scrubber"', html)
            self.assertNotRegex(html, r'https?://')
            for label in labels:
                self.assertIn(label, html, f"{filename} missing {label}")

    def test_animation_canvas_has_accessible_fallback(self):
        for filename in ANIMATIONS:
            html = (ROOT / "animations" / filename).read_text(encoding="utf-8")
            self.assertRegex(html, r'<canvas[^>]+aria-label="[^"]+"')
            self.assertIn('class="sr-only"', html)

    def test_each_target_chapter_has_one_responsive_embed(self):
        for chapter, filename in EMBEDS.items():
            source = (ROOT / chapter).read_text(encoding="utf-8")
            self.assertEqual(source.count(filename), 2)
            self.assertEqual(source.count('class="teaching-animation"'), 1)
            self.assertRegex(
                source,
                rf'<iframe[^>]+src="\.\./animations/{re.escape(filename)}"[^>]+title="[^"]+"',
            )

    def test_global_styles_define_responsive_animation_frame(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        for fragment in (
            ".teaching-animation",
            "aspect-ratio: 16 / 9",
            ".teaching-animation iframe",
            ".teaching-animation-link",
        ):
            self.assertIn(fragment, css)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认失败原因正确**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_teaching_animations -v`

Expected: 因 4 个新文件、无障碍后备、章节嵌入和 CSS 缺失而失败。

- [ ] **Step 3: 提交动画契约测试**

```powershell
git add -- tests/test_teaching_animations.py
git diff --cached --check
git commit -m "test: define teaching animation contracts"
```

### Task 2: 修订正态分布动画

**Files:**
- Modify: `animations/normal-distribution.html`
- Test: `tests/test_teaching_animations.py`

**Interfaces:**
- Consumes: 现有 `normalPDF`、`draw(t)`、10 秒时间轴和播放控件。
- Produces: 无异常值阈值暗示、带教学边界说明的正态分布动画。

- [ ] **Step 1: 给 Canvas 增加无障碍说明**

```html
<canvas id="mainCanvas" aria-label="正态分布动画。均值改变曲线位置，标准差改变曲线宽度，阴影面积表示均值附近的概率。"></canvas>
<p class="sr-only">动画展示标准正态曲线、均值、标准差和曲线下面积。原始数据不必服从正态分布，使用分布假设前要说明它针对哪一层随机量。</p>
```

```css
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
```

- [ ] **Step 2: 固定五阶段时间轴**

```javascript
// 0.0–1.0 标题；1.0–3.0 绘制曲线；3.0–5.0 标出 μ；
// 5.0–8.5 依次展示 ±1σ、±2σ、±3σ 面积；8.5–10.0 给出边界提示。
```

结束帧必须出现以下文字，不新增“超出 3σ 就是异常值”。

```javascript
ctx.fillText('先问清：分布假设针对原始值，还是模型残差？', W/2, H - 126);
```

- [ ] **Step 3: 运行单文件契约测试**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_teaching_animations.TeachingAnimationSourceTests.test_all_animation_files_follow_runtime_contract tests.test_teaching_animations.TeachingAnimationSourceTests.test_animation_canvas_has_accessible_fallback -v`

Expected: 正态分布文件相关断言通过，测试仍因其他动画未完成而失败。

- [ ] **Step 4: 提交正态分布动画**

```powershell
git add -- animations/normal-distribution.html
git diff --cached --check
git commit -m "fix: reframe normal distribution animation"
```

### Task 3: 修订双侧 P 值动画

**Files:**
- Modify: `animations/p-value.html`
- Test: `tests/test_teaching_animations.py`

**Interfaces:**
- Consumes: 现有标准正态零分布、`Z_OBS = 2.15`、`P_VAL = 0.0316`。
- Produces: 明确“同样或更极端”且不自动给出管理决策的双侧 P 值动画。

- [ ] **Step 1: 增加无障碍说明**

```html
<canvas id="mainCanvas" aria-label="双侧 P 值动画。零假设分布两端从正负 2.15 起的总面积为 0.0316。"></canvas>
<p class="sr-only">双侧 P 值是在零假设及模型条件成立时，检验统计量达到正负 2.15 或更极端位置的总概率。它不是零假设为真的概率，也不表示效应大小。</p>
```

- [ ] **Step 2: 改写尾部和结束帧**

时间轴使用以下教学文字。

```javascript
ctx.fillText('与 |z| = 2.15 同样或更极端', W/2, H - 205);
ctx.fillText('p = P(|Z| ≥ 2.15 | H₀) = 0.0316', W/2, H - 135);
ctx.fillText('P 值描述数据与模型的相容程度，不表示效应大小', W/2, H - 82);
```

删除以下旧结尾。

```text
p = 0.0316 < α = 0.05 → 拒绝 H₀
观测结果落在拒绝域内，有统计学显著性
```

- [ ] **Step 3: 运行 P 值文字检查**

Run: `rg -n "同样或更极端|效应大小|拒绝域内|自动决策" animations/p-value.html`

Expected: 命中新表述，不命中“拒绝域内”。

- [ ] **Step 4: 提交 P 值动画**

```powershell
git add -- animations/p-value.html
git diff --cached --check
git commit -m "fix: correct p value animation narrative"
```

### Task 4: 制作实验单位与伪重复动画

**Files:**
- Create: `animations/experimental-unit.html`
- Test: `tests/test_teaching_animations.py`

**Interfaces:**
- Consumes: 第 3 章黄黄草案例的 8 区组、32 小区、每小区 5 株幼苗。
- Produces: 10 秒、1920×1080、独立单文件的单位层级动画。

- [ ] **Step 1: 复制 huashu-design 运行外壳**

以 `animations/normal-distribution.html` 为外壳，保留 `resize`、`tick`、`updateControls`、播放、重播、拖动和键盘事件。将标题、无障碍文本和 `draw(t)` 全部替换，不保留正态曲线代码。

```html
<title>实验单位与伪重复 · Experimental Unit</title>
<canvas id="mainCanvas" aria-label="实验单位动画。32 个小区各测量 5 株幼苗，共有 160 条观测，但处理只在 32 个小区上独立分配。"></canvas>
<p class="sr-only">动画先展示 32 个独立小区，再展开每个小区内的 5 株幼苗。160 条观测不能当作 160 个独立处理重复。</p>
```

- [ ] **Step 2: 实现四阶段绘图**

```javascript
// 0.0–1.0 标题
// 1.0–3.5 画 8 行×4 列小区，标签 n = 32 个实验单位
// 3.5–6.5 每个小区展开 5 株幼苗，标签 160 条观测
// 6.5–8.5 错误地拆散 160 点，再用共享边界收回 32 组
// 8.5–10.0 显示：处理在哪一层独立分配，n 就从哪一层开始数
```

每株幼苗的位置由 `plotIndex` 和 `plantIndex` 计算，不使用随机数，保证录制可重复。

- [ ] **Step 3: 运行实验单位契约测试**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_teaching_animations.TeachingAnimationSourceTests.test_all_animation_files_follow_runtime_contract -v`

Expected: `experimental-unit.html` 的尺寸、时长、接口和关键词断言通过。

- [ ] **Step 4: 提交实验单位动画**

```powershell
git add -- animations/experimental-unit.html
git diff --cached --check
git commit -m "feat: animate experimental units and pseudoreplication"
```

### Task 5: 制作抽样分布与标准误动画

**Files:**
- Create: `animations/sampling-distribution.html`
- Test: `tests/test_teaching_animations.py`

**Interfaces:**
- Consumes: `SE = σ / √n` 的理想化独立同分布示例。
- Produces: 同一总体下 `n = 4, 16, 64` 的均值分布收窄动画。

- [ ] **Step 1: 建立固定样本和均值数据**

不在帧循环中调用 `Math.random()`。使用确定性伪随机生成器预生成 90 个样本均值。

```javascript
function mulberry32(seed){return function(){let t=seed+=0x6D2B79F5;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296}}
function normalFrom(rng){const u=Math.max(rng(),1e-9),v=rng();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v)}
function sampleMeans(n,count,seed){const rng=mulberry32(seed);return Array.from({length:count},()=>{let sum=0;for(let i=0;i<n;i++)sum+=normalFrom(rng);return sum/n})}
```

- [ ] **Step 2: 实现时间轴**

```javascript
// 0.0–1.0 标题
// 1.0–3.0 从固定总体抽 n=4，均值点形成较宽分布
// 3.0–5.5 切换 n=16，均值分布收窄
// 5.5–8.0 切换 n=64，均值分布进一步收窄
// 8.0–10.0 同屏比较 σ 与 SE=σ/√n，并显示“个体差异没有变”
```

- [ ] **Step 3: 核对理论比例**

代码中必须明确写出以下值。

```javascript
const CASES=[
  {n:4,se:0.5},
  {n:16,se:0.25},
  {n:64,se:0.125}
];
```

- [ ] **Step 4: 运行并提交**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_teaching_animations.TeachingAnimationSourceTests.test_all_animation_files_follow_runtime_contract -v`

```powershell
git add -- animations/sampling-distribution.html
git diff --cached --check
git commit -m "feat: animate sampling distributions and standard error"
```

### Task 6: 制作 BACI 变化之差动画

**Files:**
- Create: `animations/baci-interaction.html`
- Test: `tests/test_teaching_animations.py`

**Interfaces:**
- Consumes: 第 16 章修复地与对照地前后比较。
- Produces: 共同趋势为 1、修复地额外变化为 3、BACI 效果为 3 的确定性动画。

- [ ] **Step 1: 固定示例数值和公式**

```javascript
const CONTROL={before:12,after:13};
const RESTORED={before:12,after:16};
const BACI=(RESTORED.after-RESTORED.before)-(CONTROL.after-CONTROL.before); // 3
```

- [ ] **Step 2: 实现五阶段时间轴**

```javascript
// 0.0–1.0 标题
// 1.0–3.0 画修复前两个相同起点
// 3.0–5.0 对照 12→13，修复 12→16
// 5.0–7.0 单独高亮共同时间变化 +1
// 7.0–9.0 计算 (16−12)−(13−12)=3
// 9.0–10.0 显示“单纯前后比较把共同时间趋势算进措施效果”
```

- [ ] **Step 3: 运行并提交**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_teaching_animations.TeachingAnimationSourceTests.test_all_animation_files_follow_runtime_contract -v`

```powershell
git add -- animations/baci-interaction.html
git diff --cached --check
git commit -m "feat: animate BACI difference in differences"
```

### Task 7: 制作占域与探测动画

**Files:**
- Create: `animations/occupancy-detection.html`
- Test: `tests/test_teaching_animations.py`

**Interfaces:**
- Consumes: 第 19 章 `p = 0.5`、6 次重复调查、全漏检概率 1.5625%。
- Produces: 区分潜在占域状态与观测结果的确定性动画。

- [ ] **Step 1: 固定检测历史和概率序列**

```javascript
const P_DETECT=0.5;
const HISTORY=[0,1,0,0,1,0];
const missProb=Array.from({length:6},(_,i)=>Math.pow(1-P_DETECT,i+1));
```

- [ ] **Step 2: 实现时间轴**

```javascript
// 0.0–1.0 标题
// 1.0–2.5 动物已占据样点，z=1
// 2.5–6.5 依次播放 6 次相机调查和 HISTORY
// 6.5–8.5 展示从 (1−p) 到 (1−p)^6=1.6% 的全漏检概率
// 8.5–10.0 显示“重复调查提供观测过程信息，不保证每次检出”
```

- [ ] **Step 3: 运行并提交**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_teaching_animations.TeachingAnimationSourceTests.test_all_animation_files_follow_runtime_contract -v`

```powershell
git add -- animations/occupancy-detection.html
git diff --cached --check
git commit -m "feat: animate occupancy and detection"
```

### Task 8: 嵌入章节并添加响应式样式

**Files:**
- Modify: `styles.css`
- Modify: `chapters/03-experimental-design.qmd`
- Modify: `chapters/05-descriptive-statistics.qmd`
- Modify: `chapters/06-sampling-error.qmd`
- Modify: `chapters/08-two-group-comparison.qmd`
- Modify: `chapters/16-treatment-evaluation.qmd`
- Modify: `chapters/19-ecological-processes.qmd`
- Test: `tests/test_teaching_animations.py`

**Interfaces:**
- Consumes: 6 个已完成动画文件。
- Produces: 统一 iframe DOM、响应式样式、观看任务和后备链接。

- [ ] **Step 1: 添加统一 CSS**

```css
.teaching-animation {
  margin: 1.5rem 0;
}
.teaching-animation-frame {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: #1a1d20;
  border: 1px solid var(--line);
  border-radius: 8px;
}
.teaching-animation iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
}
.teaching-animation-link {
  margin: 0.45rem 0 0;
  color: var(--ink-muted);
  font-size: 0.88rem;
}
```

- [ ] **Step 2: 在每章插入统一 HTML**

每章使用以下结构，`TITLE` 和 `FILE` 替换为具体动画。文件名必须在 `src` 和链接中各出现一次。

```html
<div class="teaching-animation">
  <div class="teaching-animation-frame">
    <iframe src="../animations/FILE" title="TITLE" loading="lazy" allowfullscreen></iframe>
  </div>
  <p class="teaching-animation-link"><a href="../animations/FILE" target="_blank" rel="noopener">在新窗口打开动画</a></p>
</div>
```

插入位置严格遵守设计说明。每个 iframe 前保留一句观看任务，后面保留一句概念边界。

- [ ] **Step 3: 运行源文件契约测试**

Run: `$env:PYTHONPATH='.'; python -m unittest tests.test_teaching_animations -v`

Expected: 全部 PASS。

- [ ] **Step 4: 提交章节集成**

```powershell
git add -- styles.css chapters/03-experimental-design.qmd chapters/05-descriptive-statistics.qmd chapters/06-sampling-error.qmd chapters/08-two-group-comparison.qmd chapters/16-treatment-evaluation.qmd chapters/19-ecological-processes.qmd
git diff --cached --check
git commit -m "feat: embed teaching animations in textbook chapters"
```

### Task 9: 视觉检查、整书渲染与最终验证

**Files:**
- Modify: animation or chapter files only when validation finds a defect
- Test: `tests/test_teaching_animations.py`
- Test: existing `tests/test_*.py`

**Interfaces:**
- Consumes: 完成的 6 个动画和章节集成。
- Produces: 桌面、移动端和 Quarto 渲染均可用的交付版本。

- [ ] **Step 1: 启动每个动画并截取关键帧**

对每个动画检查 `t = 0`、概念转折帧和 `t = 9.9`。确认无文字遮挡、数值错误、闪烁、裁切或低对比文本。

- [ ] **Step 2: 检查交互控件**

逐个验证播放、暂停、重播、进度拖动、空格、R、左右方向键。将浏览器宽度缩到 390 px，确认画布与控件仍在视口内。

- [ ] **Step 3: 离线检查**

断开网络或阻止网络请求后重新打开 6 个文件。浏览器控制台不得出现外部字体、脚本或图片请求。

- [ ] **Step 4: 渲染整书 HTML**

Run: `quarto render`

Expected: 退出码 0；`_site/animations/` 下存在 6 个 HTML；6 个目标章节的渲染页都包含 `.teaching-animation`。

- [ ] **Step 5: 运行完整测试**

Run: `$env:PYTHONPATH='.'; python -m unittest discover -s tests -v`

Expected: PASS。

- [ ] **Step 6: 检查工作区边界**

Run: `git diff --check`

Expected: 无空白错误。`git status --short` 中 `_site`、渲染 HTML、TeX、日志和缓存保持未暂存，不进入提交。

- [ ] **Step 7: 提交验证修正**

```powershell
git add -- animations/experimental-unit.html animations/normal-distribution.html animations/sampling-distribution.html animations/p-value.html animations/baci-interaction.html animations/occupancy-detection.html styles.css chapters/03-experimental-design.qmd chapters/05-descriptive-statistics.qmd chapters/06-sampling-error.qmd chapters/08-two-group-comparison.qmd chapters/16-treatment-evaluation.qmd chapters/19-ecological-processes.qmd tests/test_teaching_animations.py
git diff --cached --check
git commit -m "fix: polish teaching animation playback and layout"
```
