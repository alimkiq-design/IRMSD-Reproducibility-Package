#!/usr/bin/env python3
"""IRMSD sprint-pilot analysis with explicit clustering and convergence diagnostics.

Definitions:
- RDR (%) = identified_risks / reference_risks * 100
- MLT (hours) = avg_mlt_hours
- DER (%) = post_release_defects / (pre_release_defects + post_release_defects) * 100
- SV (%) = (completed_sp - planned_sp) / planned_sp * 100
- RWE (hours) = rework_hours
- RAO (%) = risk_mgmt_hours / dev_total_hours * 100

The mixed model uses sprint-level observations with team random intercepts.
Mann-Whitney U and Cohen's d use team-level mean outcomes to avoid treating
repeated sprint records as independent observations. These are exploratory.
"""
import argparse
import warnings
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

REQUIRED_COLS = [
    "team_id", "group_condition", "sprint_number", "planned_sp", "completed_sp",
    "reference_risks", "identified_risks", "avg_mlt_hours", "pre_release_defects",
    "post_release_defects", "rework_hours", "risk_mgmt_hours", "dev_total_hours"
]


def validate_telemetry(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required telemetry columns: {missing}")
    if df.empty:
        raise ValueError("Telemetry CSV is empty. Populate approved observations before analysis.")
    valid_groups = {"G1_Control", "G2_IRMSD"}
    found_groups = set(df["group_condition"].dropna().unique())
    if found_groups != valid_groups:
        raise ValueError(f"Expected exactly {valid_groups}; found {found_groups}")

    numeric_cols = [c for c in REQUIRED_COLS if c not in ("team_id", "group_condition")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise ValueError(f"Column '{col}' contains missing or non-numeric values.")

    for col in ["planned_sp", "dev_total_hours"]:
        if (df[col] <= 0).any():
            raise ValueError(f"'{col}' must be > 0.")
    for col in [
        "reference_risks", "identified_risks", "pre_release_defects",
        "post_release_defects", "rework_hours", "risk_mgmt_hours"
    ]:
        if (df[col] < 0).any():
            raise ValueError(f"'{col}' cannot contain negative values.")
    if (df["identified_risks"] > df["reference_risks"]).any():
        raise ValueError("identified_risks cannot exceed reference_risks.")
    if (df["team_id"].isna() | (df["team_id"].astype(str).str.strip() == "")).any():
        raise ValueError("team_id must be populated for every row.")
    if (df["sprint_number"] < 1).any():
        raise ValueError("sprint_number must be >= 1.")
    if (df.groupby("team_id")["group_condition"].nunique() > 1).any():
        raise ValueError("A team_id cannot switch between experimental conditions.")
    if (df.groupby(["team_id", "sprint_number"]).size() > 1).any():
        raise ValueError("Duplicate team_id/sprint_number observations found.")


def compute_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["RDR_pct"] = (d["identified_risks"] / d["reference_risks"].replace(0, np.nan)) * 100.0
    d["SV_norm"] = ((d["completed_sp"] - d["planned_sp"]) / d["planned_sp"]) * 100.0
    total_defects = d["pre_release_defects"] + d["post_release_defects"]
    d["DER_pct"] = (d["post_release_defects"] / total_defects.replace(0, np.nan)) * 100.0
    d["MLT_hours"] = d["avg_mlt_hours"].astype(float)
    d["RWE_hours"] = d["rework_hours"].astype(float)
    d["RAO_pct"] = (d["risk_mgmt_hours"] / d["dev_total_hours"]) * 100.0
    d["group_bin"] = (d["group_condition"] == "G2_IRMSD").astype(int)
    d["sprint_centered"] = d["sprint_number"] - d["sprint_number"].mean()
    return d


def aggregate_team_level(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Return one mean outcome per team, retaining its experimental condition."""
    required = {"team_id", "group_condition", metric}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Cannot aggregate; missing columns: {sorted(missing)}")
    if (df.groupby("team_id")["group_condition"].nunique() > 1).any():
        raise ValueError("A team_id cannot belong to more than one condition.")
    return (
        df.groupby(["team_id", "group_condition"], as_index=False, dropna=False)[metric]
        .mean()
        .dropna(subset=[metric])
    )


def cohens_d(x: Iterable[float], y: Iterable[float]) -> float:
    x = np.asarray(list(x), dtype=float)
    y = np.asarray(list(y), dtype=float)
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return float("nan")
    pooled_var = (((nx - 1) * np.var(x, ddof=1)) + ((ny - 1) * np.var(y, ddof=1))) / (nx + ny - 2)
    pooled_sd = np.sqrt(pooled_var)
    return float((np.mean(x) - np.mean(y)) / pooled_sd) if pooled_sd > 0 else float("nan")


def run_statistical_suite(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        ("RDR_pct", "Risk Detection Rate (RDR, %)"),
        ("MLT_hours", "Mitigation Lead Time (MLT, hrs)"),
        ("DER_pct", "Defect Escape Rate (DER, %)"),
        ("SV_norm", "Normalized Schedule Variance (SV, %)"),
        ("RWE_hours", "Rework Effort (RWE, hrs)"),
        ("RAO_pct", "Risk Assessment Overhead (RAO, %)"),
    ]
    rows = []
    lmm_p_values = []

    for col, label in metrics:
        sprint_rows = df.dropna(subset=[col]).copy()
        team_rows = aggregate_team_level(sprint_rows, col)
        v1 = team_rows.loc[team_rows.group_condition == "G1_Control", col].to_numpy(dtype=float)
        v2 = team_rows.loc[team_rows.group_condition == "G2_IRMSD", col].to_numpy(dtype=float)
        if len(v1) < 2 or len(v2) < 2:
            raise ValueError(f"Metric {col} requires at least two teams per group.")

        lmm_status = "converged"
        lmm_diagnostics = []
        beta_g = ci_low = ci_high = pval = np.nan
        pval_for_fdr = np.nan
        try:
            model = smf.mixedlm(
                f"{col} ~ group_bin * sprint_centered",
                sprint_rows,
                groups=sprint_rows["team_id"]
            )
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                fitted = model.fit(reml=True, method="lbfgs")
            lmm_diagnostics = [f"{w.category.__name__}: {w.message}" for w in caught]
            beta_g = float(fitted.params.get("group_bin", np.nan))
            pval = float(fitted.pvalues.get("group_bin", np.nan))
            ci_low, ci_high = fitted.conf_int().loc["group_bin"].tolist()
            if lmm_diagnostics:
                lmm_status = "converged_with_warnings"
            else:
                pval_for_fdr = pval
        except Exception as exc:
            lmm_status = f"failed: {type(exc).__name__}"
            lmm_diagnostics = [str(exc)]

        _, mw_p = stats.mannwhitneyu(v2, v1, alternative="two-sided", method="exact")
        d_val = cohens_d(v2, v1)
        lmm_p_values.append(pval_for_fdr)
        rows.append({
            "Metric": label,
            "Teams_G1": len(v1),
            "Teams_G2": len(v2),
            "G1_Control_TeamMean_Mean_SD": f"{np.mean(v1):.2f} ± {np.std(v1, ddof=1):.2f}",
            "G2_IRMSD_TeamMean_Mean_SD": f"{np.mean(v2):.2f} ± {np.std(v2, ddof=1):.2f}",
            "LMM_Group_Effect": round(beta_g, 4) if np.isfinite(beta_g) else np.nan,
            "CI_95": f"[{ci_low:.4f}, {ci_high:.4f}]" if np.isfinite(ci_low) else "N/A",
            "LMM_p_value": round(pval, 6) if np.isfinite(pval) else np.nan,
            "MannWhitney_team_level_p": round(float(mw_p), 6),
            "Cohens_d_team_level": round(float(d_val), 4) if np.isfinite(d_val) else np.nan,
            "LMM_Status": lmm_status,
            "LMM_Warnings": " | ".join(lmm_diagnostics),
            "FDR_q_value": np.nan,
            "Significant_FDR_0.05": False,
        })

    valid = [i for i, p in enumerate(lmm_p_values) if np.isfinite(p)]
    if valid:
        _, q_values, _, _ = multipletests(
            [lmm_p_values[i] for i in valid], alpha=0.05, method="fdr_bh"
        )
        for idx, q in zip(valid, q_values):
            rows[idx]["FDR_q_value"] = round(float(q), 6)
            rows[idx]["Significant_FDR_0.05"] = bool(q < 0.05)
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze IRMSD sprint pilot telemetry.")
    parser.add_argument("--input", required=True, help="Sprint telemetry CSV")
    parser.add_argument("--out", default="pilot_statistical_results.csv", help="Output summary CSV")
    args = parser.parse_args()
    raw = pd.read_csv(args.input)
    validate_telemetry(raw)
    derived = compute_derived_metrics(raw)
    result = run_statistical_suite(derived)
    print(result.to_string(index=False))
    result.to_csv(args.out, index=False, encoding="utf-8")
    print(f"Saved: {args.out}")


if __name__ == "__main__":
    main()
