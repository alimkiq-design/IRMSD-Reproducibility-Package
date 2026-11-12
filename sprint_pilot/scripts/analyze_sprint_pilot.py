#!/usr/bin/env python3
"""
IRMSD sprint-pilot analysis.

Operational definitions:
- RDR (%): identified_risks / reference_risks * 100
- MLT (hours): avg_mlt_hours
- DER (%): post_release_defects / (pre_release_defects + post_release_defects) * 100
- SV (%): (completed_sp - planned_sp) / planned_sp * 100
- RWE (hours): rework_hours
- RAO (%): risk_mgmt_hours / dev_total_hours * 100

Statistical procedures:
- Linear mixed-effects model with team random intercept and group-by-sprint interaction
- Two-sided Mann-Whitney U test (descriptive/inferential comparison; does not account for clustering)
- Cohen's d using pooled standard deviation (does not account for clustering)
- Benjamini-Hochberg FDR adjustment for available LMM group-effect p-values

Interpret all results in light of the design, sample size, missingness, and model diagnostics.
"""
import argparse
import warnings

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

# Do not suppress model warnings: convergence/singularity diagnostics are relevant.
warnings.filterwarnings("default")

REQUIRED_COLS = [
    "team_id", "group_condition", "sprint_number", "planned_sp", "completed_sp",
    "reference_risks", "identified_risks", "avg_mlt_hours", "pre_release_defects",
    "post_release_defects", "rework_hours", "risk_mgmt_hours", "dev_total_hours"
]


def validate_telemetry(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required telemetry columns: {missing}")
    if len(df) == 0:
        raise ValueError("Telemetry CSV is empty. Populate genuine team observations before running analysis.")

    valid_groups = {"G1_Control", "G2_IRMSD"}
    found_groups = set(df["group_condition"].dropna().unique())
    if not valid_groups.issubset(found_groups):
        raise ValueError(f"Both 'G1_Control' and 'G2_IRMSD' must be present. Found: {found_groups}")

    numeric_cols = [c for c in REQUIRED_COLS if c not in ("team_id", "group_condition")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise ValueError(f"Column '{col}' contains missing or non-numeric values.")

    if (df["planned_sp"] <= 0).any():
        raise ValueError("'planned_sp' must be > 0 for every observation.")
    if (df["dev_total_hours"] <= 0).any():
        raise ValueError("'dev_total_hours' must be > 0 for every observation.")
    if (df["reference_risks"] < 0).any() or (df["identified_risks"] < 0).any():
        raise ValueError("Risk counts cannot be negative.")
    if (df["identified_risks"] > df["reference_risks"]).any():
        raise ValueError("identified_risks cannot exceed reference_risks; check the audit definition.")

    count_cols = [
        "reference_risks", "identified_risks",
        "pre_release_defects", "post_release_defects"
    ]
    for col in count_cols:
        if (df[col] % 1 != 0).any() or (df[col] < 0).any():
            raise ValueError(f"'{col}' must contain non-negative integer counts.")

    if (df["team_id"].isna() | (df["team_id"].astype(str).str.strip() == "")).any():
        raise ValueError("'team_id' must be populated for every row.")
    if (df["sprint_number"] < 1).any():
        raise ValueError("'sprint_number' must be >= 1.")
    if (df.groupby("team_id")["group_condition"].nunique() > 1).any():
        raise ValueError("A team_id cannot switch between experimental conditions.")


def compute_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["RDR_pct"] = (d["identified_risks"] / d["reference_risks"].replace(0, np.nan)) * 100.0
    d["SV_norm"] = ((d["completed_sp"] - d["planned_sp"]) / d["planned_sp"].replace(0, np.nan)) * 100.0
    total_defects = d["pre_release_defects"] + d["post_release_defects"]
    d["DER_pct"] = (d["post_release_defects"] / total_defects.replace(0, np.nan)) * 100.0
    d["MLT_hours"] = d["avg_mlt_hours"].astype(float)
    d["RWE_hours"] = d["rework_hours"].astype(float)
    d["RAO_pct"] = (d["risk_mgmt_hours"] / d["dev_total_hours"].replace(0, np.nan)) * 100.0
    d["group_bin"] = (d["group_condition"] == "G2_IRMSD").astype(int)
    d["sprint_centered"] = d["sprint_number"] - d["sprint_number"].mean()
    return d


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return float("nan")
    pooled_sd = np.sqrt(
        ((nx - 1) * np.var(x, ddof=1) + (ny - 1) * np.var(y, ddof=1))
        / (nx + ny - 2)
    )
    return float((np.mean(x) - np.mean(y)) / pooled_sd) if pooled_sd > 0 else 0.0


def run_statistical_suite(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        ("RDR_pct", "Risk Detection Rate (RDR, %)"),
        ("MLT_hours", "Mitigation Lead Time (MLT, hrs)"),
        ("DER_pct", "Defect Escape Rate (DER, %)"),
        ("SV_norm", "Normalized Schedule Variance (SV, %)"),
        ("RWE_hours", "Rework Effort (RWE, hrs)"),
        ("RAO_pct", "Risk Assessment Overhead (RAO, %)"),
    ]

    g1 = df[df["group_condition"] == "G1_Control"]
    g2 = df[df["group_condition"] == "G2_IRMSD"]
    rows = []
    raw_pvals = []

    for col, label in metrics:
        sub = df.dropna(subset=[col])
        v1 = g1[col].dropna().values
        v2 = g2[col].dropna().values
        if len(v1) < 2 or len(v2) < 2:
            raise ValueError(f"Metric {col} requires at least two non-missing observations in each group.")

        lmm_status = "converged"
        try:
            lmm = smf.mixedlm(
                f"{col} ~ group_bin * sprint_centered",
                sub,
                groups=sub["team_id"]
            )
            res = lmm.fit(reml=True, method="lbfgs")
            beta_g = float(res.params.get("group_bin", np.nan))
            pval = float(res.pvalues.get("group_bin", np.nan))
            ci_low, ci_high = res.conf_int().loc["group_bin"].tolist()
        except Exception as exc:
            beta_g = ci_low = ci_high = pval = np.nan
            lmm_status = f"failed: {type(exc).__name__}"

        _, mw_p = stats.mannwhitneyu(v2, v1, alternative="two-sided")
        d_val = cohens_d(v2, v1)
        raw_pvals.append(pval)
        rows.append({
            "Metric": label,
            "G1_Control_Mean_SD": f"{np.mean(v1):.2f} ± {np.std(v1, ddof=1):.2f}",
            "G2_IRMSD_Mean_SD": f"{np.mean(v2):.2f} ± {np.std(v2, ddof=1):.2f}",
            "LMM_Group_Effect": round(beta_g, 3) if not np.isnan(beta_g) else np.nan,
            "CI_95": f"[{ci_low:.2f}, {ci_high:.2f}]" if not np.isnan(ci_low) else "N/A",
            "LMM_p_value": round(float(pval), 4) if not np.isnan(pval) else np.nan,
            "MannWhitney_p": round(float(mw_p), 4),
            "Cohens_d": round(d_val, 3),
            "LMM_Status": lmm_status,
        })

    valid_idx = [i for i, p in enumerate(raw_pvals) if not np.isnan(p)]
    for i in range(len(rows)):
        rows[i]["FDR_q_value"] = np.nan
        rows[i]["Significant_FDR_0.05"] = False

    if valid_idx:
        _, fdr_qvals, _, _ = multipletests(
            [raw_pvals[i] for i in valid_idx], alpha=0.05, method="fdr_bh"
        )
        for idx, q in zip(valid_idx, fdr_qvals):
            rows[idx]["FDR_q_value"] = round(float(q), 4)
            rows[idx]["Significant_FDR_0.05"] = bool(q < 0.05)

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Run statistical analysis on IRMSD sprint pilot telemetry.")
    parser.add_argument("--input", required=True, help="Path to sprint telemetry CSV")
    parser.add_argument("--out", default="pilot_statistical_results.csv", help="Output summary CSV")
    args = parser.parse_args()

    raw = pd.read_csv(args.input)
    validate_telemetry(raw)
    derived = compute_derived_metrics(raw)
    summary_df = run_statistical_suite(derived)

    print("\n" + "=" * 73)
    print("SPRINT PILOT STATISTICAL COMPARISON (G1_Control vs G2_IRMSD)")
    print("=" * 73)
    print(summary_df.to_string(index=False))
    summary_df.to_csv(args.out, index=False, encoding="utf-8")
    print(f"\nSaved statistical results table to: {args.out}")


if __name__ == "__main__":
    main()
