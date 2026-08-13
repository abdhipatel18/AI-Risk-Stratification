import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class FeatureEngineer:
    HIGH_RISK_MED_CATEGORIES = {"Anticoagulants", "Insulin", "Opioids", "Immunosuppressants", "Antiarrhythmics"}

    def __init__(self, ref_date="2026-08-01"):
        self.ref_date = pd.to_datetime(ref_date)

    def extract_features(self, patient_records):
        """
        Extracts clinical and operational risk features for each patient, returning a pandas DataFrame.
        """
        feature_rows = []

        for pid, record in patient_records.items():
            demo = record["demographics"]
            meds = record["medications"]
            labs = record["labs"]
            gaps = record["care_gaps"]

            # Demographics Features
            age = int(demo.get("age", 50))
            last_visit = pd.to_datetime(demo.get("last_visit_date"))
            days_since_last_visit = (self.ref_date - last_visit).days if pd.notna(last_visit) else 365
            if days_since_last_visit < 0:
                days_since_last_visit = 0

            next_appt = pd.to_datetime(demo.get("next_scheduled_appointment_date"))
            has_scheduled_appointment = 1 if (pd.notna(next_appt) and next_appt >= self.ref_date) else 0

            # Medication Features
            active_meds = [m for m in meds if str(m.get("medication_status", "")).lower() == "active"]
            num_active_meds = len(active_meds)
            num_high_risk_meds = sum(1 for m in active_meds if m.get("medication_category") in self.HIGH_RISK_MED_CATEGORIES)

            # Laboratory Features (Using most recent result per lab test type)
            latest_labs = {}
            for l in labs:
                test_name = l.get("laboratory_test_name")
                if test_name and test_name not in latest_labs:
                    latest_labs[test_name] = l

            num_abnormal_labs = sum(1 for l in latest_labs.values() if str(l.get("abnormal_result_indicator")).upper() in ["Y", "CRITICAL"])
            num_critical_labs = sum(1 for l in latest_labs.values() if str(l.get("abnormal_result_indicator")).upper() == "CRITICAL")

            # Care Gap Features
            open_gaps = [g for g in gaps if str(g.get("care_gap_status")).lower() in ["open", "overdue"]]
            overdue_gaps = [g for g in gaps if str(g.get("care_gap_status")).lower() == "overdue"]

            num_open_care_gaps = len(open_gaps)
            num_overdue_care_gaps = len(overdue_gaps)

            total_care_gap_weight = sum(float(g.get("care_gap_weight", 0.0)) for g in open_gaps)
            max_individual_care_gap_weight = max([float(g.get("care_gap_weight", 0.0)) for g in open_gaps], default=0.0)

            # Identify highest-priority open care gap
            highest_priority_gap = "None"
            if open_gaps:
                sorted_gaps = sorted(open_gaps, key=lambda x: (float(x.get("care_gap_weight", 0.0)), 1 if str(x.get("care_gap_status")).lower() == "overdue" else 0), reverse=True)
                highest_priority_gap = sorted_gaps[0].get("care_gap_name", "None")

            # Chronic Condition Indicators (Heuristic based on meds/labs/gaps)
            has_diabetes = 1 if any("diabetes" in str(m.get("medication_category")).lower() or "hba1c" in str(l.get("laboratory_test_name")).lower() for m in meds for l in labs) else 0
            has_hypertension = 1 if any("blood pressure" in str(l.get("laboratory_test_name")).lower() or "ace" in str(m.get("medication_category")).lower() for m in meds for l in labs) else 0
            num_chronic_conditions = has_diabetes + has_hypertension

            row = {
                "patient_id": pid,
                "first_name": demo.get("first_name", ""),
                "last_name": demo.get("last_name", ""),
                "age": age,
                "gender": demo.get("gender", "Unknown"),
                "clinic": demo.get("clinic", "Unknown Clinic"),
                "primary_care_provider": demo.get("primary_care_provider", "Unknown PCP"),
                "insurance_or_payer": demo.get("insurance_or_payer", "Unknown Payer"),
                "last_visit_date": str(demo.get("last_visit_date", "")),
                "next_scheduled_appointment_date": str(demo.get("next_scheduled_appointment_date", "")),
                "days_since_last_visit": days_since_last_visit,
                "has_scheduled_appointment": has_scheduled_appointment,
                "num_active_medications": num_active_meds,
                "num_high_risk_medications": num_high_risk_meds,
                "num_abnormal_laboratory_results": num_abnormal_labs,
                "num_critical_laboratory_results": num_critical_labs,
                "num_open_care_gaps": num_open_care_gaps,
                "num_overdue_care_gaps": num_overdue_care_gaps,
                "total_care_gap_weight": total_care_gap_weight,
                "max_individual_care_gap_weight": max_individual_care_gap_weight,
                "highest_priority_care_gap": highest_priority_gap,
                "num_chronic_conditions": num_chronic_conditions
            }
            feature_rows.append(row)

        df_features = pd.DataFrame(feature_rows)
        logger.info(f"Engineered features for {len(df_features)} patient profiles.")
        return df_features
