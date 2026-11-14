"""Descriptive overlap and fixed-normalization ablations of the frozen baseline."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from research.effective_weights.audit import active_mask, build_graph, leaf_values, weights

CONFIG_PATH = Path(__file__).with_name("config.json")


@dataclass(frozen=True)
class Study:
    counties: pd.Series
    baseline: pd.Series
    indicators: pd.DataFrame
    coefficients: pd.Series


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_study(path: Path, config: dict) -> Study:
    if sha256(path) != config["scores_sha256"]:
        raise ValueError("Saved scores do not match pinned v1.0.1 data")
    for name, expected in config["audit_sha256_lf"].items():
        if hashlib.sha256((ROOT / name).read_text(encoding="utf-8").encode()).hexdigest() != expected:
            raise ValueError(f"Effective-weight audit changed: {name}")
    audit_config = json.loads((ROOT / "research/effective_weights/config.json").read_text())
    frame = pd.read_csv(path).sort_values("county").reset_index(drop=True)
    if len(frame) != config["expected_counties"] or frame["county"].isna().any() or frame["county"].duplicated().any():
        raise ValueError("Expected unique, nonmissing county names in the pinned table")
    if active_mask(frame, ROOT, audit_config).any():
        raise ValueError("This study is scoped to the released all-FEMA-fallback baseline")
    graph, _ = build_graph(ROOT, audit_config, "fema_fallback")
    exact = weights(graph, audit_config["final_score"])
    coefficients = pd.Series({name: float(value) for name, value in sorted(exact.items())})
    if set(coefficients.index) != set(config["indicator_families"]):
        raise ValueError("Family mapping must cover each active terminal indicator exactly once")
    for partition in config["partitions"]:
        if any(not item.get(partition) for item in config["indicator_families"].values()):
            raise ValueError("Missing family assignment")
    all_values = leaf_values(graph, frame)
    indicators = pd.DataFrame({name: all_values[name] for name in coefficients.index})
    if not np.isfinite(indicators.to_numpy()).all():
        raise ValueError("Nonfinite normalized indicators; no imputation is permitted")
    if ((indicators < -config["atol"]) | (indicators > 100 + config["atol"])).any().any():
        raise ValueError("Normalized indicators are outside 0–100")
    baseline = pd.to_numeric(frame[audit_config["final_score"]], errors="raise")
    if not np.isfinite(baseline).all():
        raise ValueError("Nonfinite baseline score")
    reconstructed = indicators.mul(coefficients).sum(axis=1)
    np.testing.assert_allclose(reconstructed, baseline, rtol=config["rtol"], atol=config["atol"])
    return Study(frame["county"], baseline, indicators, coefficients)


def correlations(left: pd.Series, right: pd.Series) -> tuple[float | None, float | None]:
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("Need paired observations")
    if not left.index.equals(right.index):
        raise ValueError("Paired observations must have matching indices")
    if not np.isfinite(left.to_numpy()).all() or not np.isfinite(right.to_numpy()).all():
        raise ValueError("Missing or nonfinite observations cannot be silently imputed")
    if left.nunique() < 2 or right.nunique() < 2:
        return None, None
    pearson = float(left.corr(right))
    spearman = float(left.rank(method="average").corr(right.rank(method="average")))
    return pearson, spearman


def pair_table(values: pd.DataFrame, assignments: dict | None = None) -> pd.DataFrame:
    records = []
    for left, right in combinations(values.columns, 2):
        pearson, spearman = correlations(values[left], values[right])
        row = {"left": left, "right": right, "n": len(values),
               "pearson": pearson, "spearman": spearman,
               "status": "constant_indicator" if pearson is None else "estimated",
               "left_unique": values[left].nunique(), "right_unique": values[right].nunique(),
               "exact_values_equal": bool(np.array_equal(values[left], values[right])),
               "joint_normalized_zero_rows": int(((values[left] == 0) & (values[right] == 0)).sum())}
        if assignments:
            row.update({"same_source_family": assignments[left]["source_family"] == assignments[right]["source_family"],
                        "same_component_family": assignments[left]["component_family"] == assignments[right]["component_family"]})
        records.append(row)
    return pd.DataFrame(records)


def ranks(scores: pd.Series, decimals: int) -> pd.Series:
    return scores.round(decimals).rank(ascending=False, method="average")


def top_set(scores: pd.Series, counties: pd.Series, k: int, decimals: int) -> set[str]:
    """Include every county tied at the kth boundary, never alphabetically break ties."""
    min_rank = scores.round(decimals).rank(ascending=False, method="min")
    return set(counties[min_rank <= k])


def remove_family(indicators: pd.DataFrame, coefficients: pd.Series,
                  selected: list[str]) -> tuple[pd.Series, pd.Series, pd.Series, float]:
    if not selected or len(set(selected)) != len(selected) or not set(selected) <= set(coefficients.index):
        raise ValueError("Invalid family membership")
    if not np.isfinite(coefficients).all() or (coefficients < 0).any() or not np.isclose(coefficients.sum(), 1):
        raise ValueError("Expected nonnegative coefficients summing to one")
    excluded_weight = float(coefficients[selected].sum())
    if excluded_weight >= 1 or excluded_weight <= 0:
        raise ValueError("Family removal needs positive retained and excluded weight")
    remaining = [name for name in coefficients.index if name not in selected]
    excluded = indicators[selected].mul(coefficients[selected]).sum(axis=1)
    retained = indicators[remaining].mul(coefficients[remaining]).sum(axis=1)
    return retained / (1 - excluded_weight), retained, excluded, excluded_weight


def analyze(study: Study, config: dict) -> dict[str, pd.DataFrame]:
    assignments = config["indicator_families"]
    decimals, k = config["rank_round_decimals"], config["top_k"]
    baseline_rank = ranks(study.baseline, decimals)
    baseline_top = top_set(study.baseline, study.counties, k, decimals)
    profiles = []
    for name in study.indicators:
        column = study.indicators[name]
        profiles.append({"indicator": name, **assignments[name],
                         "weight_percent": 100 * study.coefficients[name], "n": len(column),
                         "unique_values": column.nunique(), "constant": column.nunique() < 2,
                         "minimum": column.min(), "maximum": column.max(),
                         "normalized_zero_rows": int((column == 0).sum()),
                         "rows_at_minimum": int((column == column.min()).sum()),
                         "standard_deviation": column.std(ddof=0)})
    summary_rows, county_rows, family_profiles, family_pairs = [], [], [], []
    for partition in config["partitions"]:
        groups = {family: [name for name in study.indicators if assignments[name][partition] == family]
                  for family in sorted({item[partition] for item in assignments.values()})}
        subindices = {}
        for family, names in groups.items():
            candidate, retained, excluded, weight = remove_family(study.indicators, study.coefficients, names)
            np.testing.assert_allclose(retained + excluded, study.baseline, rtol=config["rtol"], atol=config["atol"])
            candidate_rank = ranks(candidate, decimals)
            shift = candidate_rank - baseline_rank
            candidate_top = top_set(candidate, study.counties, k, decimals)
            _, rho = correlations(baseline_rank, candidate_rank)
            subindices[family] = excluded / weight
            family_profiles.append({"partition": partition, "family": family,
                                    "weight_percent": 100 * weight, "indicator_count": len(names),
                                    "constant_indicator_count": sum(study.indicators[name].nunique() < 2 for name in names),
                                    "constant_weight_percent": 100 * sum(study.coefficients[name] for name in names if study.indicators[name].nunique() < 2),
                                    "mean_baseline_contribution_points": excluded.mean(),
                                    "family_subindex_unique_values": subindices[family].nunique()})
            summary_rows.append({"partition": partition, "family_removed": family,
                                 "excluded_weight_percent": 100 * weight, "rank_spearman": rho,
                                 "median_absolute_rank_change": shift.abs().median(),
                                 "maximum_absolute_rank_change": shift.abs().max(),
                                 "rank_changes_at_least_threshold": int((shift.abs() >= config["large_rank_change_threshold"]).sum()),
                                 "baseline_top_count": len(baseline_top), "candidate_top_count": len(candidate_top),
                                 "top_retained": len(baseline_top & candidate_top),
                                 "top_jaccard": len(baseline_top & candidate_top) / len(baseline_top | candidate_top),
                                 "top_entrants": " | ".join(sorted(candidate_top - baseline_top)),
                                 "top_exits": " | ".join(sorted(baseline_top - candidate_top)),
                                 "mean_score_change": (candidate - study.baseline).mean()})
            for i in study.indicators.index:
                county_rows.append({"partition": partition, "family_removed": family,
                                    "county": study.counties[i], "preserved_score": study.baseline[i],
                                    "excluded_contribution_points": excluded[i], "unscaled_retained_score": retained[i],
                                    "research_renormalized_score": candidate[i],
                                    "baseline_tie_aware_rank": baseline_rank[i],
                                    "research_tie_aware_rank": candidate_rank[i],
                                    "rank_change_positive_is_down": shift[i],
                                    "baseline_top": study.counties[i] in baseline_top,
                                    "research_top": study.counties[i] in candidate_top})
        pairs = pair_table(pd.DataFrame(subindices))
        pairs.insert(0, "partition", partition)
        family_pairs.append(pairs)
    return {"indicator_profiles": pd.DataFrame(profiles),
            "indicator_correlations": pair_table(study.indicators, assignments),
            "family_profiles": pd.DataFrame(family_profiles),
            "family_correlations": pd.concat(family_pairs, ignore_index=True),
            "ablation_summary": pd.DataFrame(summary_rows), "county_ablation": pd.DataFrame(county_rows)}


def figures(tables: dict[str, pd.DataFrame], target: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = tables["ablation_summary"].query("partition == 'source_family'").sort_values("median_absolute_rank_change")
    labels = rows.family_removed.str.replace("_", " ")
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.barh(labels, rows.median_absolute_rank_change, color="#237789")
    for i, value in enumerate(rows.median_absolute_rank_change):
        ax.text(value + 0.15, i, f"{value:g}", va="center")
    ax.set_xlabel("Median absolute county-rank change (95 counties)")
    ax.set_title("Baseline ranking sensitivity to excluding one source family", loc="left", pad=18)
    ax.set_xlim(0, max(rows.median_absolute_rank_change.max() * 1.15, 1))
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.02, 0.02, "Research variants only • Fixed normalization and FEMA fallback • Retained weights rescaled to 100%", fontsize=9)
    fig.tight_layout(rect=(0, .06, 1, 1))
    fig.savefig(target / "source_family_rank_sensitivity.png", dpi=180)
    plt.close(fig)

    pairs = tables["family_correlations"].query("partition == 'source_family'")
    profiles = tables["family_profiles"].query("partition == 'source_family'")
    names = sorted(profiles.family)
    matrix = pd.DataFrame(np.nan, index=names, columns=names)
    for _, row in profiles.iterrows():
        if row.family_subindex_unique_values > 1:
            matrix.loc[row.family, row.family] = 1
    for _, row in pairs.iterrows():
        matrix.loc[row.left, row.right] = matrix.loc[row.right, row.left] = row.spearman
    fig, ax = plt.subplots(figsize=(10, 8))
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("#dddddd")
    graphic = ax.imshow(matrix, vmin=-1, vmax=1, cmap=cmap)
    ax.set_xticks(range(len(names)), [n.replace("_", " ") for n in names], rotation=45, ha="right")
    ax.set_yticks(range(len(names)), [n.replace("_", " ") for n in names])
    for y in range(len(names)):
        for x in range(len(names)):
            value = matrix.iloc[y, x]
            ax.text(x, y, "NA" if pd.isna(value) else f"{value:.2f}", ha="center", va="center",
                    color="white" if pd.notna(value) and abs(value) > .65 else "black", fontsize=9)
    fig.colorbar(graphic, ax=ax, label="Spearman correlation (descriptive)", shrink=.7)
    ax.set_title("Overlap between disjoint source-family subindices", loc="left", pad=18)
    fig.text(.02, .02, "95 counties • Saved normalized indicators • Gray/NA = constant family; no estimable correlation", fontsize=9)
    fig.tight_layout(rect=(0, .06, 1, 1))
    fig.savefig(target / "source_family_overlap.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved-scores", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(CONFIG_PATH.read_text())
    before = sha256(args.saved_scores)
    study = load_study(args.saved_scores, config)
    tables = analyze(study, config)
    frame = pd.read_csv(args.saved_scores)
    checks = []
    for left, right in config["saved_column_comparisons"]:
        checks.append({"left": left, "right": right, "n": len(frame),
                       "exact_values_equal": bool(np.array_equal(frame[left], frame[right])),
                       "max_absolute_difference": float((frame[left] - frame[right]).abs().max()),
                       "joint_zero_rows": int(((frame[left] == 0) & (frame[right] == 0)).sum())})
    tables["saved_column_comparisons"] = pd.DataFrame(checks)
    target = ROOT / config["output_dir"]
    target.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(target / f"{name}.csv", index=False, float_format="%.12g")
    figures(tables, target)
    if sha256(args.saved_scores) != before:
        raise ValueError("Saved input changed during audit")
    pairs = tables["indicator_correlations"]
    valid = pairs[pairs.status == "estimated"]
    profiles = tables["indicator_profiles"]
    verification = {"release": config["release"], "source_commit": config["source_commit"],
                    "audit_commit": config["audit_commit"], "input_sha256": before,
                    "config_sha256_lf": hashlib.sha256(CONFIG_PATH.read_text(encoding="utf-8").encode()).hexdigest(), "analysis_sha256_lf": hashlib.sha256(Path(__file__).read_text(encoding="utf-8").encode()).hexdigest(),
                    "counties": len(study.counties), "indicators": len(study.coefficients),
                    "constant_indicators": int(profiles.constant.sum()),
                    "constant_weight_percent": float(profiles.loc[profiles.constant, "weight_percent"].sum()),
                    "pair_count": len(pairs), "estimable_pairs": len(valid),
                    "high_correlation_threshold": config["high_correlation_threshold"],
                    "pairs_at_high_threshold": int((valid.spearman.abs() >= config["high_correlation_threshold"]).sum()),
                    "very_high_correlation_threshold": config["very_high_correlation_threshold"],
                    "pairs_at_very_high_threshold": int((valid.spearman.abs() >= config["very_high_correlation_threshold"]).sum()),
                    "large_rank_change_threshold": config["large_rank_change_threshold"],
                    "ablations": len(tables["ablation_summary"]), "county_variant_rows": len(tables["county_ablation"]),
                    "all_counties_FEMA_fallback": True, "input_unchanged": True,
                    "normalization": "Frozen; no re-estimation after removing a family",
                    "missingness": "Saved zero/default semantics retained; no new imputation; nonfinite inputs rejected",
                    "rank_round_decimals": config["rank_round_decimals"], "ties": "Average ranks; include all boundary ties in top-k",
                    "scope": "Descriptive baseline sensitivity, not prediction, causal effects or replacement scores",
                    "result_sha256": {p.name: sha256(p) for p in sorted(target.iterdir()) if p.suffix in (".csv", ".png")}}
    (target / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
