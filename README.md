# IRMSD: Integrated Risk Management for Software Development

**Reproducibility package — documentation scaffold (v0.1.0)**

Repository: https://github.com/alimkiq-design/IRMSD-Reproducibility-Package

## Purpose

This repository accompanies the manuscript *A Conceptual Framework for Integrating Risk Management Tasks into Software Development Workflows*. It documents the IRMSD framework and provides a structured home for prototype-verification code, benchmark workflows, sprint-analysis scripts, data documentation, and reproducibility records.

## What this release is — and is not

This is an **initial documentation scaffold**, not yet a complete replication package. It does not currently contain the complete source code, input datasets, dependency lock files, or execution logs necessary to reproduce every result in the manuscript.

The manuscript's current evaluation includes prototype-level technical verification and an illustrative workflow walkthrough. Sprint-level results are based on **synthetic data for 12 simulated teams across six sprints**. These outputs exercise the analysis pipeline; they are not observations from industrial teams and must not be interpreted as evidence of field effectiveness.

Independent expert annotation, fully provenance-documented benchmark construction, comparative model evaluation, and live/longitudinal team trials are future validation activities unless and until their source data, protocols, and execution evidence are added here.

## Framework summary

IRMSD links software artifacts and task-board items to candidate risk identification, human validation, ordinal risk screening, risk-adjusted effort estimation, deterministic workflow gates, mitigation actions, and verification evidence.

### Risk score and workflow tiers

For human-approved risks, probability (P) and impact (I) are rated on five-point ordinal scales:

`R = P × I` (range 1–25).

The maximum active risk score for a task determines its workflow tier:

| Tier | Score | Workflow state |
|---|---:|---|
| Low | 1–6 | Ready_for_Sprint |
| Medium | 7–14 | In_Progress (Review Gate) |
| High | 15–25 | Blocked_Spike |

The manuscript also specifies the effort adjustment:

`E_adj = E_init × (1 + alpha_cal × (R_max / 25))`

where `0 < alpha_cal <= 0.50`.

## Risk taxonomy

- R1 — Requirement Ambiguity
- R2 — Requirement Instability
- R3 — Architectural Risk
- R4 — External Dependency Risk
- R5 — Security and Privacy Risk
- R6 — Performance and Scalability
- R7 — Data Integrity Risk
- R8 — Integration Risk
- R9 — Testing and Verifiability
- R10 — Deployment and Recovery
- R11 — Resource and Schedule
- R12 — Regulatory and Compliance

## Planned repository layout

```text
.
├── README.md
├── CITATION.cff
├── .zenodo.json
├── LICENSE_STATUS.md
├── docs/
├── data/
│   ├── simulated/
│   └── human_adjudicated/
├── prototype/
├── benchmark/
├── sprint_pilot/
└── results/
    ├── simulated/
    └── empirical/
```

Only add files after verifying their origin, license, completeness, and relationship to the manuscript. Keep simulated outputs separate from human-adjudicated or field-study evidence.

## Reproduction requirements before a full release

1. Add the exact prototype source code and tests used for the reported verification.
2. Record runtime versions and pinned dependencies.
3. Include the exact synthetic sprint input, generator (if applicable), analysis scripts, and machine-readable output that reproduce the manuscript tables.
4. Document the benchmark data source, source identifiers/URLs, extraction dates, licenses, transformations, exclusions, and project-level split manifest.
5. Include annotation instructions, independent annotator records, and adjudication procedures only after genuine expert annotation has been performed.
6. Run the complete workflow from a clean environment and preserve logs and checksums.
7. Add field-study data only with appropriate permissions, consent, ethics approval where required, and de-identification.

## Data, ethics, and licensing

Do not upload credentials, private repository content, personal information, confidential issue-tracker exports, or third-party datasets without redistribution permission. Document dataset licensing separately from software licensing.

No software license is assigned in this initial scaffold. See [LICENSE_STATUS.md](LICENSE_STATUS.md). A license must not be added until copyright ownership and third-party license compatibility have been confirmed.

## Citation and DOI

A provisional `CITATION.cff` and `.zenodo.json` are included for review. Confirm author order, affiliations, ORCID identifiers, release version, and metadata before creating a public release. A DOI does **not** exist yet. After the repository is linked to Zenodo and a GitHub Release is archived, update the manuscript with the version-specific DOI and the concept DOI as appropriate.

## Contact

Corresponding-author contact details: to be completed and approved by the authors.
