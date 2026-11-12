# GitHub and Zenodo publication workflow

## Repository

- GitHub account: `alimkiq-design`
- Repository: https://github.com/alimkiq-design/IRMSD-Reproducibility-Package
- Default branch: `main`
- Visibility: Public

## Current archived release

Release `v0.1.0` is listed on GitHub and its Zenodo DOI badge is visible in Zenodo's GitHub integration page.

- GitHub release: https://github.com/alimkiq-design/IRMSD-Reproducibility-Package/releases/tag/v0.1.0
- Version-specific DOI (exact v0.1.0 snapshot): https://doi.org/10.5281/zenodo.24155679
- Concept DOI (all versions): https://doi.org/10.5281/zenodo.24155678

Zenodo creates one DOI for the exact version and a Concept DOI representing all versions. Use the version-specific DOI when citing this exact package release for reproducibility. Use the Concept DOI when referring to the software project as an evolving resource.

## Important scope limitations of v0.1.0

The release includes prototype source code and tests, sprint analysis scripts, documentation, and a 72-record synthetic sprint dataset. The synthetic records are pipeline-check materials only; they are not observations from real software teams.

The expert-adjudicated classification benchmark, comparative classifier benchmarks, and longitudinal real-team field data are not included. Five of six mixed-effects models failed with singular-matrix errors in the synthetic demonstration; the remaining schedule-variance model produced singularity/boundary/Hessian warnings. These results must not be represented as real-world effectiveness evidence.

## Before creating a future release

1. Confirm all authors' full names, order, affiliations, and ORCID identifiers.
2. Confirm copyright ownership and select an appropriate software license. Document dataset-specific licenses separately.
3. Add only verified code, data, and execution logs. Preserve source provenance and checksums.
4. Run the full test and reproduction workflow from a clean environment.
5. Update `CITATION.cff`, `.zenodo.json`, and the README to match the new release contents.
6. Create a new semantic version tag and GitHub Release.
7. Verify that Zenodo archived the new version and assigned a new version-specific DOI. The Concept DOI should remain the project-wide identifier.
8. Cite the new version-specific DOI in any manuscript referring to that exact release.

## Suggested manuscript Data and Code Availability statement

See `MANUSCRIPT_DATA_AVAILABILITY.md` for the wording associated with v0.1.0.
