#!/usr/bin/env python3
"""Annotate the upstream GitHub summary SVGs without changing their design.

Percentages are calculated from the actual donut arc geometry, so they use
the same top-five denominator as the provider's chart. No invented metrics.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html import escape
from math import atan2, pi
from pathlib import Path
import re

CARD_DIR = Path("profile-summary-card-output/github_dark")
LANGUAGE_CARD = CARD_DIR / "1-repos-per-language.svg"
PROFILE_CARD = CARD_DIR / "0-profile-details.svg"

LEGEND = re.compile(
    r'<text x="16\.8" y="(?P<y>[0-9.]+)" class="gpsc-item"[^>]*>(?P<name>[^<]+)</text>'
)
ARC_PATH = re.compile(r'<g class="arc"[^>]*>\s*<path d="([^"]+)"')
NUMBER = r"[-+0-9.eE]+"
ARC_START = re.compile(
    rf"^M(?P<x0>{NUMBER}),(?P<y0>{NUMBER})"
    rf"A[0-9.]+,[0-9.]+,0,[01],1,"
    rf"(?P<x1>{NUMBER}),(?P<y1>{NUMBER})"
)
CAPTION = "contributions in the last year</text>"
MARKER = 'data-profile-enhancement="percentage"'


def arc_percent(path: str) -> float:
    match = ARC_START.match(path)
    if not match:
        raise ValueError("Unrecognized donut arc geometry; refusing to guess percentages")
    x0, y0, x1, y1 = (float(match.group(key)) for key in ("x0", "y0", "x1", "y1"))
    start, end = atan2(y0, x0), atan2(y1, x1)
    return ((end - start) % (2 * pi)) * 100 / (2 * pi)


def annotate_languages(svg: str) -> str:
    if MARKER in svg:
        raise ValueError("Language card already annotated; generate a fresh upstream SVG first")
    legends = list(LEGEND.finditer(svg))
    paths = ARC_PATH.findall(svg)
    if not legends or len(legends) != len(paths) or len(legends) > 5:
        raise ValueError("Unexpected language legend/arc count; leaving generated data untouched")
    names = [match.group("name") for match in legends]
    if "There are no" in names or "repos to show" in names:
        raise ValueError("No real repository-language data available")
    percentages = (
        [100.0] if len(paths) == 1 else [arc_percent(path) for path in paths]
    )
    if abs(sum(percentages) - 100.0) > 0.1:
        raise ValueError("Donut proportions failed validation")
    if any(not (0.0 < percent <= 100.0) for percent in percentages):
        raise ValueError("Invalid percentage found")

    iterator = iter(percentages)

    def add_percentage(match: re.Match[str]) -> str:
        percentage = next(iterator)
        return (
            match.group(0)
            + '<text x="100" y="'
            + match.group("y")
            + '" data-profile-enhancement="percentage"'
            + ' style="font-size: 10.5px; fill: #a8b9c8;">'
            + f"{percentage:.1f}%</text>"
        )

    updated = LEGEND.sub(add_percentage, svg)
    details = "; ".join(
        f"{escape(name)} {value:.1f}%" for name, value in zip(names, percentages)
    )
    title_and_desc = (
        '<title>Top five languages by repository</title>'
        '<desc>Percentages are normalized to the five languages shown: '
        + details
        + "</desc>"
    )
    updated, count = re.subn(r"(<svg\b[^>]*>)", lambda m: m.group(1) + title_and_desc, updated, count=1)
    if count != 1 or updated.count(MARKER) != len(legends):
        raise ValueError("Language annotations could not be validated")
    return updated


def annotate_profile(svg: str, updated_at: datetime) -> str:
    if svg.count(CAPTION) != 1:
        raise ValueError("Could not locate the existing contribution-chart caption")
    date_label = updated_at.astimezone(timezone.utc).strftime("%d %b %Y")
    # This stays within the chart's existing title/caption area.
    refresh_text = (
        '<text x="230" y="0" data-profile-enhancement="refreshed" '
        'style="fill: #77909c; font-size: 9px;">'
        f"Updated {date_label} UTC</text>"
    )
    return svg.replace(CAPTION, CAPTION + refresh_text, 1)


def self_test() -> None:
    example = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<text x="16.8" y="30" class="gpsc-item">JavaScript</text>'
        '<text x="16.8" y="55.2" class="gpsc-item">Python</text>'
        '<g class="arc"><path d="M0,-60A60,60,0,0,1,0,60L0,35Z"/></g>'
        '<g class="arc"><path d="M0,60A60,60,0,0,1,0,-60L0,-35Z"/></g></svg>'
    )
    annotated = annotate_languages(example)
    assert annotated.count("50.0%") == 3  # two legend values and accessible description
    assert annotated.count(MARKER) == 2
    assert "<title>Top five languages by repository</title>" in annotated
    chart = "<svg><text>contributions in the last year</text></svg>"
    result = annotate_profile(chart, datetime(2026, 10, 14, tzinfo=timezone.utc))
    assert "Updated 14 Oct 2026 UTC" in result
    assert result.count('data-profile-enhancement="refreshed"') == 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("Profile card enhancement tests passed")
        return

    # Compute and validate both before writing either card.
    language_svg = LANGUAGE_CARD.read_text(encoding="utf-8")
    profile_svg = PROFILE_CARD.read_text(encoding="utf-8")
    new_language_svg = annotate_languages(language_svg)
    new_profile_svg = annotate_profile(profile_svg, datetime.now(timezone.utc))

    LANGUAGE_CARD.write_text(new_language_svg, encoding="utf-8")
    PROFILE_CARD.write_text(new_profile_svg, encoding="utf-8")
    print("Updated top-five language percentages and contribution refresh date")


if __name__ == "__main__":
    main()
