"""Local post-analysis for the Billboard audio-melody F0 fractal run.

This script reads the server-generated F0/fractal CSVs and produces
dissertation-facing robustness tables and figures. It intentionally treats
`f0_quality.csv` and `f0_fractal_descriptors.csv` as the source of truth because
the returned `manifest.csv` may contain pre-run placeholder statuses.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats


SOURCES = ["billboard", "suno_v4_5", "yue"]
SOURCE_LABELS = {
    "billboard": "Billboard",
    "suno_v4_5": "Suno v4.5",
    "yue": "YuE",
}

QUALITY_METRICS = [
    "selected_duration_sec",
    "raw_voiced_coverage",
    "selected_voiced_coverage",
    "median_voiced_prob",
    "jump_rate",
    "octave_jump_rate",
]

DESCRIPTOR_METRICS = [
    "alpha_dfa",
    "alpha_width",
    "alpha_peak",
    "spectrum_skew",
    "delta_Hq",
    "contour_length",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-root",
        type=Path,
        default=Path("results/audio_melody_f0"),
        help="Directory containing f0_quality.csv and f0_fractal_descriptors.csv.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory. Defaults to RESULTS_ROOT/post_analysis.",
    )
    return parser.parse_args()


def ensure_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def summarize_numeric(df: pd.DataFrame, group_col: str, metrics: list[str]) -> pd.DataFrame:
    rows = []
    for group, group_df in df.groupby(group_col, sort=False):
        row = {group_col: group, "source_label": SOURCE_LABELS.get(str(group), str(group))}
        for metric in metrics:
            if metric not in group_df.columns:
                continue
            vals = group_df[metric].dropna()
            row[f"{metric}_n"] = int(vals.size)
            row[f"{metric}_mean"] = vals.mean() if vals.size else np.nan
            row[f"{metric}_std"] = vals.std(ddof=1) if vals.size > 1 else np.nan
            row[f"{metric}_median"] = vals.median() if vals.size else np.nan
            row[f"{metric}_p10"] = vals.quantile(0.10) if vals.size else np.nan
            row[f"{metric}_p25"] = vals.quantile(0.25) if vals.size else np.nan
            row[f"{metric}_p75"] = vals.quantile(0.75) if vals.size else np.nan
            row[f"{metric}_p90"] = vals.quantile(0.90) if vals.size else np.nan
            row[f"{metric}_min"] = vals.min() if vals.size else np.nan
            row[f"{metric}_max"] = vals.max() if vals.size else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    """Return Cliff's delta: P(a>b) - P(a<b)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size == 0 or b.size == 0:
        return np.nan
    greater = 0
    less = 0
    for value in a:
        greater += np.sum(value > b)
        less += np.sum(value < b)
    return float((greater - less) / (a.size * b.size))


def bh_adjust(p_values: list[float]) -> list[float]:
    """Benjamini-Hochberg adjusted p-values."""
    p = np.asarray([np.nan if value is None else value for value in p_values], dtype=float)
    out = np.full_like(p, np.nan, dtype=float)
    valid = np.where(np.isfinite(p))[0]
    if valid.size == 0:
        return out.tolist()
    order = valid[np.argsort(p[valid])]
    ranked = p[order]
    adjusted = ranked * valid.size / np.arange(1, valid.size + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0, 1)
    out[order] = adjusted
    return out.tolist()


def filter_definitions() -> dict[str, tuple[str, Callable[[pd.DataFrame], pd.Series]]]:
    return {
        "all_accepted": (
            "All tracks that passed the server F0 quality gates.",
            lambda df: df["status"].eq("accepted"),
        ),
        "coverage_ge_0.70": (
            "Accepted tracks with selected-region raw voiced coverage >= 0.70.",
            lambda df: df["status"].eq("accepted") & df["selected_voiced_coverage"].ge(0.70),
        ),
        "prob_ge_0.20": (
            "Accepted tracks with median pYIN voiced probability >= 0.20.",
            lambda df: df["status"].eq("accepted") & df["median_voiced_prob"].ge(0.20),
        ),
        "jump_clean": (
            "Accepted tracks with jump_rate <= 0.10 and octave_jump_rate <= 0.01.",
            lambda df: df["status"].eq("accepted")
            & df["jump_rate"].le(0.10)
            & df["octave_jump_rate"].le(0.01),
        ),
        "strict_combined": (
            "Accepted tracks satisfying coverage, probability, and jump filters.",
            lambda df: df["status"].eq("accepted")
            & df["selected_voiced_coverage"].ge(0.70)
            & df["median_voiced_prob"].ge(0.20)
            & df["jump_rate"].le(0.10)
            & df["octave_jump_rate"].le(0.01),
        ),
    }


def compute_acceptance_tables(quality: pd.DataFrame, out_tables: Path) -> None:
    total = quality.groupby("source", observed=False).size().rename("total_tracks")
    accepted = quality["status"].eq("success").groupby(quality["source"], observed=False).sum().rename("accepted_tracks")
    skipped = quality["status"].eq("skipped").groupby(quality["source"], observed=False).sum().rename("skipped_tracks")
    acceptance = pd.concat([total, accepted, skipped], axis=1).reset_index()
    acceptance["source_label"] = acceptance["source"].map(SOURCE_LABELS)
    acceptance["acceptance_rate"] = acceptance["accepted_tracks"] / acceptance["total_tracks"]
    acceptance.to_csv(out_tables / "acceptance_by_source.csv", index=False)

    reasons = quality.copy()
    reasons["skip_reason"] = reasons["skip_reason"].fillna("").replace("", "success")
    reason_counts = reasons.groupby(["source", "skip_reason"], observed=False).size().rename("n").reset_index()
    reason_counts["source_label"] = reason_counts["source"].map(SOURCE_LABELS)
    reason_counts = reason_counts.merge(acceptance[["source", "total_tracks", "skipped_tracks"]], on="source", how="left")
    reason_counts["pct_of_source_total"] = reason_counts["n"] / reason_counts["total_tracks"]
    reason_counts["pct_of_source_skipped"] = np.where(
        reason_counts["skip_reason"].eq("success") | reason_counts["skipped_tracks"].eq(0),
        np.nan,
        reason_counts["n"] / reason_counts["skipped_tracks"],
    )
    reason_counts.to_csv(out_tables / "skip_reasons_by_source.csv", index=False)

    by_decade = quality.copy()
    by_decade["decade"] = (by_decade["year"].astype(int) // 10) * 10
    decade = (
        by_decade.groupby(["source", "decade"], observed=False)
        .agg(
            total_tracks=("track_id", "size"),
            accepted_tracks=("status", lambda s: int((s == "success").sum())),
            skipped_tracks=("status", lambda s: int((s == "skipped").sum())),
        )
        .reset_index()
    )
    decade["source_label"] = decade["source"].map(SOURCE_LABELS)
    decade["acceptance_rate"] = decade["accepted_tracks"] / decade["total_tracks"]
    decade.to_csv(out_tables / "acceptance_by_decade.csv", index=False)


def compute_robustness_tables(desc: pd.DataFrame, out_tables: Path) -> None:
    rows = []
    test_rows = []
    filters = filter_definitions()

    for filter_name, (description, predicate) in filters.items():
        mask = predicate(desc)
        subset = desc.loc[mask].copy()
        for source in SOURCES:
            source_df = subset.loc[subset["source"].eq(source)]
            row = {
                "filter": filter_name,
                "description": description,
                "source": source,
                "source_label": SOURCE_LABELS[source],
                "n": int(source_df.shape[0]),
            }
            for metric in DESCRIPTOR_METRICS:
                vals = source_df[metric].dropna()
                row[f"{metric}_mean"] = vals.mean() if vals.size else np.nan
                row[f"{metric}_std"] = vals.std(ddof=1) if vals.size > 1 else np.nan
                row[f"{metric}_median"] = vals.median() if vals.size else np.nan
                row[f"{metric}_p25"] = vals.quantile(0.25) if vals.size else np.nan
                row[f"{metric}_p75"] = vals.quantile(0.75) if vals.size else np.nan
            rows.append(row)

        for metric in ["alpha_dfa", "alpha_width", "delta_Hq", "spectrum_skew"]:
            groups = [
                subset.loc[subset["source"].eq(source), metric].dropna().to_numpy()
                for source in SOURCES
            ]
            if all(group.size >= 2 for group in groups):
                h_stat, p_value = stats.kruskal(*groups)
                test_rows.append(
                    {
                        "filter": filter_name,
                        "metric": metric,
                        "test": "kruskal",
                        "group_a": "all_sources",
                        "group_b": "",
                        "statistic": h_stat,
                        "p_value": p_value,
                        "effect_size": np.nan,
                    }
                )

            for source_a, source_b in [
                ("billboard", "suno_v4_5"),
                ("billboard", "yue"),
                ("suno_v4_5", "yue"),
            ]:
                a = subset.loc[subset["source"].eq(source_a), metric].dropna().to_numpy()
                b = subset.loc[subset["source"].eq(source_b), metric].dropna().to_numpy()
                if a.size >= 2 and b.size >= 2:
                    u_stat, p_value = stats.mannwhitneyu(a, b, alternative="two-sided")
                    test_rows.append(
                        {
                            "filter": filter_name,
                            "metric": metric,
                            "test": "mannwhitney_u",
                            "group_a": source_a,
                            "group_b": source_b,
                            "statistic": u_stat,
                            "p_value": p_value,
                            "effect_size": cliffs_delta(a, b),
                        }
                    )

    robustness = pd.DataFrame(rows)
    robustness.to_csv(out_tables / "robustness_filter_summary.csv", index=False)

    tests = pd.DataFrame(test_rows)
    if not tests.empty:
        tests["p_value_bh"] = bh_adjust(tests["p_value"].tolist())
    tests.to_csv(out_tables / "statistical_tests_by_filter.csv", index=False)


def plot_acceptance(tables_dir: Path, figures_dir: Path) -> None:
    acceptance = pd.read_csv(tables_dir / "acceptance_by_source.csv")
    decade = pd.read_csv(tables_dir / "acceptance_by_decade.csv")
    reasons = pd.read_csv(tables_dir / "skip_reasons_by_source.csv")

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    sns.barplot(data=acceptance, x="source_label", y="acceptance_rate", ax=ax, color="#4C78A8")
    ax.set_xlabel("")
    ax.set_ylabel("Accepted contour rate")
    ax.set_ylim(0, 1)
    for container in ax.containers:
        ax.bar_label(container, labels=[f"{v:.1%}" for v in acceptance["acceptance_rate"]], padding=3)
    fig.tight_layout()
    save_figure(figures_dir / "acceptance_rate_by_source", fig)

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    sns.lineplot(
        data=decade,
        x="decade",
        y="acceptance_rate",
        hue="source_label",
        marker="o",
        ax=ax,
    )
    ax.set_xlabel("Decade")
    ax.set_ylabel("Accepted contour rate")
    ax.set_ylim(0, 1)
    ax.legend(title="")
    fig.tight_layout()
    save_figure(figures_dir / "acceptance_rate_by_decade", fig)

    skipped = reasons.loc[~reasons["skip_reason"].eq("success")].copy()
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    sns.barplot(data=skipped, x="source_label", y="n", hue="skip_reason", ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("Skipped tracks")
    ax.legend(title="Skip reason")
    fig.tight_layout()
    save_figure(figures_dir / "skip_reasons_by_source", fig)


def plot_quality(desc: pd.DataFrame, figures_dir: Path) -> None:
    accepted = desc.loc[desc["status"].eq("accepted")].copy()
    accepted["source_label"] = accepted["source"].map(SOURCE_LABELS)
    panels = [
        ("selected_voiced_coverage", "Selected voiced coverage"),
        ("median_voiced_prob", "Median pYIN voiced probability"),
        ("jump_rate", "Jump rate"),
        ("octave_jump_rate", "Octave-jump rate"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for ax, (metric, label) in zip(axes.flat, panels):
        sns.boxplot(data=accepted, x="source_label", y=metric, ax=ax, color="#F2F2F2")
        sns.stripplot(data=accepted, x="source_label", y=metric, ax=ax, color="#333333", alpha=0.2, size=2)
        ax.set_xlabel("")
        ax.set_ylabel(label)
    fig.tight_layout()
    save_figure(figures_dir / "quality_metrics_by_source", fig)


def plot_descriptors(desc: pd.DataFrame, figures_dir: Path) -> None:
    accepted = desc.loc[desc["status"].eq("accepted")].copy()
    accepted["source_label"] = accepted["source"].map(SOURCE_LABELS)
    for metric, label in [
        ("alpha_dfa", "DFA alpha"),
        ("alpha_width", "MFDFA alpha width"),
        ("delta_Hq", "Delta H(q)"),
        ("spectrum_skew", "Spectrum skew"),
    ]:
        fig, ax = plt.subplots(figsize=(7.2, 4.4))
        sns.violinplot(data=accepted, x="source_label", y=metric, ax=ax, inner="quartile", cut=0)
        ax.set_xlabel("")
        ax.set_ylabel(label)
        fig.tight_layout()
        save_figure(figures_dir / f"{metric}_distribution_by_source", fig)


def plot_robustness(tables_dir: Path, figures_dir: Path) -> None:
    robust = pd.read_csv(tables_dir / "robustness_filter_summary.csv")
    order = ["all_accepted", "coverage_ge_0.70", "prob_ge_0.20", "jump_clean", "strict_combined"]
    for metric, label in [("alpha_dfa", "DFA alpha"), ("alpha_width", "MFDFA alpha width")]:
        fig, ax = plt.subplots(figsize=(10.5, 4.8))
        sns.pointplot(
            data=robust,
            x="filter",
            y=f"{metric}_mean",
            hue="source_label",
            order=order,
            dodge=0.35,
            markers="o",
            errorbar=None,
            ax=ax,
        )
        ax.set_xlabel("")
        ax.set_ylabel(f"Mean {label}")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")
        ax.legend(title="")
        fig.tight_layout()
        save_figure(figures_dir / f"robustness_{metric}_means", fig)

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    sns.barplot(data=robust, x="filter", y="n", hue="source_label", order=order, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("Tracks retained")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")
    ax.legend(title="")
    fig.tight_layout()
    save_figure(figures_dir / "robustness_filter_retention", fig)


def save_figure(base_path: Path, fig: plt.Figure) -> None:
    fig.savefig(base_path.with_suffix(".png"), dpi=240, bbox_inches="tight")
    fig.savefig(base_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def write_summary(results_root: Path, out_dir: Path) -> None:
    tables = out_dir / "tables"
    acceptance = pd.read_csv(tables / "acceptance_by_source.csv")
    robust = pd.read_csv(tables / "robustness_filter_summary.csv")
    tests = pd.read_csv(tables / "statistical_tests_by_filter.csv")

    def row_for(filter_name: str, source: str) -> pd.Series:
        return robust.loc[(robust["filter"].eq(filter_name)) & (robust["source"].eq(source))].iloc[0]

    lines = [
        "# Audio-Melody F0 Post-Analysis Summary",
        "",
        "This local post-analysis reads the server outputs in `results/audio_melody_f0/`.",
        "`f0_quality.csv` and `f0_fractal_descriptors.csv` are treated as the source of truth; `manifest.csv` may contain pre-run placeholder statuses.",
        "",
        "## Acceptance",
        "",
    ]
    for _, row in acceptance.iterrows():
        lines.append(
            f"- {row['source_label']}: {int(row['accepted_tracks'])}/{int(row['total_tracks'])} accepted "
            f"({row['acceptance_rate']:.1%})."
        )

    lines.extend(
        [
            "",
            "## Fractal Descriptors",
            "",
            "Accepted-set means:",
        ]
    )
    for source in SOURCES:
        row = row_for("all_accepted", source)
        lines.append(
            f"- {SOURCE_LABELS[source]}: alpha_dfa={row['alpha_dfa_mean']:.3f}, "
            f"alpha_width={row['alpha_width_mean']:.2f}, n={int(row['n'])}."
        )

    lines.extend(
        [
            "",
            "Strict quality-filter means (`coverage >= .70`, `median_voiced_prob >= .20`, "
            "`jump_rate <= .10`, `octave_jump_rate <= .01`):",
        ]
    )
    for source in SOURCES:
        row = row_for("strict_combined", source)
        lines.append(
            f"- {SOURCE_LABELS[source]}: alpha_dfa={row['alpha_dfa_mean']:.3f}, "
            f"alpha_width={row['alpha_width_mean']:.2f}, n={int(row['n'])}."
        )

    alpha_tests = tests.loc[(tests["filter"].eq("strict_combined")) & (tests["metric"].eq("alpha_dfa"))]
    kruskal = alpha_tests.loc[alpha_tests["test"].eq("kruskal")]
    if not kruskal.empty:
        p_value = kruskal.iloc[0]["p_value"]
        lines.extend(
            [
                "",
                "## Robustness Interpretation",
                "",
                f"The accepted-set comparison shows source differences, but under the strict combined quality filter "
                f"the global alpha_dfa Kruskal-Wallis p-value is {p_value:.3g}. This supports a cautious framing: "
                "the strongest result is about contour recoverability and F0 reliability, while fractal descriptor "
                "differences should be presented as quality-sensitive rather than definitive melodic differences.",
            ]
        )

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `tables/acceptance_by_source.csv`",
            "- `tables/acceptance_by_decade.csv`",
            "- `tables/skip_reasons_by_source.csv`",
            "- `tables/quality_summary_by_source.csv`",
            "- `tables/descriptor_summary_by_source.csv`",
            "- `tables/robustness_filter_summary.csv`",
            "- `tables/statistical_tests_by_filter.csv`",
            "- `figures/*.png` and `figures/*.pdf`",
            "",
            f"Source results root: `{results_root}`",
        ]
    )
    (out_dir / "post_analysis_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    results_root = args.results_root
    out_dir = args.out_dir or (results_root / "post_analysis")
    tables_dir = out_dir / "tables"
    figures_dir = out_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    quality_path = results_root / "f0_quality.csv"
    desc_path = results_root / "f0_fractal_descriptors.csv"
    if not quality_path.exists():
        raise FileNotFoundError(quality_path)
    if not desc_path.exists():
        raise FileNotFoundError(desc_path)

    quality = pd.read_csv(quality_path)
    desc = pd.read_csv(desc_path)
    quality = ensure_numeric(quality, ["year"] + QUALITY_METRICS)
    desc = ensure_numeric(desc, ["year"] + QUALITY_METRICS + DESCRIPTOR_METRICS)

    compute_acceptance_tables(quality, tables_dir)
    quality.loc[quality["status"].eq("success")].pipe(
        summarize_numeric, "source", QUALITY_METRICS
    ).to_csv(tables_dir / "quality_summary_by_source.csv", index=False)
    desc.loc[desc["status"].eq("accepted")].pipe(
        summarize_numeric, "source", DESCRIPTOR_METRICS + QUALITY_METRICS
    ).to_csv(tables_dir / "descriptor_summary_by_source.csv", index=False)
    compute_robustness_tables(desc, tables_dir)

    sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)
    plot_acceptance(tables_dir, figures_dir)
    plot_quality(desc, figures_dir)
    plot_descriptors(desc, figures_dir)
    plot_robustness(tables_dir, figures_dir)
    write_summary(results_root, out_dir)

    print(f"Wrote post-analysis outputs to {out_dir}")


if __name__ == "__main__":
    main()
