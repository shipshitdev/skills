#!/usr/bin/env python3
"""Compare before/after benchmark samples and render a self-contained report.

Standard library only. Reads one JSON file:

    {
      "unit": "ms",
      "before": {"scenario": [12.1, 11.8, ...]},
      "after":  {"scenario": [6.2, 6.0, ...]},
      "failures": {"before": {"scenario": 3}, "after": {}}      # optional
    }

Per scenario it reports sample count, median, mean, p95, a bootstrap confidence
interval for each median, the percent change in the median with its bootstrap
interval, a two-sided Mann-Whitney U p-value, and a Holm-adjusted p-value across
scenarios. A scenario is "improved" or "regressed" only when the adjusted
p-value is below alpha and the interval for the change excludes zero.

Exit status: 0 no regression, 1 bad input, 2 at least one scenario regressed.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import random
import statistics
import sys
from pathlib import Path

MIN_SAMPLES = 5


def percentile(samples, q):
    if not samples:
        raise ValueError("percentile of an empty sample")
    ordered = sorted(samples)
    position = q * (len(ordered) - 1)
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def median(samples):
    return percentile(samples, 0.5)


def summarize(samples):
    return {
        "n": len(samples),
        "median": median(samples),
        "mean": statistics.fmean(samples),
        "p95": percentile(samples, 0.95),
        "min": min(samples),
        "max": max(samples),
        "stdev": statistics.stdev(samples) if len(samples) > 1 else 0.0,
    }


def bootstrap_ci(samples, statistic, resamples, confidence, rng):
    size = len(samples)
    estimates = sorted(statistic([samples[rng.randrange(size)] for _ in range(size)]) for _ in range(resamples))
    tail = (1 - confidence) / 2
    return percentile(estimates, tail), percentile(estimates, 1 - tail)


def mann_whitney_p(first, second):
    """Two-sided Mann-Whitney U test, normal approximation with tie correction."""
    n1, n2 = len(first), len(second)
    pooled = sorted([(value, 0) for value in first] + [(value, 1) for value in second])
    ranks = [0.0] * len(pooled)
    tie_term = 0.0
    start = 0
    while start < len(pooled):
        end = start
        while end + 1 < len(pooled) and pooled[end + 1][0] == pooled[start][0]:
            end += 1
        average = (start + end) / 2 + 1
        for index in range(start, end + 1):
            ranks[index] = average
        count = end - start + 1
        tie_term += count**3 - count
        start = end + 1
    rank_sum = sum(rank for rank, (_, group) in zip(ranks, pooled) if group == 0)
    u1 = rank_sum - n1 * (n1 + 1) / 2
    mean = n1 * n2 / 2
    total = n1 + n2
    variance = n1 * n2 / 12 * ((total + 1) - tie_term / (total * (total - 1)))
    if variance <= 0:
        return 1.0
    z = max(0.0, abs(u1 - mean) - 0.5) / math.sqrt(variance)
    return math.erfc(z / math.sqrt(2))


def holm_adjust(p_values):
    order = sorted(range(len(p_values)), key=lambda index: p_values[index])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[index]))
        adjusted[index] = running
    return adjusted


def percent_change(before, after):
    if before == 0:
        return 0.0 if after == 0 else math.inf
    return (after - before) / before * 100


def decide(p_value, ci, alpha):
    if p_value < alpha and ci[1] < 0:
        return "improved"
    if p_value < alpha and ci[0] > 0:
        return "regressed"
    return "no significant change"


def compare_scenario(before, after, alpha, resamples, seed, before_failures=0, after_failures=0, confidence=0.95):
    before_summary = summarize(before)
    after_summary = summarize(after)
    before_summary["failures"] = before_failures
    after_summary["failures"] = after_failures
    rng = random.Random(seed)
    before_summary["median_ci"] = bootstrap_ci(before, median, resamples, confidence, rng)
    after_summary["median_ci"] = bootstrap_ci(after, median, resamples, confidence, rng)

    changes = []
    for _ in range(resamples):
        sampled_before = median([before[rng.randrange(len(before))] for _ in before])
        sampled_after = median([after[rng.randrange(len(after))] for _ in after])
        changes.append(percent_change(sampled_before, sampled_after))
    changes.sort()
    tail = (1 - confidence) / 2
    change_ci = (percentile(changes, tail), percentile(changes, 1 - tail))

    p_value = mann_whitney_p(before, after)
    if len(before) < MIN_SAMPLES or len(after) < MIN_SAMPLES:
        verdict = "insufficient samples"
    else:
        verdict = decide(p_value, change_ci, alpha)
    return {
        "before": before_summary,
        "after": after_summary,
        "change_pct": percent_change(before_summary["median"], after_summary["median"]),
        "change_ci_pct": change_ci,
        "p_value": p_value,
        "verdict": verdict,
    }


def _clean_samples(label, side, values):
    if not isinstance(values, list) or not values:
        raise ValueError(f"{side}.{label}: expected a non-empty list of numbers")
    cleaned = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{side}.{label}: samples must be finite numbers")
        cleaned.append(float(value))
    return cleaned


def analyze(data, alpha, resamples, seed):
    if not isinstance(data, dict) or "before" not in data or "after" not in data:
        raise ValueError("input needs 'before' and 'after' objects")
    before, after = data["before"], data["after"]
    if set(before) != set(after):
        missing = sorted(set(before) ^ set(after))
        raise ValueError(f"scenarios differ between before and after: {', '.join(missing)}")
    failures = data.get("failures", {})
    results = []
    for index, label in enumerate(before):
        result = compare_scenario(
            _clean_samples(label, "before", before[label]),
            _clean_samples(label, "after", after[label]),
            alpha,
            resamples,
            seed + index,
            before_failures=int(failures.get("before", {}).get(label, 0)),
            after_failures=int(failures.get("after", {}).get(label, 0)),
        )
        result["scenario"] = label
        results.append(result)
    for result, adjusted in zip(results, holm_adjust([r["p_value"] for r in results])):
        result["p_adjusted"] = adjusted
        if result["verdict"] != "insufficient samples":
            result["verdict"] = decide(adjusted, result["change_ci_pct"], alpha)
    return results


def format_value(value, unit):
    if value < 1:
        return f"{value:.2f} {unit}"
    return f"{value:,.1f} {unit}"


def format_change(value):
    return "n/a" if math.isinf(value) else f"{value:+.1f}%"


CSS = """
:root{--bg:#fff;--fg:#1b1f23;--muted:#5b6670;--grid:#d8dee4;--before:#8b949e;--after:#1a7f64;--bad:#c0392b}
@media (prefers-color-scheme:dark){:root{--bg:#0f1418;--fg:#e6edf3;--muted:#9aa7b3;--grid:#2b343c;--before:#7d8791;--after:#3fb68f;--bad:#ef6b5b}}
body{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif}
main{max-width:960px;margin:0 auto}h1{font-size:20px;margin:0 0 4px}p.note{color:var(--muted);margin:0 0 16px}
svg{width:100%;height:auto}svg text{fill:var(--fg);font-size:12px}svg .muted{fill:var(--muted)}
table{border-collapse:collapse;width:100%;margin-top:16px;font-variant-numeric:tabular-nums}
th,td{padding:6px 8px;border-bottom:1px solid var(--grid);text-align:right}th:first-child,td:first-child{text-align:left}
.regressed{color:var(--bad);font-weight:600}.improved{color:var(--after);font-weight:600}
.legend span{display:inline-block;width:10px;height:10px;margin:0 4px 0 12px}
"""


def render_html(results, unit, title):
    safe_title = html.escape(title)
    if not results:
        body = "<p>No scenarios to report.</p>"
        return _page(safe_title, body)

    left, right, row_height, gap = 230, 110, 44, 14
    width = 920
    plot = width - left - right
    upper = max(max(r["before"]["median_ci"][1], r["after"]["median_ci"][1]) for r in results)
    lower = min(min(r["before"]["median_ci"][0], r["after"]["median_ci"][0]) for r in results)
    low_log = math.log10(max(lower, 1e-3)) - 0.1
    high_log = math.log10(max(upper, 1e-3)) + 0.1
    if high_log - low_log < 0.5:
        high_log = low_log + 0.5

    def x(value):
        return left + (math.log10(max(value, 1e-3)) - low_log) / (high_log - low_log) * plot

    height = 40 + len(results) * (row_height + gap)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{safe_title}">']
    tick = math.ceil(low_log)
    while tick <= high_log:
        position = left + (tick - low_log) / (high_log - low_log) * plot
        parts.append(f'<line x1="{position:.1f}" x2="{position:.1f}" y1="20" y2="{height - 10}" stroke="var(--grid)"/>')
        parts.append(f'<text class="muted" x="{position:.1f}" y="14" text-anchor="middle">{format_value(10**tick, unit)}</text>')
        tick += 1
    for row, result in enumerate(results):
        top = 28 + row * (row_height + gap)
        label = html.escape(result["scenario"])
        parts.append(f'<text x="{left - 10}" y="{top + row_height / 2 + 4}" text-anchor="end">{label}</text>')
        for offset, (side, color) in enumerate((("before", "var(--before)"), ("after", "var(--after)"))):
            summary = result[side]
            bar_top = top + offset * (row_height / 2)
            bar_height = row_height / 2 - 4
            parts.append(f'<rect x="{left}" y="{bar_top:.1f}" width="{max(x(summary["median"]) - left, 1):.1f}" height="{bar_height:.1f}" fill="{color}" rx="2"/>')
            low, high = summary["median_ci"]
            middle = bar_top + bar_height / 2
            parts.append(f'<line x1="{x(low):.1f}" x2="{x(high):.1f}" y1="{middle:.1f}" y2="{middle:.1f}" stroke="var(--fg)" stroke-width="1.5"/>')
            parts.append(f'<text class="muted" x="{x(high) + 6:.1f}" y="{middle + 4:.1f}">{html.escape(format_value(summary["median"], unit))}</text>')
    parts.append("</svg>")

    rows = []
    for r in results:
        verdict_class = {"improved": "improved", "regressed": "regressed"}.get(r["verdict"], "")
        low, high = r["change_ci_pct"]
        rows.append(
            "<tr>"
            f"<td>{html.escape(r['scenario'])}</td>"
            f"<td>{r['before']['n']}</td><td>{r['after']['n']}</td>"
            f"<td>{html.escape(format_value(r['before']['median'], unit))}</td>"
            f"<td>{html.escape(format_value(r['after']['median'], unit))}</td>"
            f"<td>{format_change(r['change_pct'])} [{format_change(low)}, {format_change(high)}]</td>"
            f"<td>{r['p_adjusted']:.4f}</td>"
            f"<td>{r['before']['failures']} / {r['after']['failures']}</td>"
            f'<td class="{verdict_class}">{html.escape(r["verdict"])}</td>'
            "</tr>"
        )
    table = (
        "<table><thead><tr><th>Scenario</th><th>n before</th><th>n after</th><th>Median before</th>"
        "<th>Median after</th><th>Change [95% CI]</th><th>Adj. p</th><th>Failures b/a</th><th>Verdict</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
    legend = '<p class="legend"><span style="background:var(--before)"></span>before<span style="background:var(--after)"></span>after · bars are medians on a log scale, whiskers are 95% bootstrap intervals</p>'
    return _page(safe_title, "".join(parts) + legend + table)


def _page(safe_title, body):
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{safe_title}</title><style>{CSS}</style></head><body><main>"
        f"<h1>{safe_title}</h1><p class=\"note\">Lower is better. Verdicts use Holm-adjusted Mann-Whitney p-values and bootstrap intervals.</p>"
        f"{body}</main></body></html>"
    )


def _json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def render_text(results, unit):
    lines = []
    for r in results:
        low, high = r["change_ci_pct"]
        lines.append(
            f"{r['scenario']}: {format_value(r['before']['median'], unit)} -> {format_value(r['after']['median'], unit)} "
            f"({format_change(r['change_pct'])}, 95% CI [{format_change(low)}, {format_change(high)}], "
            f"adj. p={r['p_adjusted']:.4f}, n={r['before']['n']}/{r['after']['n']}) {r['verdict']}"
        )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("input", help="JSON file with before/after samples")
    parser.add_argument("--out", help="write a self-contained HTML report here")
    parser.add_argument("--title", default="Before / after")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--resamples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        data = json.loads(Path(args.input).read_text())
        results = analyze(data, args.alpha, args.resamples, args.seed)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    unit = data.get("unit", "ms")
    if args.out:
        Path(args.out).write_text(render_html(results, unit, args.title))
    if args.format == "json":
        print(json.dumps(_json_safe(results), indent=2))
    else:
        print(render_text(results, unit))
    return 2 if any(r["verdict"] == "regressed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
