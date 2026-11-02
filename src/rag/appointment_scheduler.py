"""
Appointment Scheduling Engine for Patient Risk Stratification.
Generates valid date/time slots aligned with clinical risk levels and manages bookings.
"""

import os
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

STANDARD_TIME_SLOTS = [
    "09:00 AM",
    "09:45 AM",
    "10:30 AM",
    "11:15 AM",
    "01:30 PM",
    "02:15 PM",
    "03:00 PM",
    "03:45 PM",
    "04:30 PM"
]

class AppointmentScheduler:
    def __init__(
        self,
        results_file: str = "data/output/patient_risk_prioritization_results.csv",
        demographics_file: str = "data/input/patient_demographics.csv",
        appointments_file: str = "data/output/scheduled_appointments.json",
        reference_date: Optional[str] = None
    ):
        self.results_file = results_file
        self.demographics_file = demographics_file
        self.appointments_file = appointments_file
        
        # Use provided reference date or current date
        if reference_date:
            self.ref_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
        else:
            self.ref_date = datetime.now().date()
            
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.appointments_file), exist_ok=True)
        if not os.path.exists(self.appointments_file):
            with open(self.appointments_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def load_appointments(self) -> List[Dict[str, Any]]:
        try:
            with open(self.appointments_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading appointments: {e}")
            return []

    def save_appointments(self, appointments: List[Dict[str, Any]]):
        try:
            with open(self.appointments_file, "w", encoding="utf-8") as f:
                json.dump(appointments, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving appointments: {e}")

    def get_patient_data(self, patient_id: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.results_file):
            return None
        df = pd.read_csv(self.results_file)
        match = df[df["patient_id"].astype(str).str.upper() == patient_id.strip().upper()]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def get_risk_scheduling_window_days(self, risk_category: str) -> tuple[int, int]:
        """
        Returns (start_day_offset, end_day_offset) based on clinical risk tier.
        - High Risk: 1 to 14 days (urgent / within 1 month)
        - Medium Risk: 15 to 45 days (within 1-2 months)
        - Lower Risk: 45 to 90 days (routine within 3 months)
        """
        cat = str(risk_category).lower()
        if "high" in cat:
            return (1, 14)
        elif "medium" in cat:
            return (15, 45)
        else:
            return (45, 90)

    def get_available_slots(self, patient_id: str, limit: int = 6) -> Dict[str, Any]:
        """
        Generates available, conflict-free appointment slots tailored to the patient's risk level.
        """
        patient = self.get_patient_data(patient_id)
        if not patient:
            return {"error": f"Patient ID '{patient_id}' not found.", "slots": []}

        risk_category = str(patient.get("risk_category", "Lower Risk"))
        provider = str(patient.get("primary_care_provider", "Assigned PCP"))
        clinic = str(patient.get("clinic", "Community Health Clinic"))
        
        start_offset, end_offset = self.get_risk_scheduling_window_days(risk_category)
        
        existing_appointments = self.load_appointments()
        booked_keys = {
            f"{appt['provider']}_{appt['appointment_date']}_{appt['appointment_time']}"
            for appt in existing_appointments
            if appt.get("status") == "Confirmed"
        }

        generated_slots = []
        current_offset = start_offset

        while len(generated_slots) < limit and current_offset <= (end_offset + 30):
            target_date = self.ref_date + timedelta(days=current_offset)
            current_offset += 1
            
            # Skip weekends (Saturday=5, Sunday=6)
            if target_date.weekday() >= 5:
                continue

            date_str = target_date.strftime("%Y-%m-%d")
            day_name = target_date.strftime("%A")

            for time_slot in STANDARD_TIME_SLOTS:
                slot_key = f"{provider}_{date_str}_{time_slot}"
                if slot_key not in booked_keys:
                    slot_desc = f"{date_str} ({day_name}) at {time_slot}"
                    generated_slots.append({
                        "date": date_str,
                        "day": day_name,
                        "time": time_slot,
                        "display": slot_desc,
                        "provider": provider,
                        "clinic": clinic
                    })
                    if len(generated_slots) >= limit:
                        break

        # Recommended window message
        if "high" in risk_category.lower():
            window_msg = "Urgent / High Priority: Within 1 to 2 Weeks (Fasting / Morning slots recommended)"
        elif "medium" in risk_category.lower():
            window_msg = "Moderate Priority: Within 1 to 2 Months"
        else:
            window_msg = "Routine Care: Within 2 to 3 Months"

        return {
            "patient_id": patient_id,
            "patient_name": f"{patient.get('first_name')} {patient.get('last_name')}",
            "risk_category": risk_category,
            "recommended_window": window_msg,
            "provider": provider,
            "clinic": clinic,
            "slots": generated_slots
        }

    def book_appointment(
        self,
        patient_id: str,
        appointment_date: str,
        appointment_time: str,
        reason: Optional[str] = None,
        care_gap_addressed: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confirms an appointment, stores it, and updates patient datasets.
        """
        patient = self.get_patient_data(patient_id)
        if not patient:
            return {"success": False, "message": f"Patient '{patient_id}' not found."}

        # Validate date format
        try:
            datetime.strptime(appointment_date, "%Y-%m-%d")
        except ValueError:
            return {"success": False, "message": f"Invalid date format: '{appointment_date}'. Expected YYYY-MM-DD."}

        provider = str(patient.get("primary_care_provider", "Assigned PCP"))
        clinic = str(patient.get("clinic", "Community Health Clinic"))
        patient_name = f"{patient.get('first_name')} {patient.get('last_name')}"
        risk_category = str(patient.get("risk_category", "Lower Risk"))

        appointments = self.load_appointments()

        # Check for duplicate slot
        for appt in appointments:
            if (
                appt.get("provider") == provider and
                appt.get("appointment_date") == appointment_date and
                appt.get("appointment_time") == appointment_time and
                appt.get("status") == "Confirmed"
            ):
                return {
                    "success": False,
                    "message": f"Slot on {appointment_date} at {appointment_time} with {provider} is already booked. Please pick another slot."
                }

        # Create new appointment record
        appt_id = f"APT-{1000 + len(appointments) + 1}"
        new_appointment = {
            "appointment_id": appt_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "provider": provider,
            "clinic": clinic,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "risk_category": risk_category,
            "reason": reason or patient.get("primary_reason_for_prioritization") or "Clinical follow-up",
            "care_gap_addressed": care_gap_addressed or patient.get("highest_priority_care_gap") or "General Exam",
            "status": "Confirmed",
            "created_at": datetime.now().isoformat()
        }

        # Save to appointments file
        appointments.append(new_appointment)
        self.save_appointments(appointments)

        # Update results CSV
        self._update_patient_record(patient_id, appointment_date)

        logger.info(f"Booked appointment {appt_id} for patient {patient_id} on {appointment_date} at {appointment_time}.")
        return {
            "success": True,
            "appointment_id": appt_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "provider": provider,
            "clinic": clinic,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "risk_category": risk_category,
            "care_gap_addressed": new_appointment["care_gap_addressed"],
            "message": f"Appointment successfully scheduled for {patient_name} on {appointment_date} at {appointment_time} with {provider}."
        }

    def _update_patient_record(self, patient_id: str, appointment_date: str):
        """Updates has_scheduled_appointment and next_scheduled_appointment_date in CSV files."""
        # 1. Update results CSV
        if os.path.exists(self.results_file):
            try:
                df = pd.read_csv(self.results_file)
                mask = df["patient_id"].astype(str).str.upper() == patient_id.strip().upper()
                if mask.any():
                    df.loc[mask, "has_scheduled_appointment"] = 1
                    df.loc[mask, "next_scheduled_appointment_date"] = appointment_date
                    df.to_csv(self.results_file, index=False)
            except Exception as e:
                logger.error(f"Error updating results CSV: {e}")

        # 2. Update demographics CSV if exists
        if os.path.exists(self.demographics_file):
            try:
                df_demo = pd.read_csv(self.demographics_file)
                mask_demo = df_demo["patient_id"].astype(str).str.upper() == patient_id.strip().upper()
                if mask_demo.any():
                    df_demo.loc[mask_demo, "next_scheduled_appointment_date"] = appointment_date
                    df_demo.to_csv(self.demographics_file, index=False)
            except Exception as e:
                logger.error(f"Error updating demographics CSV: {e}")

    def list_appointments(self, patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        appointments = self.load_appointments()
        if patient_id:
            return [
                a for a in appointments
                if a.get("patient_id", "").upper() == patient_id.strip().upper() and a.get("status") == "Confirmed"
            ]
        return appointments

    def cancel_appointment(self, appointment_id: str) -> Dict[str, Any]:
        appointments = self.load_appointments()
        found = False
        target_pid = None
        for appt in appointments:
            if appt.get("appointment_id") == appointment_id:
                appt["status"] = "Cancelled"
                target_pid = appt.get("patient_id")
                found = True
                break

        if not found:
            return {"success": False, "message": f"Appointment '{appointment_id}' not found."}

        self.save_appointments(appointments)
        logger.info(f"Cancelled appointment {appointment_id}.")
        return {"success": True, "message": f"Appointment '{appointment_id}' has been cancelled."}
