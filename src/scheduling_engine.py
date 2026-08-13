import logging
import pandas as pd

logger = logging.getLogger(__name__)

class SchedulingEngine:
    def __init__(self):
        pass

    def assign_scheduling_priority(self, df_risk):
        """
        Assigns recommended scheduling timeframe windows (1 Month, 2 Months, 3 Months, or Already Scheduled / No Action).
        """
        df = df_risk.copy()

        scheduling_windows = []

        for _, row in df.iterrows():
            risk_cat = row["risk_category"]
            risk_score = row["calculated_risk_score"]
            has_appt = row["has_scheduled_appointment"]
            num_critical_labs = row["num_critical_laboratory_results"]
            num_overdue = row["num_overdue_care_gaps"]
            num_open = row["num_open_care_gaps"]

            # Criteria 1: Already Scheduled or No Scheduling Needed
            if has_appt == 1 and risk_cat not in ["High Risk"]:
                window = "Already Scheduled or No Scheduling Needed"
            elif num_open == 0 and num_critical_labs == 0 and risk_score < 20.0:
                window = "Already Scheduled or No Scheduling Needed"
            # Criteria 2: Schedule Within One Month
            elif risk_cat == "High Risk" or num_critical_labs > 0 or (num_overdue >= 2 and row["total_care_gap_weight"] >= 20.0):
                window = "Schedule Within One Month"
            # Criteria 3: Schedule Within Two Months
            elif risk_cat == "Medium Risk" or num_open > 0 or row["num_abnormal_laboratory_results"] > 0:
                window = "Schedule Within Two Months"
            # Criteria 4: Schedule Within Three Months
            else:
                window = "Schedule Within Three Months"

            scheduling_windows.append(window)

        df["recommended_scheduling_window"] = scheduling_windows
        logger.info(f"Scheduling window summary: {df['recommended_scheduling_window'].value_counts().to_dict()}")
        return df
