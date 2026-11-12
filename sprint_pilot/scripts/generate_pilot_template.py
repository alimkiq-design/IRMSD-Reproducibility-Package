#!/usr/bin/env python3
"""
IRMSD Sprint Pilot Telemetry Template Generator.

Generates an empty CSV schema. Populate it only with genuine, de-identified
team observations collected under an approved study protocol.
"""
import argparse
import os
import pandas as pd

COLUMNS = [
    "team_id",
    "group_condition",
    "sprint_number",
    "domain_type",
    "team_size",
    "planned_sp",
    "completed_sp",
    "reference_risks",
    "identified_risks",
    "avg_mlt_hours",
    "pre_release_defects",
    "post_release_defects",
    "rework_hours",
    "risk_mgmt_hours",
    "dev_total_hours",
]


def main():
    parser = argparse.ArgumentParser(description="Generate empty sprint pilot telemetry CSV template.")
    parser.add_argument(
        "--out",
        default="templates/sprint_pilot_telemetry_template.csv",
        help="Output CSV path"
    )
    args = parser.parse_args()

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    df = pd.DataFrame(columns=COLUMNS)
    df.to_csv(args.out, index=False, encoding="utf-8")
    print(f"Created empty telemetry template at: {args.out}")


if __name__ == "__main__":
    main()
