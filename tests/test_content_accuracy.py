from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class ContentAccuracyTests(unittest.TestCase):
    def test_p_value_is_not_probability_of_observed_data(self):
        sources = "\n".join(
            read(path)
            for path in (
                "chapters/01-role-of-statistics.qmd",
                "chapters/08-two-group-comparison.qmd",
                "chapters/17-stats-to-action.qmd",
                "chapters/20-bayesian-intro.qmd",
            )
        )
        forbidden = (
            "观察到当前数据的概率",
            "如果零假设为真，数据的概率",
            'P 值回答"效应是否可能为零"',
        )
        for phrase in forbidden:
            self.assertNotIn(phrase, sources)
        self.assertIn("同样或更极端", sources)
        self.assertIn("不表示零假设为真的概率", sources)

    def test_rank_test_is_not_unconditionally_described_as_median_test(self):
        chapter = read("chapters/08-two-group-comparison.qmd")
        appendix = read("appendices/method-map.qmd")
        self.assertNotIn("检验的是两组的中位数是否相等", chapter)
        self.assertNotIn("它检验中位数差异", chapter)
        self.assertNotIn("数据严重偏态", appendix)
        self.assertIn("随机优势概率", chapter)
        self.assertIn("分布形状", chapter)

    def test_interaction_and_independence_claims_are_conditional(self):
        chapter = read("chapters/09-anova.qmd")
        self.assertNotIn("主效应不能被单独解释", chapter)
        self.assertNotIn("这由设计保证（随机化）", chapter)
        self.assertIn("简单效应", chapter)
        self.assertIn("干扰", chapter)

    def test_sampling_and_richness_claims_are_qualified(self):
        sampling = read("chapters/06-sampling-error.qmd")
        richness = read("chapters/15-biodiversity-data.qmd")
        self.assertIn("独立同分布", sampling)
        self.assertNotIn("必然多于调查 5 个样方", richness)
        self.assertNotIn("使它们可比", richness)

    def test_decision_rules_do_not_turn_intervals_into_commands(self):
        chapter = read("chapters/17-stats-to-action.qmd")
        self.assertNotIn("完全高于→行动", chapter)
        self.assertNotIn("完全低于→不行动", chapter)
        self.assertIn("损失", chapter)
        self.assertIn("可逆性", chapter)

    def test_bayesian_chapter_uses_current_rhat_guidance(self):
        chapter = read("chapters/20-bayesian-intro.qmd")
        self.assertNotIn("> 1.1 表示未收敛", chapter)
        self.assertIn("1.01", chapter)
        self.assertNotIn("频率学派不能回答这个问题", chapter)

    def test_cluster_bootstrap_preserves_resampled_station_duplicates(self):
        chapter = read("chapters/06-sampling-error.qmd")
        self.assertNotIn("camera$station_id %in% idx_stations", chapter)
        self.assertIn("boot_station", chapter)
        self.assertIn("seq_along(idx_stations)", chapter)

    def test_bayesian_example_uses_existing_damage_class_column(self):
        chapter = read("chapters/20-bayesian-intro.qmd")
        self.assertNotIn("damaged ~ block_id", chapter)
        self.assertIn("damage_class ~ block_id", chapter)
        self.assertIn('plot_damage$damage_class[, "damaged"]', chapter)

    def test_occupancy_state_is_not_described_as_never_knowable(self):
        chapter = read("chapters/19-ecological-processes.qmd")
        self.assertNotIn("你永远无法直接观察", chapter)
        self.assertIn("一旦至少一次检出", chapter)

    def test_cross_chapter_references_match_actual_scope(self):
        design = read("chapters/03-experimental-design.qmd")
        anova = read("chapters/09-anova.qmd")
        self.assertNotIn("具体公式留待第 8 章", design)
        self.assertNotIn("第 8 章详述", design)
        self.assertNotIn("那是第 18 章的内容", anova)
        self.assertIn("含交互项的固定效应模型", anova)

    def test_baci_success_standard_uses_meaningful_effect_and_harm_bounds(self):
        chapter = read("chapters/16-treatment-evaluation.qmd")
        self.assertNotIn("95% CI 的下限 > 0", chapter)
        self.assertNotIn("没有显著增加", chapter)
        self.assertIn("95% CI 的下限 ≥ X", chapter)
        self.assertIn("预设容忍值", chapter)

    def test_every_reader_file_appears_in_audit_report(self):
        report = read("docs/reviews/2026-07-11-textbook-content-audit.md")
        reader_files = [ROOT / "index.qmd"]
        reader_files += sorted((ROOT / "chapters").glob("*.qmd"))
        reader_files += sorted((ROOT / "appendices").glob("*.qmd"))
        for path in reader_files:
            relative = path.relative_to(ROOT).as_posix()
            self.assertIn(f"`{relative}`", report)


if __name__ == "__main__":
    unittest.main()
