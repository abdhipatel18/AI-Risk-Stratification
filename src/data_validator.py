import logging
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class DataValidator:
    REQUIRED_COLUMNS = {
        "demographics": ["patient_id", "first_name", "last_name", "date_of_birth", "gender", "clinic", "primary_care_provider", "last_visit_date"],
        "medications": ["patient_id", "medication_name", "medication_category", "medication_status"],
        "labs": ["patient_id", "laboratory_test_name", "result_value", "test_date"],
        "care_gaps": ["patient_id", "care_gap_code", "care_gap_name", "care_gap_status"],
        "care_gap_weights": ["care_gap_code", "care_gap_name", "care_gap_weight"]
    }

    def __init__(self):
        self.data_quality_issues = []

    def log_issue(self, category, table_name, record_id, issue_description):
        """Records a data quality issue for reporting."""
        self.data_quality_issues.append({
            "category": category,
            "table_name": table_name,
            "record_id": str(record_id),
            "issue_description": issue_description
        })

    def validate_schema(self, datasets):
        """Validates that all required columns are present in each dataset."""
        for name, df in datasets.items():
            if name not in self.REQUIRED_COLUMNS:
                continue
            req_cols = self.REQUIRED_COLUMNS[name]
            missing_cols = [c for c in req_cols if c not in df.columns]
            if missing_cols:
                err = f"Table '{name}' missing required columns: {missing_cols}"
                logger.error(err)
                raise ValueError(err)
        return True

    def validate_and_clean_demographics(self, df):
        """Validates and cleans patient demographics dataframe."""
        df = df.copy()
        initial_count = len(df)

        # Detect missing patient identifiers
        missing_id_mask = df["patient_id"].isna() | (df["patient_id"].str.strip() == "")
        for idx, row in df[missing_id_mask].iterrows():
            self.log_issue("Missing patient identifier", "demographics", idx, f"Patient record for '{row.get('first_name', '')} {row.get('last_name', '')}' missing patient_id.")
        df = df[~missing_id_mask].copy()

        # Detect duplicate records
        dup_mask = df.duplicated(subset=["patient_id"], keep="first")
        for idx, row in df[dup_mask].iterrows():
            self.log_issue("Duplicate records", "demographics", row["patient_id"], f"Duplicate patient_id '{row['patient_id']}' detected and removed.")
        df = df[~dup_mask].copy()

        # Clean string columns
        for col in ["first_name", "last_name", "gender", "clinic", "primary_care_provider", "insurance_or_payer"]:
            if col in df.columns:
                df[col] = df[col].fillna("Unknown").str.strip()

        # Validate dates & calculate age
        df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce")
        df["last_visit_date"] = pd.to_datetime(df["last_visit_date"], errors="coerce")
        df["next_scheduled_appointment_date"] = pd.to_datetime(df["next_scheduled_appointment_date"], errors="coerce")

        today = pd.to_datetime("2026-08-01")
        invalid_dob_mask = df["date_of_birth"].isna()
        for idx, row in df[invalid_dob_mask].iterrows():
            self.log_issue("Invalid dates", "demographics", row["patient_id"], "Invalid or unparseable date_of_birth.")

        df["age"] = (today - df["date_of_birth"]).dt.days // 365
        df["age"] = df["age"].fillna(50).astype(int) # Default to 50 if invalid

        logger.info(f"Cleaned Demographics: {len(df)} valid records (removed {initial_count - len(df)} duplicate/invalid records).")
        return df

    def validate_and_clean_medications(self, df, valid_patient_ids):
        """Validates and cleans patient medications dataframe."""
        df = df.copy()

        # Unmatched patient records
        unmatched_mask = ~df["patient_id"].isin(valid_patient_ids)
        for idx, row in df[unmatched_mask].iterrows():
            self.log_issue("Unmatched patient records", "medications", row["patient_id"], f"Medication record for unknown patient_id '{row['patient_id']}'.")
        df = df[~unmatched_mask].copy()

        df["medication_name"] = df["medication_name"].fillna("Unknown Med").str.strip()
        df["medication_category"] = df["medication_category"].fillna("General").str.strip()
        df["medication_status"] = df["medication_status"].fillna("Active").str.strip()
        df["medication_adherence_indicator"] = pd.to_numeric(df["medication_adherence_indicator"], errors="coerce").fillna(1.0)

        return df

    def validate_and_clean_labs(self, df, valid_patient_ids):
        """Validates and cleans patient laboratory results dataframe."""
        df = df.copy()

        # Unmatched patient records
        unmatched_mask = ~df["patient_id"].isin(valid_patient_ids)
        for idx, row in df[unmatched_mask].iterrows():
            self.log_issue("Unmatched patient records", "labs", row["patient_id"], f"Lab record for unknown patient_id '{row['patient_id']}'.")
        df = df[~unmatched_mask].copy()

        # Missing lab values
        missing_val_mask = df["result_value"].isna() | (df["result_value"].str.strip() == "")
        for idx, row in df[missing_val_mask].iterrows():
            self.log_issue("Missing laboratory values", "labs", row["patient_id"], f"Missing result value for test '{row.get('laboratory_test_name', '')}'.")

        df["result_value_num"] = pd.to_numeric(df["result_value"], errors="coerce")
        df["test_date"] = pd.to_datetime(df["test_date"], errors="coerce")
        df["abnormal_result_indicator"] = df["abnormal_result_indicator"].fillna("N").str.strip()

        return df

    def validate_and_clean_care_gaps(self, df, valid_patient_ids, weights_df):
        """Validates and cleans patient care gaps dataframe."""
        df = df.copy()

        # Unmatched patient records
        unmatched_mask = ~df["patient_id"].isin(valid_patient_ids)
        for idx, row in df[unmatched_mask].iterrows():
            self.log_issue("Unmatched patient records", "care_gaps", row["patient_id"], f"Care gap record for unknown patient_id '{row['patient_id']}'.")
        df = df[~unmatched_mask].copy()

        # Missing care-gap weights check
        valid_gap_codes = set(weights_df["care_gap_code"].str.strip())
        missing_weight_mask = ~df["care_gap_code"].str.strip().isin(valid_gap_codes)
        for idx, row in df[missing_weight_mask].iterrows():
            self.log_issue("Missing care-gap weights", "care_gaps", row["patient_id"], f"Care gap code '{row['care_gap_code']}' has no weight defined in config.")

        df["care_gap_due_date"] = pd.to_datetime(df["care_gap_due_date"], errors="coerce")
        df["care_gap_status"] = df["care_gap_status"].fillna("Open").str.strip()

        return df

    def get_data_quality_report(self):
        """Returns the accumulated Data Quality issues as a DataFrame."""
        if not self.data_quality_issues:
            return pd.DataFrame(columns=["category", "table_name", "record_id", "issue_description"])
        return pd.DataFrame(self.data_quality_issues)
