from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANIMATIONS = {
    "experimental-unit.html": ("实验单位", "32", "160"),
    "normal-distribution.html": ("正态分布", "μ", "σ"),
    "sampling-distribution.html": ("抽样分布", "标准误", "√n"),
    "p-value.html": ("双侧 p 值", "同样或更极端", "效应大小"),
    "type-i-ii-errors.html": ("两类错误", "α", "β"),
    "baci-interaction.html": ("BACI", "变化之差", "共同时间趋势"),
    "occupancy-detection.html": ("占域与探测", "(1 − p)ᴷ", "重复调查"),
}
EMBEDS = {
    "chapters/03-experimental-design.qmd": ["experimental-unit.html"],
    "chapters/05-descriptive-statistics.qmd": ["normal-distribution.html"],
    "chapters/06-sampling-error.qmd": ["sampling-distribution.html"],
    "chapters/08-two-group-comparison.qmd": ["p-value.html", "type-i-ii-errors.html"],
    "chapters/16-treatment-evaluation.qmd": ["baci-interaction.html"],
    "chapters/19-ecological-processes.qmd": ["occupancy-detection.html"],
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
            self.assertNotRegex(html, r"https?://")
            for label in labels:
                self.assertIn(label, html, f"{filename} missing {label}")

    def test_animation_canvas_has_accessible_fallback(self):
        for filename in ANIMATIONS:
            html = (ROOT / "animations" / filename).read_text(encoding="utf-8")
            self.assertRegex(html, r'<canvas[^>]+aria-label="[^"]+"')
            self.assertIn('class="sr-only"', html)

    def test_scrubbing_does_not_reset_existing_animations_to_blank_frame(self):
        for filename in ("normal-distribution.html", "p-value.html"):
            html = (ROOT / "animations" / filename).read_text(encoding="utf-8")
            self.assertNotRegex(
                html,
                r"if\s*\(lastTick\s*===\s*null\)\s*\{[^}]*draw\s*\(0\)",
                f"{filename}: the next animation frame must redraw the selected time",
            )

    def test_each_target_chapter_has_responsive_embeds(self):
        for chapter, filenames in EMBEDS.items():
            source = (ROOT / chapter).read_text(encoding="utf-8")
            self.assertEqual(source.count('class="teaching-animation"'), len(filenames))
            for filename in filenames:
                self.assertEqual(source.count(filename), 2)
                self.assertRegex(
                    source,
                    rf'<iframe[^>]+src="\.\./animations/{re.escape(filename)}"[^>]+title="[^"]+"',
                )
                self.assertNotIn(
                    f'    <iframe src="../animations/{filename}"',
                    source,
                    f"{chapter}: four-space indentation makes Pandoc render the iframe as code",
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
