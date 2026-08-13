import os
import yaml
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class RiskEngine:
    def __init__(self, config_path="config/risk_rules.yaml"):
        self.config = self._load_config(config_path)

    def _load_config(self, path):
        if not os.path.exists(path):
            logger.warning(f"Config file {path} not found. Using default rules.")
            return self._default_config()
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _default_config(self):
        return {
            "demographic_risk": {"age_65_to_74_points": 5.0, "age_75_plus_points": 10.0},
            "medication_risk": {"points_per_active_med": 1.5, "points_per_high_risk_med": 5.0},
            "lab_risk": {"abnormal_result_base_points": 4.0, "critical_result_base_points": 10.0},
            "care_gap_risk": {"open_gap_weight_multiplier": 1.0, "overdue_gap_penalty_points": 5.0},
            "scheduling_risk": {"unseen_days_threshold": 180, "unseen_days_points": 8.0, "has_scheduled_appointment_discount": 15.0},
            "risk_categories": {"high_risk_min_score": 40.0, "medium_risk_min_score": 20.0}
        }

    def calculate_patient_risk(self, df_features):
        """
        Calculates risk components and overall risk score, stratifying patients and generating explanations.
        """
        df = df_features.copy()

        demo_cfg = self.config.get("demographic_risk", {})
        med_cfg = self.config.get("medication_risk", {})
        lab_cfg = self.config.get("lab_risk", {})
        gap_cfg = self.config.get("care_gap_risk", {})
        sched_cfg = self.config.get("scheduling_risk", {})
        cat_cfg = self.config.get("risk_categories", {})

        demographic_scores = []
        medication_scores = []
        laboratory_scores = []
        care_gap_scores = []
        scheduling_scores = []
        overall_scores = []
        risk_categories = []
        primary_reasons = []

        for _, row in df.iterrows():
            # 1. Demographic Risk
            age = row["age"]
            demo_score = 0.0
            if age >= 75:
                demo_score += demo_cfg.get("age_75_plus_points", 10.0)
            elif age >= 65:
                demo_score += demo_cfg.get("age_65_to_74_points", 5.0)

            # 2. Medication Risk
            med_score = (row["num_active_medications"] * med_cfg.get("points_per_active_med", 1.5)) + \
                        (row["num_high_risk_medications"] * med_cfg.get("points_per_high_risk_med", 5.0))

            # 3. Laboratory Risk
            lab_score = (row["num_abnormal_laboratory_results"] * lab_cfg.get("abnormal_result_base_points", 4.0)) + \
                        (row["num_critical_laboratory_results"] * lab_cfg.get("critical_result_base_points", 10.0))

            # 4. Care Gap Risk
            gap_score = (row["total_care_gap_weight"] * gap_cfg.get("open_gap_weight_multiplier", 1.0)) + \
                        (row["num_overdue_care_gaps"] * gap_cfg.get("overdue_gap_penalty_points", 5.0))

            # 5. Scheduling Risk
            sched_score = 0.0
            if row["days_since_last_visit"] >= sched_cfg.get("unseen_days_threshold", 180):
                sched_score += sched_cfg.get("unseen_days_points", 8.0)
            
            if row["has_scheduled_appointment"] == 1:
                sched_score -= sched_cfg.get("has_scheduled_appointment_discount", 15.0)

            # Overall Score (Clamped to non-negative)
            overall_score = max(0.0, round(demo_score + med_score + lab_score + gap_score + sched_score, 1))

            # Risk Stratification Category
            high_thresh = cat_cfg.get("high_risk_min_score", 40.0)
            med_thresh = cat_cfg.get("medium_risk_min_score", 20.0)

            if row["has_scheduled_appointment"] == 1 and overall_score < med_thresh:
                category = "No Immediate Action or Already Scheduled"
            elif overall_score >= high_thresh:
                category = "High Risk"
            elif overall_score >= med_thresh:
                category = "Medium Risk"
            else:
                category = "Lower Risk"

            # Primary Factor Explanation Generator
            reasons = []
            if row["num_overdue_care_gaps"] > 0:
                reasons.append(f"{row['num_overdue_care_gaps']} overdue care gap(s)")
            if row["num_critical_laboratory_results"] > 0:
                reasons.append(f"{row['num_critical_laboratory_results']} critical lab result(s)")
            elif row["num_abnormal_laboratory_results"] > 0:
                reasons.append(f"{row['num_abnormal_laboratory_results']} abnormal lab result(s)")
            if row["num_high_risk_medications"] > 0:
                reasons.append(f"{row['num_high_risk_medications']} high-risk medication(s)")
            if row["total_care_gap_weight"] >= 20.0:
                reasons.append(f"high total care-gap weight ({row['total_care_gap_weight']})")
            if row["days_since_last_visit"] >= 180:
                reasons.append("has not been seen in >6 months")
            if row["has_scheduled_appointment"] == 0 and category in ["High Risk", "Medium Risk"]:
                reasons.append("no appointment scheduled")
            elif row["has_scheduled_appointment"] == 1:
                reasons.append("appointment already scheduled")

            explanation = f"{category} — " + ", ".join(reasons) if reasons else f"{category} — Routine health profile"

            demographic_scores.append(demo_score)
            medication_scores.append(med_score)
            laboratory_scores.append(lab_score)
            care_gap_scores.append(gap_score)
            scheduling_scores.append(sched_score)
            overall_scores.append(overall_score)
            risk_categories.append(category)
            primary_reasons.append(explanation)

        df["demographic_risk_score"] = demographic_scores
        df["medication_risk_score"] = medication_scores
        df["laboratory_risk_score"] = laboratory_scores
        df["care_gap_risk_score"] = care_gap_scores
        df["scheduling_risk_score"] = scheduling_scores
        df["calculated_risk_score"] = overall_scores
        df["risk_category"] = risk_categories
        df["primary_reason_for_prioritization"] = primary_reasons

        logger.info(f"Risk stratification complete: {df['risk_category'].value_counts().to_dict()}")
        return df
