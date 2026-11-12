import pandas as pd

from scripts.analyze_sprint_pilot import aggregate_team_level


def test_team_level_aggregation_produces_one_row_per_team_and_metric_mean():
    df = pd.DataFrame({
        "team_id": ["T1", "T1", "T2", "T2"],
        "group_condition": ["G1_Control", "G1_Control", "G2_IRMSD", "G2_IRMSD"],
        "metric": [10.0, 20.0, 30.0, 50.0],
    })
    result = aggregate_team_level(df, "metric")
    assert len(result) == 2
    assert result.set_index("team_id").loc["T1", "metric"] == 15.0
    assert result.set_index("team_id").loc["T2", "metric"] == 40.0


def test_team_level_aggregation_preserves_group_identity():
    df = pd.DataFrame({
        "team_id": ["T1", "T1", "T2", "T2"],
        "group_condition": ["G1_Control", "G1_Control", "G2_IRMSD", "G2_IRMSD"],
        "metric": [10.0, 20.0, 30.0, 50.0],
    })
    result = aggregate_team_level(df, "metric")
    assert result.set_index("team_id").loc["T1", "group_condition"] == "G1_Control"
    assert result.set_index("team_id").loc["T2", "group_condition"] == "G2_IRMSD"


def test_team_level_aggregation_ignores_missing_metric_values():
    df = pd.DataFrame({
        "team_id": ["T1", "T1", "T2", "T2"],
        "group_condition": ["G1_Control", "G1_Control", "G2_IRMSD", "G2_IRMSD"],
        "metric": [10.0, float("nan"), 30.0, 50.0],
    })
    result = aggregate_team_level(df, "metric")
    assert result.set_index("team_id").loc["T1", "metric"] == 10.0
