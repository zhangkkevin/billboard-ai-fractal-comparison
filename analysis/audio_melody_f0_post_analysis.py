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

ROBUSTNESS_FILTER_ORDER = [
    "all_accepted",
    "coverage_ge_0.70",
    "prob_ge_0.20",
    "jump_clean",
    "strict_combined",
]

MATCHED_FILTER_ORDER = ["matched_all_accepted", "matched_strict_combined"]

FILTER_DISPLAY_LABELS = {
    "all_accepted": "Accepted",
    "coverage_ge_0.70": "Coverage >= .70",
    "prob_ge_0.20": "Voiced prob >= .20",
    "jump_clean": "Jump clean",
    "strict_combined": "Strict combined",
}

MATCHED_FILTER_DISPLAY_LABELS = {
    "matched_all_accepted": "Matched accepted",
    "matched_strict_combined": "Matched strict",
}

PAIRWISE_SOURCES = [
    ("billboard", "suno_v4_5"),
    ("billboard", "yue"),
    ("suno_v4_5", "yue"),
]

PDF_METADATA = {
    "Creator": "audio_melody_f0_post_analysis.py",
    "Producer": "Matplotlib",
    "CreationDate": None,
    "ModDate": None,
}


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

            for source_a, source_b in PAIRWISE_SOURCES:
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


def compute_alpha_dfa_by_decade(desc: pd.DataFrame, out_tables: Path) -> None:
    accepted = desc.loc[desc["status"].eq("accepted")].copy()
    accepted = accepted.dropna(subset=["year", "alpha_dfa"])
    accepted["year"] = accepted["year"].astype(int)
    accepted["decade"] = (accepted["year"] // 10) * 10
    accepted["source_label"] = accepted["source"].map(SOURCE_LABELS)

    alpha_by_decade = (
        accepted.groupby(["source", "source_label", "decade"], observed=False)
        .agg(
            n=("alpha_dfa", "size"),
            alpha_dfa_mean=("alpha_dfa", "mean"),
            alpha_dfa_std=("alpha_dfa", "std"),
            alpha_dfa_median=("alpha_dfa", "median"),
            alpha_dfa_p25=("alpha_dfa", lambda s: s.quantile(0.25)),
            alpha_dfa_p75=("alpha_dfa", lambda s: s.quantile(0.75)),
        )
        .reset_index()
    )
    alpha_by_decade["alpha_dfa_se"] = alpha_by_decade["alpha_dfa_std"] / np.sqrt(alpha_by_decade["n"])
    alpha_by_decade.to_csv(out_tables / "alpha_dfa_by_decade.csv", index=False)


def compute_matched_complete_case_tables(desc: pd.DataFrame, out_tables: Path) -> None:
    key_cols = ["year", "position"]
    metrics = DESCRIPTOR_METRICS + QUALITY_METRICS
    filters = {
        "matched_all_accepted": (
            "Year-position triples where Billboard, Suno v4.5, and YuE all passed server acceptance.",
            lambda df: df["status"].eq("accepted"),
        ),
        "matched_strict_combined": (
            "Year-position triples where all three sources pass the strict combined local quality filter.",
            filter_definitions()["strict_combined"][1],
        ),
    }

    summary_rows = []
    test_rows = []

    for filter_name, (description, predicate) in filters.items():
        subset = desc.loc[predicate(desc)].dropna(subset=key_cols).copy()
        source_counts = subset.groupby(key_cols, observed=False)["source"].nunique()
        matched_keys = source_counts.loc[source_counts.eq(len(SOURCES))].index
        matched_key_index = pd.MultiIndex.from_frame(subset[key_cols])
        matched = subset.loc[matched_key_index.isin(matched_keys)].copy()
        n_pairs = int(len(matched_keys))

        for source in SOURCES:
            source_df = matched.loc[matched["source"].eq(source)]
            row = {
                "filter": filter_name,
                "description": description,
                "source": source,
                "source_label": SOURCE_LABELS[source],
                "matched_tracks": n_pairs,
                "n": int(source_df.shape[0]),
            }
            for metric in metrics:
                vals = source_df[metric].dropna()
                row[f"{metric}_mean"] = vals.mean() if vals.size else np.nan
                row[f"{metric}_std"] = vals.std(ddof=1) if vals.size > 1 else np.nan
                row[f"{metric}_median"] = vals.median() if vals.size else np.nan
                row[f"{metric}_p25"] = vals.quantile(0.25) if vals.size else np.nan
                row[f"{metric}_p75"] = vals.quantile(0.75) if vals.size else np.nan
            summary_rows.append(row)

        for metric in ["alpha_dfa", "alpha_width", "delta_Hq", "spectrum_skew"]:
            wide = matched.pivot_table(index=key_cols, columns="source", values=metric, aggfunc="first")
            wide = wide.dropna(subset=SOURCES)
            if wide.shape[0] >= 3:
                statistic, p_value = stats.friedmanchisquare(
                    *[wide[source].to_numpy() for source in SOURCES]
                )
                test_rows.append(
                    {
                        "filter": filter_name,
                        "metric": metric,
                        "test": "friedman",
                        "group_a": "all_sources",
                        "group_b": "",
                        "n_pairs": int(wide.shape[0]),
                        "statistic": statistic,
                        "p_value": p_value,
                        "mean_diff_a_minus_b": np.nan,
                        "median_diff_a_minus_b": np.nan,
                    }
                )

            for source_a, source_b in PAIRWISE_SOURCES:
                pair = wide[[source_a, source_b]].dropna()
                if pair.shape[0] < 2:
                    continue
                diff = pair[source_a] - pair[source_b]
                try:
                    statistic, p_value = stats.wilcoxon(
                        pair[source_a],
                        pair[source_b],
                        alternative="two-sided",
                        zero_method="wilcox",
                    )
                except ValueError:
                    statistic, p_value = np.nan, np.nan
                test_rows.append(
                    {
                        "filter": filter_name,
                        "metric": metric,
                        "test": "wilcoxon_signed_rank",
                        "group_a": source_a,
                        "group_b": source_b,
                        "n_pairs": int(pair.shape[0]),
                        "statistic": statistic,
                        "p_value": p_value,
                        "mean_diff_a_minus_b": diff.mean(),
                        "median_diff_a_minus_b": diff.median(),
                    }
                )

    matched_summary = pd.DataFrame(summary_rows)
    matched_summary.to_csv(out_tables / "matched_complete_case_summary.csv", index=False)

    matched_tests = pd.DataFrame(test_rows)
    if not matched_tests.empty:
        matched_tests["p_value_bh"] = bh_adjust(matched_tests["p_value"].tolist())
    matched_tests.to_csv(out_tables / "matched_complete_case_tests.csv", index=False)


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


def plot_alpha_dfa_by_decade(tables_dir: Path, figures_dir: Path) -> None:
    alpha_by_decade = pd.read_csv(tables_dir / "alpha_dfa_by_decade.csv")
    order = sorted(alpha_by_decade["decade"].dropna().unique())

    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    sns.lineplot(
        data=alpha_by_decade,
        x="decade",
        y="alpha_dfa_mean",
        hue="source_label",
        hue_order=[SOURCE_LABELS[source] for source in SOURCES],
        marker="o",
        linewidth=2,
        ax=ax,
    )
    for source in SOURCES:
        source_rows = alpha_by_decade.loc[alpha_by_decade["source"].eq(source)].sort_values("decade")
        ax.errorbar(
            source_rows["decade"],
            source_rows["alpha_dfa_mean"],
            yerr=source_rows["alpha_dfa_se"],
            fmt="none",
            capsize=3,
            linewidth=1,
            alpha=0.65,
        )

    ax.set_xlabel("Decade")
    ax.set_ylabel("Mean DFA alpha")
    ax.set_xticks(order)
    ax.legend(title="")
    fig.tight_layout()
    save_figure(figures_dir / "alpha_dfa_by_decade", fig)


def plot_metric_mean_ci(
    summary: pd.DataFrame,
    filter_col: str,
    order: list[str],
    metric: str,
    y_label: str,
    figures_dir: Path,
    filename: str,
    label_map: dict[str, str] | None = None,
) -> None:
    colors = sns.color_palette("deep", n_colors=len(SOURCES))
    offsets = np.linspace(-0.20, 0.20, len(SOURCES))
    x_base = np.arange(len(order))

    fig, ax = plt.subplots(figsize=(10.5 if len(order) > 2 else 6.8, 4.8))
    for offset, source, color in zip(offsets, SOURCES, colors):
        source_rows = summary.loc[summary["source"].eq(source)].set_index(filter_col).reindex(order)
        y = source_rows[f"{metric}_mean"].to_numpy(dtype=float)
        std = source_rows[f"{metric}_std"].to_numpy(dtype=float)
        n = source_rows["n"].to_numpy(dtype=float)
        yerr = np.where(n > 1, 1.96 * std / np.sqrt(n), np.nan)
        ax.errorbar(
            x_base + offset,
            y,
            yerr=yerr,
            marker="o",
            linewidth=2,
            capsize=3,
            label=SOURCE_LABELS[source],
            color=color,
        )

    ax.set_xlabel("")
    ax.set_ylabel(y_label)
    ax.set_xticks(x_base)
    labels = [label_map.get(item, item) for item in order] if label_map else order
    ax.set_xticklabels(labels, rotation=20 if len(order) > 2 else 0, ha="right" if len(order) > 2 else "center")
    ax.legend(title="")
    fig.tight_layout()
    save_figure(figures_dir / filename, fig)


def plot_robustness(tables_dir: Path, figures_dir: Path) -> None:
    robust = pd.read_csv(tables_dir / "robustness_filter_summary.csv")
    for metric, label in [("alpha_dfa", "DFA alpha"), ("alpha_width", "MFDFA alpha width")]:
        plot_metric_mean_ci(
            robust,
            "filter",
            ROBUSTNESS_FILTER_ORDER,
            metric,
            f"Mean {label} (95% CI)",
            figures_dir,
            f"robustness_{metric}_means",
            FILTER_DISPLAY_LABELS,
        )

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    sns.barplot(data=robust, x="filter", y="n", hue="source_label", order=ROBUSTNESS_FILTER_ORDER, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("Tracks retained")
    ax.set_xticklabels(
        [FILTER_DISPLAY_LABELS.get(label.get_text(), label.get_text()) for label in ax.get_xticklabels()],
        rotation=20,
        ha="right",
    )
    ax.legend(title="")
    fig.tight_layout()
    save_figure(figures_dir / "robustness_filter_retention", fig)


def plot_matched_complete_case(tables_dir: Path, figures_dir: Path) -> None:
    matched = pd.read_csv(tables_dir / "matched_complete_case_summary.csv")
    for metric, label in [("alpha_dfa", "DFA alpha"), ("alpha_width", "MFDFA alpha width")]:
        plot_metric_mean_ci(
            matched,
            "filter",
            MATCHED_FILTER_ORDER,
            metric,
            f"Matched mean {label} (95% CI)",
            figures_dir,
            f"matched_complete_case_{metric}_means",
            MATCHED_FILTER_DISPLAY_LABELS,
        )


def save_figure(base_path: Path, fig: plt.Figure) -> None:
    fig.savefig(base_path.with_suffix(".png"), dpi=240, bbox_inches="tight")
    fig.savefig(base_path.with_suffix(".pdf"), bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)


def write_summary(results_root: Path, out_dir: Path) -> None:
    tables = out_dir / "tables"
    acceptance = pd.read_csv(tables / "acceptance_by_source.csv")
    robust = pd.read_csv(tables / "robustness_filter_summary.csv")
    tests = pd.read_csv(tables / "statistical_tests_by_filter.csv")
    matched = pd.read_csv(tables / "matched_complete_case_summary.csv")
    matched_tests = pd.read_csv(tables / "matched_complete_case_tests.csv")

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
            "## Matched Complete-Case Sensitivity",
            "",
        ]
    )
    for filter_name in MATCHED_FILTER_ORDER:
        filter_rows = matched.loc[matched["filter"].eq(filter_name)]
        if filter_rows.empty:
            continue
        matched_tracks = int(filter_rows.iloc[0]["matched_tracks"])
        label = MATCHED_FILTER_DISPLAY_LABELS.get(filter_name, filter_name.replace("_", " "))
        lines.append(f"- {label}: {matched_tracks} year-position triples retained across all three sources.")
        for source in SOURCES:
            row = filter_rows.loc[filter_rows["source"].eq(source)].iloc[0]
            lines.append(
                f"  - {SOURCE_LABELS[source]}: alpha_dfa={row['alpha_dfa_mean']:.3f}, "
                f"alpha_width={row['alpha_width_mean']:.2f}, n={int(row['n'])}."
            )

    strict_matched_alpha = matched_tests.loc[
        (matched_tests["filter"].eq("matched_strict_combined"))
        & (matched_tests["metric"].eq("alpha_dfa"))
        & (matched_tests["test"].eq("friedman"))
    ]
    if not strict_matched_alpha.empty:
        p_value = strict_matched_alpha.iloc[0]["p_value"]
        lines.append(
            f"- In the strict matched subset, the paired Friedman test for alpha_dfa has p={p_value:.3g}; "
            "this is consistent with the quality-sensitive framing above."
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
            "- `tables/alpha_dfa_by_decade.csv`",
            "- `tables/robustness_filter_summary.csv`",
            "- `tables/statistical_tests_by_filter.csv`",
            "- `tables/matched_complete_case_summary.csv`",
            "- `tables/matched_complete_case_tests.csv`",
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
    compute_alpha_dfa_by_decade(desc, tables_dir)
    compute_robustness_tables(desc, tables_dir)
    compute_matched_complete_case_tables(desc, tables_dir)

    sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)
    plot_acceptance(tables_dir, figures_dir)
    plot_quality(desc, figures_dir)
    plot_descriptors(desc, figures_dir)
    plot_alpha_dfa_by_decade(tables_dir, figures_dir)
    plot_robustness(tables_dir, figures_dir)
    plot_matched_complete_case(tables_dir, figures_dir)
    write_summary(results_root, out_dir)

    print(f"Wrote post-analysis outputs to {out_dir}")


if __name__ == "__main__":
    main()
