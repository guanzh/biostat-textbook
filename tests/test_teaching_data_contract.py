"""教学数据契约测试。

验证五份合成 CSV 存在、行数、主键、字段、水平和 source_type。
"""

from pathlib import Path
import csv
import unittest


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "teaching"


def _read_csv(name):
    path = DATA_DIR / name
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return path, rows


def _unique_keys(rows, keys):
    seen = set()
    for r in rows:
        k = tuple(r[k] for k in keys)
        self.assertNotIn(k, seen, f"重复主键 {keys}={k}")
        seen.add(k)


class TeachingDataContractTests(unittest.TestCase):
    # ── 黄黄草光照数据 ──

    def test_huanghuang_exists_and_has_480_rows(self):
        path, rows = _read_csv("huanghuang_light_long.csv")
        self.assertEqual(len(rows), 480)

    def test_huanghuang_has_required_columns(self):
        _, rows = _read_csv("huanghuang_light_long.csv")
        expected = {
            "block_id", "plot_id", "light_pct", "plant_id",
            "month", "alive", "flowered", "height_cm", "spad", "source_type",
        }
        self.assertTrue(expected.issubset(set(rows[0].keys())))

    def test_huanghuang_primary_key_unique(self):
        _, rows = _read_csv("huanghuang_light_long.csv")
        seen = set()
        for r in rows:
            k = (r["block_id"], r["plot_id"], r["plant_id"], r["month"])
            self.assertNotIn(k, seen, f"重复主键 {k}")
            seen.add(k)

    def test_huanghuang_has_32_plots(self):
        _, rows = _read_csv("huanghuang_light_long.csv")
        plots = set((r["block_id"], r["plot_id"]) for r in rows)
        self.assertEqual(len(plots), 32)

    def test_huanghuang_light_levels(self):
        _, rows = _read_csv("huanghuang_light_long.csv")
        levels = set(r["light_pct"] for r in rows)
        self.assertEqual(levels, {"100", "70", "40", "15"})

    def test_huanghuang_source_type(self):
        _, rows = _read_csv("huanghuang_light_long.csv")
        vals = set(r["source_type"] for r in rows)
        self.assertEqual(vals, {"synthetic_teaching_data"})

    # ── 红外相机监测数据 ──

    def test_camera_exists_and_has_1080_rows(self):
        _, rows = _read_csv("camera_monitoring_long.csv")
        self.assertEqual(len(rows), 1080)

    def test_camera_has_required_columns(self):
        _, rows = _read_csv("camera_monitoring_long.csv")
        expected = {
            "station_id", "stratum", "x_km", "y_km",
            "year", "occasion", "effort_nights", "detected",
            "photo_count", "forest_cover", "distance_road_km", "source_type",
        }
        self.assertTrue(expected.issubset(set(rows[0].keys())))

    def test_camera_primary_key_unique(self):
        _, rows = _read_csv("camera_monitoring_long.csv")
        seen = set()
        for r in rows:
            k = (r["station_id"], r["year"], r["occasion"])
            self.assertNotIn(k, seen, f"重复主键 {k}")
            seen.add(k)

    def test_camera_has_60_stations(self):
        _, rows = _read_csv("camera_monitoring_long.csv")
        stations = set(r["station_id"] for r in rows)
        self.assertEqual(len(stations), 60)

    def test_camera_source_type(self):
        _, rows = _read_csv("camera_monitoring_long.csv")
        vals = set(r["source_type"] for r in rows)
        self.assertEqual(vals, {"synthetic_teaching_data"})

    # ── 森林病虫害试验数据 ──

    def test_forest_exists_and_has_2400_rows(self):
        _, rows = _read_csv("forest_pest_trial_long.csv")
        self.assertEqual(len(rows), 2400)

    def test_forest_has_required_columns(self):
        _, rows = _read_csv("forest_pest_trial_long.csv")
        expected = {
            "block_id", "plot_id", "treatment", "tree_id", "visit",
            "pest_count", "damage_class", "dead", "non_target_count",
            "cost_cny_plot", "implementation_score", "source_type",
        }
        self.assertTrue(expected.issubset(set(rows[0].keys())))

    def test_forest_primary_key_unique(self):
        _, rows = _read_csv("forest_pest_trial_long.csv")
        seen = set()
        for r in rows:
            k = (r["block_id"], r["plot_id"], r["tree_id"], r["visit"])
            self.assertNotIn(k, seen, f"重复主键 {k}")
            seen.add(k)

    def test_forest_has_40_treatment_plots(self):
        _, rows = _read_csv("forest_pest_trial_long.csv")
        plots = set((r["block_id"], r["plot_id"]) for r in rows)
        self.assertEqual(len(plots), 40)

    def test_forest_treatment_levels(self):
        _, rows = _read_csv("forest_pest_trial_long.csv")
        levels = set(r["treatment"] for r in rows)
        self.assertEqual(levels, {"control", "standard", "biocontrol", "integrated"})

    def test_forest_source_type(self):
        _, rows = _read_csv("forest_pest_trial_long.csv")
        vals = set(r["source_type"] for r in rows)
        self.assertEqual(vals, {"synthetic_teaching_data"})

    # ── 修复地样点—时期数据 ──

    def test_restoration_site_exists_and_has_120_rows(self):
        _, rows = _read_csv("restoration_site_period.csv")
        self.assertEqual(len(rows), 120)

    def test_restoration_site_has_required_columns(self):
        _, rows = _read_csv("restoration_site_period.csv")
        expected = {
            "landscape_id", "site_id", "status", "period",
            "quadrat_id", "canopy_cover", "soil_moisture",
            "species_richness", "native_cover", "source_type",
        }
        self.assertTrue(expected.issubset(set(rows[0].keys())))

    def test_restoration_site_primary_key_unique(self):
        _, rows = _read_csv("restoration_site_period.csv")
        seen = set()
        for r in rows:
            k = (r["landscape_id"], r["site_id"], r["period"], r["quadrat_id"])
            self.assertNotIn(k, seen, f"重复主键 {k}")
            seen.add(k)

    def test_restoration_site_period_levels(self):
        _, rows = _read_csv("restoration_site_period.csv")
        periods = set(r["period"] for r in rows)
        statuses = set(r["status"] for r in rows)
        self.assertEqual(periods, {"before", "after"})
        self.assertEqual(statuses, {"restored", "control"})

    def test_restoration_site_source_type(self):
        _, rows = _read_csv("restoration_site_period.csv")
        vals = set(r["source_type"] for r in rows)
        self.assertEqual(vals, {"synthetic_teaching_data"})

    # ── 修复地群落长表 ──

    def test_restoration_community_exists_and_has_3000_rows(self):
        _, rows = _read_csv("restoration_community_long.csv")
        self.assertEqual(len(rows), 3000)

    def test_restoration_community_has_required_columns(self):
        _, rows = _read_csv("restoration_community_long.csv")
        expected = {
            "landscape_id", "site_id", "period", "quadrat_id",
            "species_id", "abundance", "native", "guild", "source_type",
        }
        self.assertTrue(expected.issubset(set(rows[0].keys())))

    def test_restoration_community_primary_key_unique(self):
        _, rows = _read_csv("restoration_community_long.csv")
        seen = set()
        for r in rows:
            k = (r["landscape_id"], r["site_id"], r["period"],
                 r["quadrat_id"], r["species_id"])
            self.assertNotIn(k, seen, f"重复主键 {k}")
            seen.add(k)

    def test_restoration_community_richness_matches_site_period(self):
        """群落长表的丰富度应与 site_period 的 species_richness 一致。"""
        _, comm = _read_csv("restoration_community_long.csv")
        _, site = _read_csv("restoration_site_period.csv")

        # 从长表计算丰富度
        richness_from_comm = {}
        for r in comm:
            if int(r["abundance"]) > 0:
                key = (r["landscape_id"], r["site_id"], r["period"], r["quadrat_id"])
                richness_from_comm.setdefault(key, set()).add(r["species_id"])

        for r in site:
            key = (r["landscape_id"], r["site_id"], r["period"], r["quadrat_id"])
            expected = int(r["species_richness"])
            actual = len(richness_from_comm.get(key, set()))
            self.assertEqual(actual, expected,
                             f"丰富度不匹配 {key}: 期望 {expected}, 实际 {actual}")

    def test_restoration_community_source_type(self):
        _, rows = _read_csv("restoration_community_long.csv")
        vals = set(r["source_type"] for r in rows)
        self.assertEqual(vals, {"synthetic_teaching_data"})


if __name__ == "__main__":
    unittest.main()
