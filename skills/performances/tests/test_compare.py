from __future__ import annotations

import io
import json
import math
import random
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import compare  # noqa: E402


def noisy(center, spread, n, seed):
    rng = random.Random(seed)
    return [max(0.01, rng.gauss(center, spread)) for _ in range(n)]


class SummaryTests(unittest.TestCase):
    def test_percentile_interpolates(self):
        self.assertEqual(compare.percentile([1, 2, 3, 4], 0.5), 2.5)
        self.assertEqual(compare.percentile([1, 2, 3, 4], 0.0), 1)
        self.assertEqual(compare.percentile([1, 2, 3, 4], 1.0), 4)

    def test_percentile_rejects_empty(self):
        with self.assertRaises(ValueError):
            compare.percentile([], 0.5)

    def test_summarize(self):
        s = compare.summarize([10, 20, 30, 40, 50])
        self.assertEqual(s["n"], 5)
        self.assertEqual(s["median"], 30)
        self.assertEqual(s["mean"], 30)
        self.assertEqual(s["min"], 10)
        self.assertEqual(s["max"], 50)
        self.assertAlmostEqual(s["p95"], 48)

    def test_summarize_single_sample_has_zero_stdev(self):
        self.assertEqual(compare.summarize([7])["stdev"], 0.0)


class StatisticsTests(unittest.TestCase):
    def test_bootstrap_ci_brackets_the_median(self):
        samples = noisy(100, 5, 40, seed=1)
        low, high = compare.bootstrap_ci(samples, compare.median, 2000, 0.95, random.Random(2))
        self.assertLess(low, compare.median(samples))
        self.assertGreater(high, compare.median(samples))
        self.assertLess(high - low, 10)

    def test_bootstrap_is_deterministic_for_a_seed(self):
        samples = noisy(50, 4, 30, seed=3)
        a = compare.bootstrap_ci(samples, compare.median, 500, 0.95, random.Random(9))
        b = compare.bootstrap_ci(samples, compare.median, 500, 0.95, random.Random(9))
        self.assertEqual(a, b)

    def test_mann_whitney_detects_a_shift(self):
        p = compare.mann_whitney_p(noisy(100, 5, 30, 1), noisy(60, 5, 30, 2))
        self.assertLess(p, 0.001)

    def test_mann_whitney_accepts_identical_distributions(self):
        p = compare.mann_whitney_p(noisy(100, 5, 40, 4), noisy(100, 5, 40, 5))
        self.assertGreater(p, 0.05)

    def test_mann_whitney_all_ties_is_not_significant(self):
        self.assertEqual(compare.mann_whitney_p([5, 5, 5, 5], [5, 5, 5, 5]), 1.0)

    def test_holm_adjusts_and_keeps_order(self):
        adjusted = compare.holm_adjust([0.01, 0.04, 0.03])
        self.assertAlmostEqual(adjusted[0], 0.03)
        self.assertAlmostEqual(adjusted[1], 0.06)
        self.assertAlmostEqual(adjusted[2], 0.06)

    def test_holm_caps_at_one(self):
        self.assertEqual(compare.holm_adjust([0.9, 0.8]), [1.0, 1.0])

    def test_holm_empty(self):
        self.assertEqual(compare.holm_adjust([]), [])


class CompareScenarioTests(unittest.TestCase):
    def run_compare(self, before, after, **kwargs):
        return compare.compare_scenario(before, after, alpha=0.05, resamples=2000, seed=1, **kwargs)

    def test_improvement(self):
        result = self.run_compare(noisy(200, 10, 30, 1), noisy(100, 10, 30, 2))
        self.assertEqual(result["verdict"], "improved")
        self.assertLess(result["change_pct"], -40)
        self.assertLess(result["change_ci_pct"][1], 0)

    def test_regression(self):
        result = self.run_compare(noisy(100, 10, 30, 1), noisy(200, 10, 30, 2))
        self.assertEqual(result["verdict"], "regressed")
        self.assertGreater(result["change_ci_pct"][0], 0)

    def test_no_change_is_inconclusive(self):
        result = self.run_compare(noisy(100, 10, 30, 1), noisy(100, 10, 30, 2))
        self.assertEqual(result["verdict"], "no significant change")

    def test_too_few_samples_refuses_to_judge(self):
        result = self.run_compare([100, 101, 99], [50, 51, 49])
        self.assertEqual(result["verdict"], "insufficient samples")

    def test_failed_runs_are_reported_not_hidden(self):
        result = self.run_compare(noisy(100, 5, 30, 1), noisy(50, 5, 30, 2), before_failures=3, after_failures=0)
        self.assertEqual(result["before"]["failures"], 3)
        self.assertEqual(result["after"]["failures"], 0)

    def test_zero_baseline_does_not_divide_by_zero(self):
        result = self.run_compare([0.0] * 10, [1.0] * 10)
        self.assertTrue(math.isinf(result["change_pct"]))
        self.assertFalse(any(math.isnan(bound) for bound in result["change_ci_pct"]))
        self.assertEqual(result["verdict"], "regressed")

    def test_throughput_increase_is_an_improvement_when_higher_is_better(self):
        before, after = noisy(100, 5, 30, 1), noisy(200, 5, 30, 2)
        lower = self.run_compare(before, after)
        higher = self.run_compare(before, after, higher_is_better=True)
        self.assertEqual(lower["verdict"], "regressed")
        self.assertEqual(higher["verdict"], "improved")

    def test_format_change_renders_nan_as_not_available(self):
        self.assertEqual(compare.format_change(float("nan")), "n/a")


class ReportTests(unittest.TestCase):
    def sample_input(self):
        return {
            "unit": "ms",
            "before": {"orders.list@1x": noisy(20, 2, 20, 1), "orders.list@1000x": noisy(900, 50, 20, 2)},
            "after": {"orders.list@1x": noisy(19, 2, 20, 3), "orders.list@1000x": noisy(90, 8, 20, 4)},
        }

    def test_analyze_covers_every_scenario_and_adjusts_p_values(self):
        results = compare.analyze(self.sample_input(), alpha=0.05, resamples=1000, seed=1)
        self.assertEqual([r["scenario"] for r in results], ["orders.list@1x", "orders.list@1000x"])
        for r in results:
            self.assertIn("p_adjusted", r)
            self.assertGreaterEqual(r["p_adjusted"], r["p_value"])
        self.assertEqual(results[1]["verdict"], "improved")

    def test_analyze_rejects_mismatched_scenarios(self):
        data = self.sample_input()
        del data["after"]["orders.list@1x"]
        with self.assertRaises(ValueError):
            compare.analyze(data, alpha=0.05, resamples=100, seed=1)

    def test_analyze_accepts_failure_counts(self):
        data = self.sample_input()
        data["failures"] = {"before": {"orders.list@1000x": 4}, "after": {}}
        results = compare.analyze(data, alpha=0.05, resamples=100, seed=1)
        self.assertEqual(results[1]["before"]["failures"], 4)

    def test_html_is_self_contained_and_escaped(self):
        data = self.sample_input()
        data["before"]["<script>x</script>"] = noisy(10, 1, 10, 5)
        data["after"]["<script>x</script>"] = noisy(9, 1, 10, 6)
        results = compare.analyze(data, alpha=0.05, resamples=100, seed=1)
        page = compare.render_html(results, unit="ms", title="Before & after")
        self.assertIn("<svg", page)
        self.assertNotIn("<script>x</script>", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("Before &amp; after", page)
        self.assertNotIn("http://", page.replace("http://www.w3.org/2000/svg", ""))

    def test_html_escapes_the_unit_in_axis_labels(self):
        data = self.sample_input()
        data["unit"] = "</text><script>x</script>"
        results = compare.analyze(data, alpha=0.05, resamples=100, seed=1)
        page = compare.render_html(results, unit=data["unit"], title="t")
        self.assertNotIn("<script>x</script>", page)

    def test_html_states_the_metric_direction(self):
        self.assertIn("Higher is better", compare.render_html([], unit="req/s", title="t", higher_is_better=True))
        self.assertIn("Lower is better", compare.render_html([], unit="ms", title="t"))

    def test_html_handles_no_results(self):
        self.assertIn("No scenarios", compare.render_html([], unit="ms", title="Empty"))

    def test_format_ms_scales_units(self):
        self.assertEqual(compare.format_value(0.5, "ms"), "0.50 ms")
        self.assertEqual(compare.format_value(1234.5, "ms"), "1,234.5 ms")


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        scratch = SKILL_DIR.parents[1] / ".tmp"
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.input = self.directory / "samples.json"
        self.input.write_text(
            json.dumps(
                {
                    "unit": "ms",
                    "before": {"q": noisy(100, 5, 20, 1)},
                    "after": {"q": noisy(50, 5, 20, 2)},
                }
            )
        )

    def test_text_report_and_html_file(self):
        out = self.directory / "report.html"
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = compare.main([str(self.input), "--out", str(out), "--resamples", "500"])
        self.assertEqual(code, 0)
        self.assertIn("improved", buffer.getvalue())
        self.assertIn("<svg", out.read_text())

    def test_json_format(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = compare.main([str(self.input), "--format", "json", "--resamples", "500"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(buffer.getvalue())[0]["scenario"], "q")

    def test_exit_code_signals_regression(self):
        data = json.loads(self.input.read_text())
        data["before"], data["after"] = data["after"], data["before"]
        self.input.write_text(json.dumps(data))
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = compare.main([str(self.input), "--resamples", "500"])
        self.assertEqual(code, 2)

    def test_out_creates_missing_directories_and_writes_utf8(self):
        data = json.loads(self.input.read_text())
        data["before"] = {"requête·é": data["before"]["q"]}
        data["after"] = {"requête·é": data["after"]["q"]}
        self.input.write_text(json.dumps(data), encoding="utf-8")
        out = self.directory / "nested" / "dir" / "report.html"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(compare.main([str(self.input), "--out", str(out), "--resamples", "200"]), 0)
        self.assertIn("requête·é", out.read_text(encoding="utf-8"))

    def test_higher_is_better_flag_flips_the_exit_code(self):
        data = json.loads(self.input.read_text())
        data["before"], data["after"] = data["after"], data["before"]
        self.input.write_text(json.dumps(data))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(compare.main([str(self.input), "--resamples", "200", "--higher-is-better"]), 0)

    def test_bad_input_exits_with_usage_error(self):
        self.input.write_text("{not json")
        with self.assertRaises(SystemExit) as raised:
            compare.main([str(self.input)])
        self.assertEqual(raised.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
