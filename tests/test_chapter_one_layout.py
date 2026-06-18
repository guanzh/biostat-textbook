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
        rendered_content = content_html.read_text(encoding="utf-8")
        self.assertRegex(
            rendered_cover,
            r'href="(?:\.\./chapters/)?01-role-of-statistics\.html"',
        )
        self.assertNotIn("&lt;strong&gt;黑豹提醒", rendered_content)
        self.assertIn("chapter-cover", rendered_cover)


if __name__ == "__main__":
    unittest.main()
