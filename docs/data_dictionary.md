# Data dictionary and provenance requirements

## Required provenance fields for external artifacts
For every record, preserve (where legally permitted):
- stable record identifier;
- source platform and repository/project identifier;
- source URL or resolvable source reference;
- extraction date and time;
- source creation/update timestamp, if available;
- license and terms governing redistribution;
- project/domain metadata;
- text preprocessing steps;
- duplicate-detection and exclusion decisions;
- label origin (original, annotator, adjudicated, or simulated).

## Label semantics
For human annotation, document the exact meaning of positive, negative, uncertain, and not-assessed values. Do not conflate a blank cell with a negative label.

## Separation of data types
- `data/simulated/`: generated synthetic data only.
- `data/human_adjudicated/`: labels produced by independent human annotators and adjudication, with permissions and de-identification documented.
- Do not mix synthetic and empirical records in a single unmarked file.
