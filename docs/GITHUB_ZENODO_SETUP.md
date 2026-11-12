# GitHub and Zenodo publication steps

## Target repository

- GitHub account: `alimkiq-design`
- Repository: `IRMSD-Reproducibility-Package`
- URL: https://github.com/alimkiq-design/IRMSD-Reproducibility-Package
- Visibility: Public (confirm that all future uploaded material is cleared for public redistribution).

## Current GitHub state

The repository has been created and initialized with documentation and metadata files. This is an initial scaffold, not a complete replication package. Code, data, pinned dependencies, and execution logs must be added and verified before an archival release is made.

## Complete and verify the package before a DOI release

1. Add the exact prototype source code and tests used for the reported verification.
2. Record runtime versions and pinned dependencies.
3. Include the exact synthetic sprint input, generator or generation procedure, analysis scripts, and machine-readable output that reproduce the manuscript tables.
4. Document benchmark data source, source identifiers/URLs, extraction dates, licenses, transformations, exclusions, and project-level split manifest.
5. Include annotation instructions, independent annotator records, and adjudication procedures only after genuine expert annotation has been performed.
6. Run the complete workflow from a clean environment and preserve logs, warnings, and checksums.
7. Add field-study data only with appropriate permissions, consent, ethics approval where required, and de-identification.
8. Confirm author order, institutional affiliation, ORCID identifiers, copyright ownership, software license, and dataset licenses.

## Connect GitHub to Zenodo

1. Sign in to https://zenodo.org/ using the account intended to manage the project record.
2. Open Zenodo's GitHub integration/settings area and authorize access to the target repository.
3. Enable `IRMSD-Reproducibility-Package` in Zenodo's repository list.
4. Once the package is complete and tested, create a version tag and GitHub Release (for example `v1.0.0`).
5. Confirm that Zenodo archived the release and minted a DOI. Do not invent or cite a DOI before it exists.
6. Copy the version-specific DOI and add it to the manuscript's Data and Code Availability statement and the repository README.

## Suggested manuscript statement (only after publication)

`The IRMSD replication package is available at https://github.com/alimkiq-design/IRMSD-Reproducibility-Package (version [VERSION]), archived on Zenodo at https://doi.org/[DOI]. The package distinguishes prototype verification materials and synthetic pipeline-check data from any expert-adjudicated benchmark or field-study data.`

Replace `[VERSION]` and `[DOI]` only after the Zenodo record is live.

## DOI status

No Zenodo record or DOI has been created yet.
