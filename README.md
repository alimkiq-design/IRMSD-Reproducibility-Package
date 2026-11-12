# IRMSD: Integrated Risk Management for Software Development

[![DOI](https://zenodo.org/badge/1454958531.svg)](https://doi.org/10.5281/zenodo.24155678)

**Reproducibility package — release v0.1.0**

- **Version-specific DOI (v0.1.0):** [10.5281/zenodo.24155679](https://doi.org/10.5281/zenodo.24155679)
- **Concept DOI (all versions):** [10.5281/zenodo.24155678](https://doi.org/10.5281/zenodo.24155678)
- **GitHub repository:** https://github.com/alimkiq-design/IRMSD-Reproducibility-Package

The version-specific DOI identifies the archived v0.1.0 snapshot. The Concept DOI resolves to the overall software record and is intended for references to the project across versions.

## Purpose

This repository accompanies the manuscript *A Conceptual Framework for Integrating Risk Management Tasks into Software Development Workflows*. It documents the IRMSD framework and provides the prototype source code, deterministic risk-gating tests, sprint-analysis scripts, a synthetic demonstration dataset, and supporting metadata/documentation.

## Scope of the current release

This release includes:
- the four-layer IRMSD architecture summary and R1–R12 risk taxonomy;
- a Python prototype implementing risk scoring, effort adjustment, workflow gating, and active-risk idempotency;
- a PostgreSQL schema and automated prototype tests;
- sprint telemetry template generation and a statistical analysis script;
- a 72-row **synthetic** sprint dataset and its clearly labelled analysis output;
- documentation and provisional GitHub/Zenodo metadata.

It does **not** yet include the expert-adjudicated risk-classification benchmark, verified benchmark model-training scripts, real software-team observations, or a field-study protocol/results package. The `benchmark/` and `data/human_adjudicated/` directories are placeholders only.

## Evidence boundary

The sprint dataset contains 12 simulated teams across six sprints. It is included only to demonstrate data validation and analysis code paths. It is not field data and must not be described as empirical validation or evidence of industrial effectiveness.

Prototype tests verify deterministic software behavior; they do not evaluate classifier precision/recall, calibration, risk prediction validity, mitigation effectiveness, or organizational impact. PostgreSQL concurrency behavior has not yet been integration-tested.

In the current synthetic sprint analysis, five of six mixed-effects models fail with singular-matrix errors. The remaining schedule-variance fit emits singular covariance, boundary, and non-positive-definite Hessian warnings. Mann–Whitney U and Cohen's d use team-level means (six teams per group), not sprint rows as independent observations. These synthetic results are exploratory pipeline checks only and are not reliable confirmatory evidence.

Independent expert annotation, benchmark comparisons, and real-team/longitudinal trials remain future validation work unless complete source data, study protocols, permissions, and execution evidence are added in a later release.

## Framework summary

IRMSD links software artifacts and task-board items to candidate risk identification, human validation, ordinal risk screening, risk-adjusted effort estimation, deterministic workflow gates, mitigation actions, and verification evidence.

### Risk score and workflow tiers

For human-approved risks, probability (P) and impact (I) are rated on five-point ordinal scales:

`R = P × I` (range 1–25).

| Tier | Score | Workflow state |
|---|---:|---|
| Low | 1–6 | Ready_for_Sprint |
| Medium | 7–14 | In_Progress (Review Gate) |
| High | 15–25 | Blocked_Spike |

Effort adjustment:

`E_adj = E_init × (1 + alpha_cal × (R_max / 25))`, where `0 < alpha_cal <= 0.50`.

## Repository layout

```text
.
├── README.md
├── CITATION.cff
├── .zenodo.json
├── LICENSE_STATUS.md
├── docs/
├── prototype/
│   ├── app/
│   ├── sql/
│   └── tests/
├── sprint_pilot/
│   ├── scripts/
│   ├── templates/
│   └── tests/
├── data/
│   ├── simulated/
│   └── human_adjudicated/
├── benchmark/              # placeholder; not yet populated
└── results/
    ├── simulated/
    └── empirical/          # placeholder; no field results included
```

## Quick start: prototype tests

From `prototype/`:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

The source package's regression suite was run in the authoring environment and reported **10 passed**. Re-run locally and preserve the execution log before relying on that verification in a formal replication.

## Quick start: sprint analysis

From `sprint_pilot/`:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/analyze_sprint_pilot.py --input ../data/simulated/simulated_sprint_pilot_telemetry.csv --out ../results/simulated/pilot_statistical_results_simulated.csv
```

Expected model warnings/failures are documented in `results/simulated/data_quality_and_method_audit.json`. Synthetic data are not empirical observations.

## Licensing, data, and ethics

No software license has been assigned. See [LICENSE_STATUS.md](LICENSE_STATUS.md). Do not upload credentials, private repository content, personal information, confidential issue-tracker exports, or third-party datasets without redistribution permission. Dataset licensing and provenance must be documented separately from software licensing.

## Citation and DOI

A provisional `CITATION.cff` and `.zenodo.json` are provided. Author order, affiliations, ORCID identifiers, and license remain to be confirmed. The GitHub repository exists, but **no Zenodo record or DOI has been created**. Do not cite a DOI until Zenodo has archived a versioned GitHub release.

See [docs/GITHUB_ZENODO_SETUP.md](docs/GITHUB_ZENODO_SETUP.md) for the release workflow.
