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
            self.assertNotRegex(html, r"https?://")
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
