from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BOOK_CONFIG = ROOT / "_quarto.yml"
CONTENT_QMD = ROOT / "chapters" / "01-role-of-statistics.qmd"
STYLES = ROOT / "styles.css"
PAIRED_PLOT = ROOT / "images" / "figures" / "ch01-flowering-paired-plot.svg"


class ChapterOneSourceTests(unittest.TestCase):
    def test_book_has_one_chapter_one_entry(self):
        config = BOOK_CONFIG.read_text(encoding="utf-8")
        standalone_cover = "- chapters/01-role-of-statistics-cover.qmd"
        content = "- chapters/01-role-of-statistics.qmd"
        self.assertNotIn(standalone_cover, config)
        self.assertIn(content, config)

    def test_previous_cover_is_embedded_before_reading_route(self):
        source = CONTENT_QMD.read_text(encoding="utf-8")
        self.assertIn('<div class="ch1-fig sketch">', source)
        self.assertIn("保护数据中的不确定性", source)
        self.assertIn("统计学在保护中的四个作用", source)
        self.assertLess(source.index("ch1-fig sketch"), source.index("chapter-route"))

    def test_content_uses_design_system_without_inline_css(self):
        source = CONTENT_QMD.read_text(encoding="utf-8")
        self.assertNotIn("<style>", source)
        for component in (
            "ch1-fig",
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
            ".ch1-fig",
            ".ch1-noises",
            ".ch1-pipeline",
            ".ch1-final",
            ".chapter-route",
            ".evidence-figure",
            ".mascot-note",
        ):
            self.assertIn(selector, css)

    def test_visual_assets_exist(self):
        self.assertGreater(PAIRED_PLOT.stat().st_size, 1_000)


class ChapterOneRenderedTests(unittest.TestCase):
    def test_rendered_page_contains_cover_before_reading_route(self):
        content_html = ROOT / "_site" / "chapters" / "01-role-of-statistics.html"
        self.assertTrue(content_html.exists())
        rendered_content = content_html.read_text(encoding="utf-8")
        self.assertNotIn("&lt;strong&gt;黑豹提醒", rendered_content)
        self.assertIn("ch1-fig sketch", rendered_content)
        self.assertLess(
            rendered_content.index("ch1-fig sketch"),
            rendered_content.index("chapter-route"),
        )


if __name__ == "__main__":
    unittest.main()
