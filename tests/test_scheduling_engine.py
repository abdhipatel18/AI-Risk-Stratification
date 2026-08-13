import pytest
import pandas as pd
from src.scheduling_engine import SchedulingEngine

def test_scheduling_priority_assignment():
    engine = SchedulingEngine()

    dummy_risk = pd.DataFrame([
        {
            "patient_id": "PAT-0001",
            "risk_category": "High Risk",
            "calculated_risk_score": 65.0,
            "has_scheduled_appointment": 0,
            "num_critical_laboratory_results": 1,
            "num_abnormal_laboratory_results": 1,
            "num_overdue_care_gaps": 2,
            "num_open_care_gaps": 2,
            "total_care_gap_weight": 30.0
        },
        {
            "patient_id": "PAT-0002",
            "risk_category": "Lower Risk",
            "calculated_risk_score": 12.0,
            "has_scheduled_appointment": 1,
            "num_critical_laboratory_results": 0,
            "num_abnormal_laboratory_results": 0,
            "num_overdue_care_gaps": 0,
            "num_open_care_gaps": 0,
            "total_care_gap_weight": 0.0
        }
    ])

    df_sched = engine.assign_scheduling_priority(dummy_risk)

    assert "recommended_scheduling_window" in df_sched.columns
    assert df_sched.iloc[0]["recommended_scheduling_window"] == "Schedule Within One Month"
    assert df_sched.iloc[1]["recommended_scheduling_window"] == "Already Scheduled or No Scheduling Needed"
