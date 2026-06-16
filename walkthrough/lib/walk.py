"""Shared helpers for the full-stack-carbon walkthrough segments.

Each segment recomputes a tool's result from committed data, writes a small
``result.json`` (a headline number plus the handoff values the next segment
consumes), and renders a figure. These helpers keep that uniform across the six
segments and let ``lib/verify_chain.py`` check that the numbers handed from one
tool to the next are mutually consistent.

A segment's recompute script typically does:

    import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
    import walk
    walk.save_result(walk.seg_dir(__file__), {...})
    walk.bar_chart(walk.seg_dir(__file__) / "figures" / "x.png", labels, values, title=...)
"""
from __future__ import annotations

import json
from pathlib import Path

# .../full-stack-carbon and .../full-stack-carbon/walkthrough
SUITE_ROOT = Path(__file__).resolve().parents[2]
WALK_ROOT = Path(__file__).resolve().parents[1]


def seg_dir(script_file) -> Path:
    """The segment directory that owns ``script_file`` (its recompute.py)."""
    return Path(script_file).resolve().parent


def _result_path(seg, golden: bool) -> Path:
    return Path(seg) / ("golden" if golden else "figures") / "result.json"


def save_result(seg, data: dict) -> Path:
    """Write a segment's live result.json under figures/."""
    p = _result_path(seg, golden=False)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n")
    return p


def load_result(seg, golden: bool = False) -> dict:
    """Read a segment's result.json (live by default, committed golden if golden=True)."""
    return json.loads(_result_path(seg, golden=golden).read_text())


def fmt_kg(value, *, is_kg: bool = True) -> str:
    kg = value if is_kg else value / 1000.0
    return f"{kg:,.1f} kgCO2e"


def bar_chart(out_png, labels, values, *, title, ylabel="kgCO2e",
              color=None, annotate=True, figsize=(7.2, 4.3)):
    """Render a labelled bar chart to ``out_png`` (headless / Agg)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar([str(x) for x in labels], values, color=color or "#3b7a57")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if annotate:
        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v:,.1f}",
                    ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def grouped_bar(out_png, groups, series: dict, *, title, ylabel="kgCO2e",
                colors=None, figsize=(7.2, 4.3)):
    """Grouped bar chart. ``groups`` are x labels; ``series`` maps a name to a
    list of values (one per group)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.arange(len(groups))
    n = max(len(series), 1)
    w = 0.8 / n
    colors = colors or {}
    fig, ax = plt.subplots(figsize=figsize)
    for i, (name, vals) in enumerate(series.items()):
        ax.bar(x + (i - (n - 1) / 2) * w, vals, w, label=name, color=colors.get(name))
    ax.set_xticks(x)
    ax.set_xticklabels([str(g) for g in groups])
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(frameon=False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out
