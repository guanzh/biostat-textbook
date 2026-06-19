"""第 2 章布局回归测试。

针对 2026-06-19 修复的两处结构错误：
1. `.chapter-route` 不能用 Markdown 有序列表写（会被 Pandoc 渲染成单个 <ol>，
   只占网格一列，文字在窄列中逐字换行）。
2. `.mascot-note` 不能用 fenced div + Markdown 段落（会渲染成三个 <p>
   兄弟节点，第三个被 grid 塞进 56px 图标列）。

详见 docs/superpowers/specs/2026-06-18-textbook-page-style-design.md 7.1 节
"组件 DOM 结构契约"。
"""

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTENT_QMD = ROOT / "chapters" / "02-variables-hypotheses.qmd"
RENDERED_HTML = ROOT / "_site" / "chapters" / "02-variables-hypotheses.html"


class _StructuredCollector(HTMLParser):
    """收集带特定 class 的元素及其直接子元素结构。

    返回 list[dict]，每个 dict 含 tag / class / children（每个 child 是
    {tag, class, text_preview}）。文本节点中的纯空白被忽略。
    """

    # HTML5 void elements — 没有结束标签，HTMLParser 不会自动平衡它们，
    # 必须手动跳过开/关栈逻辑。
    _VOID_TAGS = frozenset(
        {
            "area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr",
        }
    )

    def __init__(self, target_class: str):
        super().__init__(convert_charrefs=True)
        self.target_class = target_class
        self.results: list[dict] = []
        # 栈：每项 (tag, classes, children_list, depth_when_opened)
        # 只在收集模式下记录直接子元素（depth == open_depth + 1）
        self._stack: list[tuple[str, list[str]]] = []
        self._capture_stack: list[dict] = []  # 当前正在收集的 .target 元素
        self._current_text_buf: list[str] = []

    @staticmethod
    def _classes(attrs):
        for name, val in attrs:
            if name == "class" and val:
                return val.split()
        return []

    def _record_child(self, tag, classes):
        """如果当前层级正好是某个 capture entry 的直接子，把它记下来。"""
        for entry in self._capture_stack:
            if len(self._stack) == entry["open_depth"]:
                # _stack 此刻不含将要 push 的开标签（void 不 push）也不含
                # 已经 push 的开标签（开标签先 push 再调用本函数时，深度
                # 应为 open_depth + 1）。我们在外层确保 depth == open_depth + 1。
                pass
        # 调用者保证 depth 关系，这里只 append。
        for entry in self._capture_stack:
            if len(self._stack) == entry["open_depth"] + 1:
                entry["children"].append(
                    {"tag": tag, "class": classes, "text": ""}
                )
                return

    def handle_starttag(self, tag, attrs):
        classes = self._classes(attrs)

        if tag in self._VOID_TAGS:
            # 不入栈，但仍要记成"直接子元素"（如果当前正在收集的目标
            # 期望子元素出现在当前深度+1 上）。
            # 直接子的判定是：开标签出现时所在栈深度 == open_depth。
            for entry in self._capture_stack:
                if len(self._stack) == entry["open_depth"]:
                    entry["children"].append(
                        {"tag": tag, "class": classes, "text": ""}
                    )
                    break
            return

        self._stack.append((tag, classes))

        if self.target_class in classes:
            entry = {
                "tag": tag,
                "class": classes,
                "open_depth": len(self._stack),
                "children": [],
            }
            self.results.append(entry)
            self._capture_stack.append(entry)
            return

        # 是否是某个正在收集的目标的直接子元素？
        for entry in self._capture_stack:
            if len(self._stack) == entry["open_depth"] + 1:
                entry["children"].append(
                    {"tag": tag, "class": classes, "text": ""}
                )
                break

    def handle_startendtag(self, tag, attrs):
        # 形如 <img ... />，统一按 void 处理
        classes = self._classes(attrs)
        for entry in self._capture_stack:
            if len(self._stack) == entry["open_depth"]:
                entry["children"].append(
                    {"tag": tag, "class": classes, "text": ""}
                )
                break

    def handle_endtag(self, tag):
        if tag in self._VOID_TAGS:
            return
        if not self._stack:
            return
        # 关闭目标元素
        if (
            self._capture_stack
            and len(self._stack) == self._capture_stack[-1]["open_depth"]
        ):
            self._capture_stack.pop()
        self._stack.pop()

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        # 把文本归到最近的 capture entry 的最后一个直接子元素（如果当前层级匹配）
        for entry in self._capture_stack:
            cur_depth = len(self._stack)
            if cur_depth > entry["open_depth"] and entry["children"]:
                entry["children"][-1]["text"] = (
                    entry["children"][-1].get("text", "") + text
                )


def _extract(html: str, target_class: str):
    p = _StructuredCollector(target_class)
    p.feed(html)
    return p.results


class ChapterTwoSourceTests(unittest.TestCase):
    """直接检查 .qmd 源文件，无需 Quarto 渲染。"""

    def setUp(self):
        self.assertTrue(CONTENT_QMD.exists(), f"missing {CONTENT_QMD}")
        self.source = CONTENT_QMD.read_text(encoding="utf-8")

    def test_chapter_route_uses_raw_html_with_five_direct_children(self):
        """.chapter-route 必须是裸 HTML，含恰好 5 个 <div> 直接子元素。"""
        # 不允许 Pandoc fenced div 写法
        self.assertNotRegex(
            self.source,
            r"::: *\{\.chapter-route\}",
            "chapter-route 必须用裸 HTML，不能用 Pandoc fenced div + Markdown 列表",
        )
        # 找到 chapter-route 块
        match = re.search(
            r'<div class="chapter-route"[^>]*>(.*?)</div>\s*\n\s*\n',
            self.source,
            flags=re.DOTALL,
        )
        # 兼容紧跟其他内容的情况：用解析器更稳
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
        # 每个直接子都是 <div>，不能是 <ol>/<ul>/<li>
        for i, c in enumerate(children, 1):
            self.assertEqual(
                c["tag"],
                "div",
                f"chapter-route 第 {i} 个直接子元素应为 <div>，实际 <{c['tag']}>",
            )

    def test_mascot_notes_have_correct_two_child_structure(self):
        """两个 .mascot-note 都必须有 img + .mascot-note-copy 两个直接子元素。"""
        results = _extract(self.source, "mascot-note")
        self.assertEqual(
            len(results),
            2,
            f"第 2 章应有 2 个 .mascot-note，实际 {len(results)}",
        )
        for idx, note in enumerate(results, 1):
            children = note["children"]
            # 直接子元素恰好 2 个
            self.assertEqual(
                len(children),
                2,
                f".mascot-note #{idx} 必须只有 2 个直接子元素，实际 {len(children)}：{children}",
            )
            tags = [c["tag"] for c in children]
            self.assertEqual(
                tags[0],
                "img",
                f".mascot-note #{idx} 第一个直接子元素必须是 <img>，实际 <{tags[0]}>",
            )
            self.assertIn(
                "mascot-note-copy",
                children[1]["class"],
                f".mascot-note #{idx} 第二个直接子元素必须是 .mascot-note-copy，实际 class={children[1]['class']}",
            )

    def test_mascot_notes_do_not_use_fenced_div_form(self):
        """禁止 ::: {.mascot-note} 形式（会渲染出 3 个 <p> 兄弟）。"""
        self.assertNotRegex(
            self.source,
            r"::: *\{\.mascot-note\}",
            ".mascot-note 必须用裸 HTML，不能用 Pandoc fenced div",
        )

    def test_no_inline_layout_hacks(self):
        """禁止用硬换行/分字断行掩盖结构错误。"""
        # 我们关心的是结构修复处不应出现的应急手段。先做粗粒度全文扫描。
        self.assertNotIn(
            "word-break: break-all",
            self.source,
            "禁止用 word-break: break-all 掩盖错误布局",
        )


@unittest.skipUnless(
    RENDERED_HTML.exists(),
    f"渲染产物不存在：{RENDERED_HTML}（请先 quarto render chapters/02-variables-hypotheses.qmd）",
)
class ChapterTwoRenderedTests(unittest.TestCase):
    """检查 _site 渲染输出，验证 Quarto 没有把结构搅坏。"""

    def setUp(self):
        self.html = RENDERED_HTML.read_text(encoding="utf-8")

    def test_chapter_route_renders_with_five_div_children(self):
        results = _extract(self.html, "chapter-route")
        self.assertGreaterEqual(len(results), 1, "渲染产物中找不到 .chapter-route")
        # 取第一个匹配（章内只有一个学习路线）
        children = results[0]["children"]
        self.assertEqual(
            len(children),
            5,
            f"渲染后 .chapter-route 应有 5 个直接子元素，实际 {len(children)}：{[c['tag'] for c in children]}",
        )
        # 不能是 <ol>/<ul>
        for c in children:
            self.assertNotIn(
                c["tag"],
                {"ol", "ul", "li"},
                f".chapter-route 直接子元素不应为列表标签，实际 <{c['tag']}>",
            )

    def test_mascot_notes_render_with_only_two_direct_children(self):
        """关键：渲染后 .mascot-note 不能多出 <p> 兄弟，否则正文会被塞进图标列。"""
        results = _extract(self.html, "mascot-note")
        self.assertEqual(
            len(results),
            2,
            f"渲染后第 2 章应有 2 个 .mascot-note，实际 {len(results)}",
        )
        for idx, note in enumerate(results, 1):
            children = note["children"]
            # 必须恰好两个直接子元素：img + .mascot-note-copy
            self.assertEqual(
                len(children),
                2,
                (
                    f".mascot-note #{idx} 渲染后必须只有 2 个直接子元素；"
                    f"出现额外子元素意味着正文段落被排进 56 px 图标列。"
                    f"实际：{[(c['tag'], c['class']) for c in children]}"
                ),
            )
            self.assertEqual(children[0]["tag"], "img")
            self.assertIn("mascot-note-copy", children[1]["class"])

    def test_mascot_note_body_is_inside_copy_column(self):
        """提醒正文必须落在 .mascot-note-copy 内（即文字不能在图标列）。"""
        # 简易检查：搜两个提醒标题对应的正文片段，应该出现在 .mascot-note-copy
        # 块内部，且与 mascot-note-copy 的距离比与 <img class="mascot"> 近。
        for body_fragment in (
            "测量过程本身是研究设计的一部分",
            "用同一份数据既找规律又验证规律",
        ):
            idx_body = self.html.find(body_fragment)
            self.assertGreater(
                idx_body,
                0,
                f"渲染产物中找不到提醒正文片段：{body_fragment!r}",
            )
            # 在 body_fragment 之前 300 字符内必须出现 mascot-note-copy 开标签
            window = self.html[max(0, idx_body - 600) : idx_body]
            self.assertIn(
                "mascot-note-copy",
                window,
                f"提醒正文 {body_fragment!r} 不在 .mascot-note-copy 内",
            )


if __name__ == "__main__":
    unittest.main()
