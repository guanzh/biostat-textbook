"""版本结构契约测试。

验证三个专业方向 profile（_quarto-wildlife.yml / _quarto-forest.yml /
_quarto-plant.yml）的章节组合正确：

1. 基础 _quarto.yml 只含三专业共用的第一至三篇，不含第四篇及之后的章节。
2. 每个 profile 追加第四篇（专业专属）+ 第五篇 + 附录，且第五篇和附录
   的清单在三个 profile 间完全一致（防止改一个漏两个）。
3. 三个版本对第 13/14/15 章的取舍互斥且完整：
   野保版：无 13，有 14、15；森保版：13-forest，无 14，有 15；
   植保版：13-plant，无 14、15。
4. profile 引用的每个章节文件都存在。
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]

SHARED_TAIL = {
    "第五篇": [
        "chapters/18-mixed-models.qmd",
        "chapters/19-ecological-processes.qmd",
        "chapters/20-bayesian-intro.qmd",
        "chapters/21-spatiotemporal.qmd",
        "chapters/22-ai-assisted-learning.qmd",
    ],
    "附录": [
        "appendices/r-basics.qmd",
        "appendices/method-map.qmd",
        "appendices/glossary.qmd",
        "appendices/reproducible-template.qmd",
        "appendices/data-ethics.qmd",
        "appendices/ai-checklist.qmd",
        "appendices/learning-pathway.qmd",
    ],
}

PART_FOUR_EXPECTED = {
    "wildlife": [
        "chapters/14-wildlife-survey.qmd",
        "chapters/15-biodiversity-data.qmd",
        "chapters/16-treatment-evaluation.qmd",
        "chapters/17-stats-to-action.qmd",
    ],
    "forest": [
        "chapters/13-forest-protection.qmd",
        "chapters/15-biodiversity-data.qmd",
        "chapters/16-treatment-evaluation.qmd",
        "chapters/17-stats-to-action.qmd",
    ],
    "plant": [
        "chapters/13-plant-protection.qmd",
        "chapters/16-treatment-evaluation.qmd",
        "chapters/17-stats-to-action.qmd",
    ],
}


def _read_yaml(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _chapters_in_profile(profile):
    """解析 profile 文件，返回 {篇名: [章节路径]}（仅 profile 追加的部分）。"""
    text = _read_yaml(f"_quarto-{profile}.yml")
    result = {}
    for part_match in re.finditer(
        r'-\s*part:\s*"([^"]+)"\s*\n(?:\s*chapters:\s*\n)?((?:\s*-\s*[\w\-/.]+\.qmd\s*\n?)+)',
        text,
    ):
        part_name = part_match.group(1)
        chapters = re.findall(r"-\s*([\w\-/.]+\.qmd)", part_match.group(2))
        result[part_name] = chapters
    return result


def _part4_chapters(profile_parts):
    """从解析结果里取第四篇（键是完整标题，前缀匹配）。"""
    for key, chapters in profile_parts.items():
        if key.startswith("第四篇"):
            return chapters
    raise AssertionError(f"缺少第四篇：{profile_parts}")


class BookVersionContractTests(unittest.TestCase):
    def test_base_config_has_no_chapter_beyond_part_three(self):
        base = _read_yaml("_quarto.yml")
        # 去掉注释行后再扫描（注释里会提到第四篇/第五篇）
        base_no_comments = "\n".join(
            line for line in base.splitlines() if not line.strip().startswith("#")
        )
        for banned in (
            "chapters/13-forest-protection.qmd",
            "chapters/13-plant-protection.qmd",
            "chapters/14-wildlife-survey.qmd",
            "chapters/15-biodiversity-data.qmd",
            "chapters/16-treatment-evaluation.qmd",
            "chapters/17-stats-to-action.qmd",
            "chapters/18-mixed-models.qmd",
            "chapters/19-ecological-processes.qmd",
            "chapters/20-bayesian-intro.qmd",
            "chapters/21-spatiotemporal.qmd",
            "chapters/22-ai-assisted-learning.qmd",
            "appendices/",
            "第四篇",
            "第五篇",
        ):
            self.assertNotIn(banned, base_no_comments, f"基础配置不应包含 {banned}")

    def test_base_config_keeps_first_three_parts(self):
        base = _read_yaml("_quarto.yml")
        for part in ("第一篇", "第二篇", "第三篇"):
            self.assertIn(part, base)
        for ch in (
            "chapters/01-role-of-statistics.qmd",
            "chapters/04-data-management.qmd",
            "chapters/12-glm-intro.qmd",
        ):
            self.assertIn(ch, base)

    def test_part_four_matches_expected_per_profile(self):
        for profile, expected in PART_FOUR_EXPECTED.items():
            parts = _chapters_in_profile(profile)
            self.assertEqual(
                _part4_chapters(parts),
                expected,
                f"{profile} 第四篇章节清单不符",
            )

    def test_part_five_and_appendix_lists_are_identical_across_profiles(self):
        profiles = {p: _chapters_in_profile(p) for p in PART_FOUR_EXPECTED}
        for part_name, expected in SHARED_TAIL.items():
            for profile, parts in profiles.items():
                matching = [k for k in parts if k.startswith(part_name)]
                self.assertTrue(
                    matching, f"{profile} 缺少{part_name}"
                )
                self.assertEqual(
                    parts[matching[0]],
                    expected,
                    f"{profile} 的{part_name}清单与共享清单不一致",
                )

    def test_every_profile_referenced_chapter_exists(self):
        for profile in PART_FOUR_EXPECTED:
            for chapters in _chapters_in_profile(profile).values():
                for path in chapters:
                    self.assertTrue(
                        (ROOT / path).exists(),
                        f"{profile} 引用了不存在的文件 {path}",
                    )

    def test_every_chapter_file_belongs_to_at_least_one_version(self):
        """每个章节文件要么在基础配置（三版本共用），要么至少被一个 profile 引用。"""
        base = _read_yaml("_quarto.yml")
        all_chapters = sorted((ROOT / "chapters").glob("*.qmd"))
        for path in all_chapters:
            rel = path.relative_to(ROOT).as_posix()
            in_base = rel in base
            in_profile = any(
                rel in " ".join(chs)
                for p in PART_FOUR_EXPECTED
                for chs in _chapters_in_profile(p).values()
            )
            self.assertTrue(
                in_base or in_profile,
                f"{rel} 既不在基础配置也不在任何 profile 中",
            )

    def test_versions_are_mutually_exclusive_on_chapter_13_and_14(self):
        parts = {
            p: _part4_chapters(_chapters_in_profile(p))
            for p in PART_FOUR_EXPECTED
        }
        joined = {p: "\n".join(chs) for p, chs in parts.items()}
        # 第 13 章：野保无，森保 13-forest，植保 13-plant
        self.assertNotIn("13-", joined["wildlife"])
        self.assertIn("13-forest", joined["forest"])
        self.assertIn("13-plant", joined["plant"])
        self.assertNotIn("13-forest", joined["plant"])
        self.assertNotIn("13-plant", joined["forest"])
        # 第 14 章只在野保版
        self.assertIn("14-wildlife", joined["wildlife"])
        self.assertNotIn("14-wildlife", joined["forest"])
        self.assertNotIn("14-wildlife", joined["plant"])

    def test_split_chapter_13_files_do_not_reference_removed_file(self):
        """旧文件已删除，且没有章节仍然引用 13-forest-plant-protection.qmd。"""
        self.assertFalse(
            (ROOT / "chapters" / "13-forest-plant-protection.qmd").exists(),
            "旧的第 13 章合并文件应该已被删除",
        )
        for path in sorted((ROOT / "chapters").glob("*.qmd")):
            self.assertNotIn(
                "13-forest-plant-protection.qmd",
                path.read_text(encoding="utf-8"),
                f"{path.name} 仍引用已删除的旧文件",
            )


if __name__ == "__main__":
    unittest.main()
