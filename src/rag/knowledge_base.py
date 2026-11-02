"""
Knowledge Base for Patient Risk Stratification, Clinical Care Gaps, and Scheduling Protocols.
Provides structured clinical protocols, clinic guidelines, and indexed patient profiles for RAG.
"""

import os
import json
import logging
import pandas as pd
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Standard Clinical Care Gap Protocols
CLINICAL_PROTOCOLS = [
    {
        "id": "protocol_CG001",
        "title": "Clinical Protocol for Care Gap CG001: Uncontrolled HbA1c (>9.0%)",
        "category": "care_gap_protocol",
        "care_gap_code": "CG001",
        "content": (
            "Care Gap CG001 applies to diabetic patients with HbA1c > 9.0%. "
            "Clinical Priority: High. Recommended Outreach: Within 1 Month. "
            "Pre-appointment Instructions: Patient should arrive in a fasting state (water only for 8 hours prior) "
            "if repeat blood glucose/lipid panel is ordered. Advise patient to bring their home glucose monitoring logs "
            "and all current insulin or oral hypoglycemic medications. "
            "Objective: Medication titration, diabetes self-management education, and preventing microvascular complications."
        )
    },
    {
        "id": "protocol_CG002",
        "title": "Clinical Protocol for Care Gap CG002: Uncontrolled Blood Pressure (>140/90 mmHg)",
        "category": "care_gap_protocol",
        "care_gap_code": "CG002",
        "content": (
            "Care Gap CG002 applies to patients with systolic BP >= 140 mmHg or diastolic BP >= 90 mmHg. "
            "Clinical Priority: High. Recommended Outreach: Within 1 Month. "
            "Pre-appointment Instructions: Patient should avoid caffeine, exercise, and smoking 30 minutes before arrival. "
            "Bring 7-day home blood pressure log. If systolic BP exceeds 180 mmHg or diastolic exceeds 120 mmHg with headache, "
            "chest pain, or vision changes, patient must seek immediate emergency medical care."
        )
    },
    {
        "id": "protocol_CG003",
        "title": "Clinical Protocol for Care Gap CG003: Diabetic Retinopathy Eye Exam",
        "category": "care_gap_protocol",
        "care_gap_code": "CG003",
        "content": (
            "Care Gap CG003 requires an annual dilated retinal examination for diabetic patients. "
            "Clinical Priority: Medium. Recommended Outreach: Within 2 Months. "
            "Pre-appointment Instructions: Dilating eye drops will blur near vision and cause light sensitivity for 4-6 hours. "
            "Patients should bring sunglasses and arrange for someone to drive them home after the appointment."
        )
    },
    {
        "id": "protocol_CG004",
        "title": "Clinical Protocol for Care Gap CG004: Colorectal Cancer Screening",
        "category": "care_gap_protocol",
        "care_gap_code": "CG004",
        "content": (
            "Care Gap CG004 applies to adults aged 45-75. "
            "Clinical Priority: Medium. Recommended Outreach: Within 2 Months. "
            "Options: Annual Fecal Immunochemical Test (FIT kit) or screening colonoscopy every 10 years. "
            "Pre-appointment Instructions: Discuss screening preference with the primary care provider. If colonoscopy is chosen, "
            "special bowel preparation instructions and a clear liquid diet will be scheduled."
        )
    },
    {
        "id": "protocol_CG005",
        "title": "Clinical Protocol for Care Gap CG005: Breast Cancer Screening (Mammography)",
        "category": "care_gap_protocol",
        "care_gap_code": "CG005",
        "content": (
            "Care Gap CG005 requires screening mammography every 1-2 years for eligible women. "
            "Clinical Priority: Medium. Recommended Outreach: Within 2 Months. "
            "Pre-appointment Instructions: Do not apply deodorant, antiperspirant, powder, lotion, or perfume under the arms "
            "or on breasts on the day of the exam, as metallic particles can mimic calcifications on the imaging."
        )
    },
    {
        "id": "protocol_CG006",
        "title": "Clinical Protocol for Care Gap CG006: Statin Therapy for Cardiovascular Disease",
        "category": "care_gap_protocol",
        "care_gap_code": "CG006",
        "content": (
            "Care Gap CG006 targets patients with clinical ASCVD or LDL cholesterol >= 190 mg/dL not currently on statin therapy. "
            "Clinical Priority: High. Recommended Outreach: Within 1 Month. "
            "Pre-appointment Instructions: Patient should list any past intolerance, muscle aches, or statin concerns to review "
            "alternative dosing or moderate-intensity regimens with their physician."
        )
    },
    {
        "id": "protocol_CG007",
        "title": "Clinical Protocol for Care Gap CG007: Kidney Health Evaluation for Diabetes (uACR & eGFR)",
        "category": "care_gap_protocol",
        "care_gap_code": "CG007",
        "content": (
            "Care Gap CG007 mandates annual assessment of both estimated Glomerular Filtration Rate (eGFR) and urine "
            "albumin-to-creatinine ratio (uACR) in diabetic patients. "
            "Clinical Priority: Medium. Recommended Outreach: Within 2 Months. "
            "Pre-appointment Instructions: Drink normal amounts of water. A first-morning urine sample is preferred for accuracy."
        )
    },
    {
        "id": "protocol_CG008",
        "title": "Clinical Protocol for Care Gap CG008: Annual Routine Physical Wellness Exam",
        "category": "care_gap_protocol",
        "care_gap_code": "CG008",
        "content": (
            "Care Gap CG008 covers comprehensive preventive health examination and review of systems. "
            "Clinical Priority: Low. Recommended Outreach: Within 3 Months. "
            "Pre-appointment Instructions: Bring updated list of current over-the-counter supplements and specialist records."
        )
    },
    {
        "id": "protocol_CG009",
        "title": "Clinical Protocol for Care Gap CG009: Adult Immunization Status (Flu & Pneumococcal)",
        "category": "care_gap_protocol",
        "care_gap_code": "CG009",
        "content": (
            "Care Gap CG009 ensures adults and high-risk patients receive annual influenza and pneumococcal conjugate vaccines. "
            "Clinical Priority: Low. Recommended Outreach: Within 3 Months. Can be bundled with routine office visits."
        )
    },
    {
        "id": "protocol_CG010",
        "title": "Clinical Protocol for Care Gap CG010: Medication Reconciliation Post-Discharge",
        "category": "care_gap_protocol",
        "care_gap_code": "CG010",
        "content": (
            "Care Gap CG010 applies to patients recently discharged from hospital or emergency care. "
            "Clinical Priority: High. Recommended Outreach: Within 1 Month (ideally within 7-14 days post-discharge). "
            "Pre-appointment Instructions: Bring all prescription bottles, hospital discharge summaries, and new discharge medications "
            "to prevent adverse drug interactions and hospital readmissions."
        )
    }
]

# Risk Stratification and Scheduling Policies
SCHEDULING_POLICIES = [
    {
        "id": "policy_risk_tiers",
        "title": "Hospital Risk Stratification & Scheduling Window Guidelines",
        "category": "scheduling_policy",
        "content": (
            "Our AI Risk Stratification System classifies patients into 4 clinical risk tiers:\n"
            "1. HIGH RISK (Risk Score >= 40.0, or critical laboratory results, or multiple overdue severe care gaps):\n"
            "   - Scheduling Window: SCHEDULE WITHIN ONE MONTH (target: 1-14 days for urgent review).\n"
            "   - Reason: High likelihood of acute clinical deterioration, medication complications, or untreated severe markers.\n"
            "2. MEDIUM RISK (Risk Score 20.0 - 39.9, or open care gaps, or abnormal non-critical labs):\n"
            "   - Scheduling Window: SCHEDULE WITHIN TWO MONTHS (target: 30-60 days).\n"
            "   - Reason: Chronic disease monitoring, preventive screenings, and closing open quality care gaps.\n"
            "3. LOWER RISK (Risk Score < 20.0 with no critical labs or overdue gaps):\n"
            "   - Scheduling Window: SCHEDULE WITHIN THREE MONTHS (target: 60-90 days).\n"
            "   - Reason: Routine annual wellness, preventive maintenance, and immunizations.\n"
            "4. ALREADY SCHEDULED OR NO SCHEDULING NEEDED:\n"
            "   - Patient already has a confirmed future appointment date on file, or has zero care gaps and low risk score."
        )
    },
    {
        "id": "policy_emergency_triage",
        "title": "Clinical Red-Flag Emergency Triage Protocol",
        "category": "emergency_policy",
        "content": (
            "CRITICAL SAFETY PROTOCOL: The chatbot and appointment booking system are for non-emergency scheduling only. "
            "If a patient reports active emergency symptoms—including crushing chest pain, sudden numbness or paralysis on one side, "
            "severe difficulty breathing, coughing up blood, acute confusion, or suicidal ideation—the chatbot MUST immediately advise "
            "the patient to call emergency services (911 / 112 / local emergency) or proceed to the nearest Emergency Department immediately. "
            "Do NOT schedule an outpatient appointment for acute life-threatening symptoms."
        )
    },
    {
        "id": "policy_clinics_hours",
        "title": "Participating Clinics, Locations, and Standard Operating Hours",
        "category": "clinic_info",
        "content": (
            "Operating Hours across all clinics: Monday through Friday from 8:00 AM to 5:00 PM. Closed on weekends and statutory holidays.\n"
            "Participating Clinics:\n"
            "1. Northside Community Clinic - 100 Medical Park Blvd. (Primary Care, Internal Medicine, Phlebotomy Labs).\n"
            "2. Eastside Health - 450 Horizon Way (Family Medicine, Chronic Care Management, Radiology/Mammography).\n"
            "3. Westpark Medical Center - 780 Orchard Ave (Adult Internal Medicine, Endocrinology, Cardiology Consultation).\n"
            "4. Downtown Family Clinic - 220 Main Street (Family Practice, Preventive Wellness, Pediatrics & Adult Care).\n"
            "Standard Appointment Length: 30 minutes for follow-up/routine, 45 minutes for comprehensive high-risk evaluations."
        )
    }
]


class KnowledgeBase:
    """
    Manages clinical guideline documents and dynamically formats patient profiles
    into searchable knowledge chunks for RAG.
    """
    def __init__(self, patient_data_file: str = "data/output/patient_risk_prioritization_results.csv"):
        self.patient_data_file = patient_data_file
        self.documents: List[Dict[str, Any]] = []
        self.patients_df: Optional[pd.DataFrame] = None
        self._load_knowledge()

    def _load_knowledge(self):
        # 1. Add static clinical protocols and policies
        self.documents = []
        for proto in CLINICAL_PROTOCOLS:
            self.documents.append(proto)
        for policy in SCHEDULING_POLICIES:
            self.documents.append(policy)

        # 2. Add dynamic patient documents if data file exists
        if os.path.exists(self.patient_data_file):
            try:
                self.patients_df = pd.read_csv(self.patient_data_file)
                for _, row in self.patients_df.iterrows():
                    doc = self._patient_to_document(row)
                    self.documents.append(doc)
                logger.info(f"Loaded {len(self.documents)} total knowledge documents ({len(self.patients_df)} patients).")
            except Exception as e:
                logger.error(f"Error loading patient data for knowledge base: {e}")
        else:
            logger.warning(f"Patient results file '{self.patient_data_file}' not found. Knowledge base will contain guidelines only.")

    def reload(self):
        """Reloads the knowledge base from disk."""
        self._load_knowledge()

    def _patient_to_document(self, row: pd.Series) -> Dict[str, Any]:
        pid = str(row["patient_id"])
        name = f"{row['first_name']} {row['last_name']}"
        risk_cat = str(row.get("risk_category", "Unknown"))
        score = float(row.get("calculated_risk_score", 0.0))
        window = str(row.get("recommended_scheduling_window", "Schedule Within One Month"))
        pcp = str(row.get("primary_care_provider", "Assigned PCP"))
        clinic = str(row.get("clinic", "Local Clinic"))
        reason = str(row.get("primary_reason_for_prioritization", "Clinical evaluation"))
        appt_status = "Scheduled on " + str(row.get("next_scheduled_appointment_date")) if row.get("has_scheduled_appointment") == 1 else "Not currently scheduled"
        
        open_gaps = int(row.get("num_open_care_gaps", 0))
        overdue_gaps = int(row.get("num_overdue_care_gaps", 0))
        highest_gap = str(row.get("highest_priority_care_gap", "None"))
        critical_labs = int(row.get("num_critical_laboratory_results", 0))
        active_meds = int(row.get("num_active_medications", 0))
        high_risk_meds = int(row.get("num_high_risk_medications", 0))

        content = (
            f"Patient Record for {name} (ID: {pid}):\n"
            f"- Clinical Risk Tier: {risk_cat} (Risk Score: {score:.1f})\n"
            f"- Recommended Scheduling Timeframe: {window}\n"
            f"- Assigned Primary Care Provider: {pcp} at {clinic}\n"
            f"- Current Appointment Status: {appt_status}\n"
            f"- Primary Clinical Concern / Reason for Prioritization: {reason}\n"
            f"- Care Gaps: {open_gaps} open ({overdue_gaps} overdue). Highest priority care gap: {highest_gap}\n"
            f"- Labs & Medications: {critical_labs} critical lab results, {active_meds} active medications ({high_risk_meds} high-risk meds)."
        )

        return {
            "id": f"patient_{pid}",
            "title": f"Patient Record: {name} ({pid})",
            "category": "patient_profile",
            "patient_id": pid,
            "patient_name": name,
            "risk_category": risk_cat,
            "content": content
        }

    def get_patient_profile(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Direct retrieval of patient details by ID."""
        if self.patients_df is None or self.patients_df.empty:
            return None
        match = self.patients_df[self.patients_df["patient_id"].astype(str).str.upper() == patient_id.strip().upper()]
        if match.empty:
            return None
        row = match.iloc[0]
        return row.to_dict()

    def get_all_patients(self) -> List[Dict[str, Any]]:
        """Returns list of all available patients for dropdowns/searches."""
        if self.patients_df is None or self.patients_df.empty:
            return []
        cols = ["patient_id", "first_name", "last_name", "risk_category", "calculated_risk_score",
                "recommended_scheduling_window", "primary_care_provider", "clinic", "has_scheduled_appointment", "next_scheduled_appointment_date"]
        avail_cols = [c for c in cols if c in self.patients_df.columns]
        return self.patients_df[avail_cols].to_dict(orient="records")
