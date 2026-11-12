# Reproduction steps

This is a checklist for completing a reproducible release. Commands must be updated to match the final tested scripts and environment.

1. Record operating system, Python version, package versions, and hardware.
2. Create a clean virtual environment.
3. Install dependencies from a pinned requirements or lock file.
4. Verify dataset checksums and provenance manifests.
5. Run preprocessing and deduplication; save the exact configuration.
6. Generate and preserve project-level train/validation/test split manifests.
7. Train each benchmark model using documented seeds and hyperparameters.
8. Save per-label and aggregate metrics, thresholds, and model checkpoints where redistribution is allowed.
9. Generate sprint telemetry template; keep synthetic and field data separate.
10. Run sprint analysis and preserve warnings, convergence diagnostics, and complete statistical outputs.
11. Regenerate manuscript tables and figures from machine-readable outputs.
12. Run the entire workflow from a clean checkout and compare output checksums.

Never replace missing observations with invented values. Failed model fits and excluded records must be reported transparently.
