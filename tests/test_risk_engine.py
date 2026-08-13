import pytest
import pandas as pd
from src.risk_engine import RiskEngine

def test_risk_engine_calculation():
    engine = RiskEngine()

    dummy_features = pd.DataFrame([{
        "patient_id": "PAT-0001",
        "first_name": "John",
        "last_name": "Doe",
        "age": 78, # 10 pts
        "gender": "Male",
        "clinic": "Metro Clinic",
        "primary_care_provider": "Dr. Smith",
        "insurance_or_payer": "Medicare",
        "days_since_last_visit": 200, # 8 pts
        "has_scheduled_appointment": 0, # 0 discount
        "num_active_medications": 4, # 4 * 1.5 = 6 pts
        "num_high_risk_medications": 2, # 2 * 5.0 = 10 pts
        "num_abnormal_laboratory_results": 1, # 4 pts
        "num_critical_laboratory_results": 1, # 10 pts
        "num_open_care_gaps": 2,
        "num_overdue_care_gaps": 1, # 5 pts
        "total_care_gap_weight": 25.0, # 25.0 pts
        "max_individual_care_gap_weight": 25.0,
        "highest_priority_care_gap": "HbA1c Control",
        "num_chronic_conditions": 2
    }])

    df_risk = engine.calculate_patient_risk(dummy_features)

    assert "calculated_risk_score" in df_risk.columns
    assert "risk_category" in df_risk.columns
    assert "primary_reason_for_prioritization" in df_risk.columns

    score = df_risk.iloc[0]["calculated_risk_score"]
    category = df_risk.iloc[0]["risk_category"]

    # 10 + 8 + 6 + 10 + 4 + 10 + 25 + 5 = 78.0
    assert score >= 40.0
    assert category == "High Risk"
    assert "High Risk — " in df_risk.iloc[0]["primary_reason_for_prioritization"]
