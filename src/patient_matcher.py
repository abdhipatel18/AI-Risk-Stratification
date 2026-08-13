import logging
import pandas as pd

logger = logging.getLogger(__name__)

class PatientMatcher:
    def __init__(self):
        pass

    def consolidate_patient_data(self, df_demo, df_meds, df_labs, df_gaps, df_weights):
        """
        Consolidates relational multi-table datasets into a structured dictionary per patient ID.
        Ensures 1 master record per patient containing list of meds, most recent labs, and care gaps.
        """
        patient_records = {}

        # Convert weights dataframe into dictionary for quick lookup
        weights_lookup = {}
        for _, row in df_weights.iterrows():
            code = str(row["care_gap_code"]).strip()
            weights_lookup[code] = {
                "care_gap_name": row["care_gap_name"],
                "clinical_priority": row["clinical_priority"],
                "care_gap_weight": float(row["care_gap_weight"]),
                "max_months": int(row.get("max_recommended_scheduling_timeframe_months", 3))
            }

        # Initialize patient master entries
        for _, demo in df_demo.iterrows():
            pid = demo["patient_id"]
            patient_records[pid] = {
                "demographics": demo.to_dict(),
                "medications": [],
                "labs": [],
                "care_gaps": []
            }

        # Attach Medications
        for _, med in df_meds.iterrows():
            pid = med["patient_id"]
            if pid in patient_records:
                patient_records[pid]["medications"].append(med.to_dict())

        # Attach Labs (Sort by date descending so most recent is first)
        df_labs_sorted = df_labs.sort_values(by="test_date", ascending=False)
        for _, lab in df_labs_sorted.iterrows():
            pid = lab["patient_id"]
            if pid in patient_records:
                patient_records[pid]["labs"].append(lab.to_dict())

        # Attach Care Gaps & join weights
        for _, gap in df_gaps.iterrows():
            pid = gap["patient_id"]
            if pid in patient_records:
                gap_dict = gap.to_dict()
                code = str(gap_dict.get("care_gap_code", "")).strip()
                w_info = weights_lookup.get(code, {"care_gap_weight": 5.0, "clinical_priority": "Low", "max_months": 3})
                gap_dict["care_gap_weight"] = w_info["care_gap_weight"]
                gap_dict["clinical_priority"] = w_info["clinical_priority"]
                gap_dict["max_months"] = w_info["max_months"]
                patient_records[pid]["care_gaps"].append(gap_dict)

        logger.info(f"Consolidated records for {len(patient_records)} unique patients.")
        return patient_records, weights_lookup
