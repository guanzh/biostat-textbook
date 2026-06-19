"""第 3 章布局与内容回归测试。

执行计划：docs/superpowers/plans/2026-06-19-chapter-three-experimental-design.md

本测试同时验证三件事：

1. **DOM 契约**（与 ch1/ch2 同源）：`.chapter-route` 恰好 5 个 <div>
   直接子；`.mascot-note` 恰好 img + .mascot-note-copy 两个直接子。
   详见 docs/superpowers/specs/2026-06-18-textbook-page-style-design.md §5.7。
2. **章节结构契约**：frontmatter title 含「第 3 章」+ 正文不重复 H1；
   恰好 7 节正文 ## 3.X；术语完备；R 代码可复现；
   主案例核心词（黄黄草/苗圃/光照/小区/指名亚种）齐全。
3. **设计陷阱清除**：旧版"同株多叶 = 技术重复""每组 10 个"等无依据规则
   不得复活；本章只引用 1 张 SVG（单位层级），不得引入第二张。
"""

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTENT_QMD = ROOT / "chapters" / "03-experimental-design.qmd"
RENDERED_HTML = ROOT / "_site" / "chapters" / "03-experimental-design.html"
UNIT_HIERARCHY_SVG = ROOT / "images" / "figures" / "ch03-unit-hierarchy.svg"


# ---------------------------------------------------------------------------
# 复用 ch2 测试中的 _StructuredCollector（DOM 直接子元素收集器）
# 直接 import 避免重复维护两份解析器。
# ---------------------------------------------------------------------------
from tests.test_chapter_two_layout import _StructuredCollector, _extract  # noqa: E402


# ---------------------------------------------------------------------------
# 源文件检查（不需要 Quarto 渲染）
# ---------------------------------------------------------------------------
class ChapterThreeSourceTests(unittest.TestCase):
    """直接检查 .qmd 源文件，无需 Quarto 渲染。"""

    @classmethod
    def setUpClass(cls):
        if not CONTENT_QMD.exists():
            raise unittest.SkipTest(f"missing {CONTENT_QMD}")
        cls.source = CONTENT_QMD.read_text(encoding="utf-8")

    # ---- frontmatter 与标题契约 -----------------------------------------
    def test_frontmatter_title_carries_chapter_number_and_subtitle(self):
        """title 必须含「第 3 章」+「实验设计」+ 正副标题分隔（让比较产生可信证据）。"""
        m = re.search(r'(?m)^title:\s*"([^"]+)"', self.source)
        self.assertIsNotNone(m, "frontmatter 中未找到 title 字段")
        title = m.group(1)
        self.assertIn("第 3 章", title, f"title 必须含「第 3 章」，实际：{title!r}")
        self.assertIn("实验设计", title, f"title 必须含「实验设计」，实际：{title!r}")
        self.assertIn(
            "让比较产生可信证据",
            title,
            f"title 必须含副标题「让比较产生可信证据」，实际：{title!r}",
        )

    def test_no_naked_h1_in_body(self):
        """正文不得出现裸 # H1（H1 由 frontmatter title 渲染）。

        策略：去除 frontmatter 与 ```{=html}/```r 等代码块内的内容，
        然后检查剩余 Markdown 中是否还有以 '# ' 开头的行。
        """
        # 跳过首个 frontmatter 块
        body = re.sub(r"^---\n.*?\n---\n", "", self.source, count=1, flags=re.DOTALL)
        # 去掉所有 ``` 代码块
        body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
        # 检查是否还有裸 H1
        h1_lines = [
            line
            for line in body.splitlines()
            if re.match(r"^# (?!#)", line)  # 以 "# " 开头但不是 "## "
        ]
        self.assertEqual(
            h1_lines,
            [],
            f"正文不得出现裸 H1 标题（H1 由 frontmatter title 渲染），发现：{h1_lines}",
        )

    def test_body_has_exactly_seven_h2_section_headings(self):
        """正文恰好 7 个 ## 3.X 二级小节标题，覆盖计划中的 7 节。

        允许章末另有 ## 本章小结 / ## 练习 / ## 继续学习（与 ch1/ch2 一致），
        但 3.1–3.7 必须齐全。
        """
        # 收集所有 ## 开头标题（排除 ### 及更深）
        h2 = re.findall(r"(?m)^## (?!#)(.+)$", self.source)
        # 找出形如 "3.X 标题" 的核心节
        section_h2 = [h for h in h2 if re.match(r"^3\.\d+\s", h)]
        self.assertEqual(
            len(section_h2),
            7,
            f"正文应有恰好 7 个 ## 3.X 二级标题，实际 {len(section_h2)}：{section_h2}",
        )
        # 编号必须是 3.1–3.7 完整序列
        nums = sorted(int(re.match(r"^3\.(\d+)", h).group(1)) for h in section_h2)
        self.assertEqual(
            nums,
            [1, 2, 3, 4, 5, 6, 7],
            f"小节编号必须是 3.1–3.7 完整序列，实际：{nums}",
        )

    # ---- 主案例核心词 ---------------------------------------------------
    def test_main_case_core_terms_present(self):
        """主案例必须出现：黄黄草、指名亚种、苗圃、光照、小区。"""
        for term in ("黄黄草", "指名亚种", "苗圃", "光照", "小区"):
            self.assertIn(term, self.source, f"主案例缺少核心词：{term}")

    def test_continuity_with_chapter_two(self):
        """学生必须能看到本章承接第 2 章观察性研究的明确语句。

        策略：检查正文是否在某段同时提及"第 2 章"或"观察"与
        "操纵实验"/"操纵"/"主动施加"中的至少一项。
        """
        has_ch2_ref = ("第 2 章" in self.source) or ("观察" in self.source)
        has_manipulation = any(
            kw in self.source for kw in ("操纵实验", "主动施加", "主动分配")
        )
        self.assertTrue(
            has_ch2_ref and has_manipulation,
            "应在正文中明示从第 2 章观察性研究升级到本章操纵实验",
        )

    # ---- 学习目标与学习路线 ---------------------------------------------
    def test_learning_goals_use_observable_verbs(self):
        """学习目标至少 6 项，使用可观察动词（写出/区分/实施/选择/解释/识别等）。"""
        # 抓 .learning-goals 块（fenced div 写法允许）
        m = re.search(
            r":::\s*\{\.learning-goals\}(.*?):::",
            self.source,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(m, "未找到 .learning-goals 块")
        goals_block = m.group(1)
        # 计数有序列表项
        items = re.findall(r"(?m)^\s*\d+\.\s+(.+)$", goals_block)
        self.assertGreaterEqual(
            len(items),
            6,
            f"学习目标应至少 6 项，实际 {len(items)}",
        )
        # 禁止使用空泛动词
        forbidden = ("理解", "了解", "掌握")
        for verb in forbidden:
            for item in items:
                self.assertNotIn(
                    verb,
                    item,
                    f"学习目标禁止使用空泛动词「{verb}」：{item!r}",
                )

    # ---- 必备术语 -------------------------------------------------------
    def test_design_vocabulary_is_complete(self):
        for term in (
            "实验单位",
            "观测单位",
            "子抽样",
            "技术重复",
            "伪重复",
            "完全随机设计",
            "随机区组设计",
            "析因",
            "重复测量",
            "嵌套",
            "裂区",
            "最小有意义效应",
            "统计功效",
        ):
            self.assertIn(term, self.source, f"缺少必备术语：{term}")

    # ---- R 代码 ---------------------------------------------------------
    def test_randomization_code_is_reproducible(self):
        """R 代码块必须含固定种子、sample()、table() 验证。"""
        self.assertIn("set.seed(20260619)", self.source)
        self.assertIn("sample(treatments)", self.source)
        self.assertIn("table(block, treatment)", self.source)

    def test_r_code_marked_as_demo_not_required_to_run(self):
        """R 代码定位必须明确为「演示」，让无 R 环境的读者也能阅读。

        策略：R 代码块周围 600 字符内必须出现「演示」或「无需」「即可」与「输出」相关字样。
        """
        m = re.search(r"set\.seed\(20260619\)", self.source)
        self.assertIsNotNone(m)
        # 检查 600 字符上下文窗口
        start = max(0, m.start() - 600)
        end = min(len(self.source), m.end() + 600)
        window = self.source[start:end]
        self.assertTrue(
            ("演示" in window) or ("无需" in window and "输出" in window),
            "R 代码块附近未明示为「演示」用途；学生应知道无 R 环境也能阅读",
        )

    # ---- DOM 契约：chapter-route ----------------------------------------
    def test_chapter_route_uses_raw_html_with_five_direct_children(self):
        self.assertNotRegex(
            self.source,
            r"::: *\{\.chapter-route\}",
            ".chapter-route 必须用裸 HTML，不能用 Pandoc fenced div",
        )
        results = _extract(self.source, "chapter-route")
        self.assertEqual(
            len(results),
            1,
            f"应有恰好 1 个 .chapter-route，实际 {len(results)}",
        )
        children = results[0]["children"]
        self.assertEqual(
            len(children),
            5,
            f".chapter-route 必须包含恰好 5 个直接子元素，实际 {len(children)}：{children}",
        )
        for i, c in enumerate(children, 1):
            self.assertEqual(
                c["tag"],
                "div",
                f".chapter-route 第 {i} 个直接子应为 <div>，实际 <{c['tag']}>",
            )

    # ---- DOM 契约：mascot-note ------------------------------------------
    def test_mascot_notes_have_correct_two_child_structure(self):
        results = _extract(self.source, "mascot-note")
        self.assertEqual(
            len(results),
            2,
            f"第 3 章应有恰好 2 个 .mascot-note，实际 {len(results)}",
        )
        for idx, note in enumerate(results, 1):
            children = note["children"]
            self.assertEqual(
                len(children),
                2,
                f".mascot-note #{idx} 必须只有 2 个直接子，实际 {len(children)}：{children}",
            )
            self.assertEqual(
                children[0]["tag"],
                "img",
                f".mascot-note #{idx} 第一个直接子必须是 <img>",
            )
            self.assertIn(
                "mascot-note-copy",
                children[1]["class"],
                f".mascot-note #{idx} 第二个直接子必须是 .mascot-note-copy",
            )

    def test_mascot_notes_do_not_use_fenced_div_form(self):
        self.assertNotRegex(
            self.source,
            r"::: *\{\.mascot-note\}",
            ".mascot-note 必须用裸 HTML，不能用 Pandoc fenced div",
        )

    def test_mascot_note_titles_match_plan(self):
        """两个黑豹提醒标题固定。"""
        for required_title in (
            "不要数测量次数，要数独立分配次数",
            "随机化不能拯救含糊的测量",
        ):
            self.assertIn(
                required_title,
                self.source,
                f"缺少计划中固定的黑豹提醒标题：{required_title!r}",
            )

    # ---- SVG 引用 -------------------------------------------------------
    def test_only_unit_hierarchy_svg_is_referenced(self):
        """本章只引用 1 张 SVG（ch03-unit-hierarchy.svg），无第二张。"""
        self.assertIn(
            "ch03-unit-hierarchy.svg",
            self.source,
            "必须引用 ch03-unit-hierarchy.svg",
        )
        self.assertNotIn(
            "ch03-design-chain.svg",
            self.source,
            "本章已砍掉设计链 SVG，不应引用 ch03-design-chain.svg",
        )

    # ---- 一页式模板与评分量规 -------------------------------------------
    def test_one_page_template_has_all_twelve_fields(self):
        """12 字段一页式模板：必须出现表征每个字段的核心关键词。

        不强求字段编号顺序，但每个字段的指示词必须在正文中出现。
        """
        required_field_keywords = (
            "可证伪假设",  # 1. 研究问题与可证伪假设
            "纳入",  # 2. 纳入与排除标准
            "层级关系",  # 3. 层级
            "施加方式",  # 4. 处理与对照
            "随机种子",  # 5. 随机化记录
            "区组",  # 6. 限制随机化
            "样本量依据",  # 7. 重复与样本量
            "质量控制",  # 8. 测量与质控
            "缺失",  # 9. 缺失与不良事件
            "分析接口",  # 10. 数据表与分析
            "伦理",  # 11. 伦理与可行性
            "结论边界",  # 12. 主要比较与边界
        )
        missing = [k for k in required_field_keywords if k not in self.source]
        self.assertEqual(
            missing,
            [],
            f"一页式模板缺少这些字段指示词：{missing}",
        )

    def test_rubric_has_eight_dimensions(self):
        """评分量规 8 维度全部出现。"""
        for dim in (
            "问题与因果对比",
            "单位与层级",
            "处理与对照",
            "随机化与区组",
            "重复与样本量",
            "测量与偏差控制",
            "数据与分析接口",
            "伦理与可行性",
        ):
            self.assertIn(dim, self.source, f"评分量规缺少维度：{dim}")

    # ---- 禁止规则 -------------------------------------------------------
    def test_forbids_old_misclassifications(self):
        """旧版的错误规则不得作为本章主张复活。

        允许在反面教材中**引述**这些短语（用引号包围 + 立刻批判），
        因此只检测"无引号、无批判语境"的复活。检测策略：
        短语前后 80 字符内必须出现批评词（"错"/"没用"/"不"/"反例"/"避免"/"禁止"）
        或被引号包围（引述用法）。
        """
        forbidden = (
            "同一株植物测5片叶子 | 技术重复",
            "同一株植物测 5 片叶子 | 技术重复",
            "本科实验每组至少 3",
            "每组通常做 10 个",
            "通常每组 10 个",
        )
        critique_markers = ("错", "没用", "不是", "反例", "避免", "禁止", "陷阱", "都没用")
        quote_chars = '"\'""''「」『』'
        for phrase in forbidden:
            idx = self.source.find(phrase)
            if idx == -1:
                continue
            window_start = max(0, idx - 80)
            window_end = min(len(self.source), idx + len(phrase) + 80)
            window = self.source[window_start:window_end]
            # 引号包围（前后 5 字符内有引号）的情况算引述用法
            near_left = self.source[max(0, idx - 5) : idx]
            near_right = self.source[idx + len(phrase) : min(len(self.source), idx + len(phrase) + 5)]
            quoted = any(c in near_left for c in quote_chars) and any(
                c in near_right for c in quote_chars
            )
            critiqued = any(m in window for m in critique_markers)
            self.assertTrue(
                quoted or critiqued,
                f"短语 {phrase!r} 出现在正文中但既未引号包围也未被批判——疑为旧规则复活。"
                f"\n上下文：...{window}...",
            )

    def test_no_inline_layout_hacks(self):
        self.assertNotIn(
            "word-break: break-all",
            self.source,
            "禁止用 word-break: break-all 掩盖错误布局",
        )

    # 注：spec §5.1 / §9 / §11 已确认章首手账封面允许在 .qmd 顶部
    # 内嵌 .chXX-* 章节专用 <style>。第 1、2 章均如此实现，是基准做法。
    # 因此本章不再断言"禁止内嵌 <style>"。


# ---------------------------------------------------------------------------
# 资源文件检查
# ---------------------------------------------------------------------------
class ChapterThreeAssetsTests(unittest.TestCase):
    def test_unit_hierarchy_svg_exists_and_is_valid_svg(self):
        self.assertTrue(
            UNIT_HIERARCHY_SVG.exists(),
            f"缺少单位层级 SVG：{UNIT_HIERARCHY_SVG}",
        )
        content = UNIT_HIERARCHY_SVG.read_text(encoding="utf-8")
        # 基本结构检查
        self.assertIn("<svg", content, "SVG 文件缺少 <svg> 根元素")
        self.assertIn("viewBox", content, "SVG 必须使用 viewBox 以保证响应式")
        # 四层关键文字必须出现
        for layer_word in ("区组", "小区", "幼苗", "叶片"):
            self.assertIn(
                layer_word,
                content,
                f"单位层级 SVG 必须包含层级词：{layer_word}",
            )
        # 实验单位标记
        self.assertIn(
            "实验单位",
            content,
            "单位层级 SVG 必须显式标记「实验单位」位于哪一层",
        )


# ---------------------------------------------------------------------------
# 渲染产物检查（仅在 _site/.../03-*.html 存在时运行）
# ---------------------------------------------------------------------------
@unittest.skipUnless(
    RENDERED_HTML.exists(),
    f"渲染产物不存在：{RENDERED_HTML}（请先 quarto render chapters/03-experimental-design.qmd）",
)
class ChapterThreeRenderedTests(unittest.TestCase):
    def setUp(self):
        self.html = RENDERED_HTML.read_text(encoding="utf-8")

    def test_chapter_route_renders_with_five_div_children(self):
        results = _extract(self.html, "chapter-route")
        self.assertGreaterEqual(len(results), 1, "渲染产物中找不到 .chapter-route")
        children = results[0]["children"]
        self.assertEqual(
            len(children),
            5,
            f"渲染后 .chapter-route 应有 5 个直接子，实际 {len(children)}：{[c['tag'] for c in children]}",
        )
        for c in children:
            self.assertNotIn(
                c["tag"],
                {"ol", "ul", "li"},
                f".chapter-route 直接子不应为列表标签，实际 <{c['tag']}>",
            )

    def test_mascot_notes_render_with_only_two_direct_children(self):
        results = _extract(self.html, "mascot-note")
        self.assertEqual(
            len(results),
            2,
            f"渲染后第 3 章应有 2 个 .mascot-note，实际 {len(results)}",
        )
        for idx, note in enumerate(results, 1):
            children = note["children"]
            self.assertEqual(
                len(children),
                2,
                (
                    f".mascot-note #{idx} 渲染后必须只有 2 个直接子；"
                    f"额外子元素会让正文塞进 56 px 图标列。"
                    f"实际：{[(c['tag'], c['class']) for c in children]}"
                ),
            )
            self.assertEqual(children[0]["tag"], "img")
            self.assertIn("mascot-note-copy", children[1]["class"])


if __name__ == "__main__":
    unittest.main()
