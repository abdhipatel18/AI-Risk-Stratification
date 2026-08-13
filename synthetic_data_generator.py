import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_data(output_dir="data/input", num_patients=100):
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42)

    # Reference data
    first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Jessica", "William", "Amanda",
                   "James", "Ashley", "Joseph", "Stephanie", "Charles", "Nicole", "Thomas", "Elizabeth", "Daniel", "Heather"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    clinics = ["Metro Health Main", "Northside Community Clinic", "Valley Care Center", "Downtown Medical", "Eastside Health"]
    pcps = ["Dr. Alice Smith", "Dr. Bob Jones", "Dr. Carol Danvers", "Dr. David Banner", "Dr. Elena Rostova"]
    payers = ["Medicare", "Medicaid", "BlueCross BlueShield", "Aetna", "UnitedHealthcare", "Humana"]

    med_list = [
        ("Warfarin", "Anticoagulants", True),
        ("Apixaban", "Anticoagulants", True),
        ("Insulin Glargine", "Insulin", True),
        ("Metformin", "Antidiabetics", False),
        ("Lisinopril", "ACE Inhibitors", False),
        ("Amlodipine", "Calcium Channel Blockers", False),
        ("Atorvastatin", "Statins", False),
        ("Oxycodone", "Opioids", True),
        ("Amiodarone", "Antiarrhythmics", True),
        ("Tacrolimus", "Immunosuppressants", True),
        ("Levothyroxine", "Thyroid", False),
        ("Omeprazole", "Proton Pump Inhibitors", False)
    ]

    lab_list = [
        ("HbA1c", "%", "4.0 - 5.6", lambda: round(random.uniform(5.0, 11.5), 1), lambda v: "Y" if v > 6.5 else ("Critical" if v > 9.0 else "N")),
        ("Blood Pressure Systolic", "mmHg", "90 - 120", lambda: random.randint(110, 180), lambda v: "Critical" if v >= 160 else ("Y" if v >= 130 else "N")),
        ("LDL Cholesterol", "mg/dL", "< 100", lambda: random.randint(70, 210), lambda v: "Y" if v >= 130 else "N"),
        ("eGFR Kidney Function", "mL/min/1.73m2", "> 60", lambda: random.randint(30, 95), lambda v: "Critical" if v < 45 else ("Y" if v < 60 else "N")),
        ("Fasting Blood Glucose", "mg/dL", "70 - 99", lambda: random.randint(80, 200), lambda v: "Y" if v > 125 else "N")
    ]

    care_gaps_master = [
        ("CG001", "HbA1c Control Poor (>9.0%)", "Diabetic patient HbA1c is above recommended target."),
        ("CG002", "Blood Pressure Uncontrolled (>140/90)", "Systolic blood pressure is elevated."),
        ("CG003", "Diabetic Retinopathy Eye Exam", "Annual retinal screening for diabetic patients."),
        ("CG004", "Colorectal Cancer Screening", "Routine colorectal cancer screening."),
        ("CG005", "Breast Cancer Screening (Mammogram)", "Bi-annual mammogram for eligible patients."),
        ("CG006", "Statin Therapy for Cardiovascular Disease", "Statin prescription for ASCVD or diabetes."),
        ("CG007", "Kidney Health Evaluation for Diabetes", "Annual urine albumin-to-creatinine ratio test."),
        ("CG008", "Annual Routine Physical Exam", "Annual wellness visit with Primary Care Provider."),
        ("CG009", "Adult Immunization Status (Flu/Pneumococcal)", "Routine seasonal or adult vaccinations."),
        ("CG010", "Medication Reconciliation Post-Discharge", "Reconcile meds after hospital discharge.")
    ]

    base_date = datetime(2026, 8, 1)

    demographics_rows = []
    medications_rows = []
    labs_rows = []
    care_gaps_rows = []

    for i in range(1, num_patients + 1):
        pid = f"PAT-{i:04d}"
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        dob = base_date - timedelta(days=random.randint(18*365, 85*365))
        age = (base_date - dob).days // 365
        gender = random.choice(["Male", "Female"])
        zip_code = f"{random.randint(10000, 99999)}"
        pcp = random.choice(pcps)
        clinic = random.choice(clinics)
        payer = random.choice(payers)

        last_visit_days_ago = random.randint(10, 400)
        last_visit_date = (base_date - timedelta(days=last_visit_days_ago)).strftime("%Y-%m-%d")

        # 35% of patients have a future appointment
        has_appt = random.random() < 0.35
        if has_appt:
            next_appt_date = (base_date + timedelta(days=random.randint(5, 60))).strftime("%Y-%m-%d")
        else:
            next_appt_date = None

        demographics_rows.append({
            "patient_id": pid,
            "first_name": fn,
            "last_name": ln,
            "date_of_birth": dob.strftime("%Y-%m-%d"),
            "age": age,
            "gender": gender,
            "zip_code": zip_code,
            "primary_care_provider": pcp,
            "clinic": clinic,
            "last_visit_date": last_visit_date,
            "next_scheduled_appointment_date": next_appt_date,
            "insurance_or_payer": payer
        })

        # Generate Medications (1 to 4 meds per patient)
        num_meds = random.randint(1, 4)
        chosen_meds = random.sample(med_list, num_meds)
        for med_name, med_cat, high_risk in chosen_meds:
            rx_days_ago = random.randint(30, 300)
            rx_date = (base_date - timedelta(days=rx_days_ago)).strftime("%Y-%m-%d")
            refill_date = (base_date - timedelta(days=random.randint(-10, 90))).strftime("%Y-%m-%d")
            status = random.choice(["Active", "Active", "Active", "Discontinued"])
            days_supplied = random.choice([30, 90])
            adherence = round(random.uniform(0.6, 1.0), 2) if status == "Active" else None

            medications_rows.append({
                "patient_id": pid,
                "medication_name": med_name,
                "medication_category": med_cat,
                "prescription_date": rx_date,
                "refill_date": refill_date,
                "medication_status": status,
                "days_supplied": days_supplied,
                "medication_adherence_indicator": adherence
            })

        # Generate Labs (1 to 3 labs per patient)
        num_labs = random.randint(1, 3)
        chosen_labs = random.sample(lab_list, num_labs)
        for test_name, units, ref_range, val_fn, abn_fn in chosen_labs:
            test_val = val_fn()
            abn = abn_fn(test_val)
            test_days_ago = random.randint(5, 180)
            t_date = (base_date - timedelta(days=test_days_ago)).strftime("%Y-%m-%d")

            labs_rows.append({
                "patient_id": pid,
                "laboratory_test_name": test_name,
                "result_value": test_val,
                "units": units,
                "reference_range": ref_range,
                "abnormal_result_indicator": abn,
                "test_date": t_date,
                "result_status": "Final"
            })

        # Generate Care Gaps (0 to 3 gaps per patient)
        num_gaps = random.randint(0, 3)
        if num_gaps > 0:
            chosen_gaps = random.sample(care_gaps_master, num_gaps)
            for code, name, desc in chosen_gaps:
                id_days_ago = random.randint(30, 200)
                id_date = (base_date - timedelta(days=id_days_ago)).strftime("%Y-%m-%d")
                due_offset = random.randint(-60, 60)
                due_date = (base_date + timedelta(days=due_offset)).strftime("%Y-%m-%d")

                if due_offset < 0:
                    status = random.choice(["Overdue", "Overdue", "Closed"])
                else:
                    status = random.choice(["Open", "Open", "Closed"])

                last_comp = (base_date - timedelta(days=random.randint(100, 400))).strftime("%Y-%m-%d") if status == "Closed" else None

                care_gaps_rows.append({
                    "patient_id": pid,
                    "care_gap_code": code,
                    "care_gap_name": name,
                    "care_gap_description": desc,
                    "date_care_gap_was_identified": id_date,
                    "care_gap_due_date": due_date,
                    "care_gap_status": status,
                    "last_completed_date": last_comp,
                    "recommended_frequency": "Annual"
                })

    # INTENTIONAL DATA QUALITY ISSUES FOR TESTING DATA VALIDATOR:
    # 1. Blank/Missing Patient ID in Demographics
    demographics_rows.append({
        "patient_id": "", "first_name": "Ghost", "last_name": "User",
        "date_of_birth": "1990-01-01", "age": 36, "gender": "Male",
        "zip_code": "00000", "primary_care_provider": "Dr. Unknown",
        "clinic": "Metro Health Main", "last_visit_date": "2026-01-01",
        "next_scheduled_appointment_date": None, "insurance_or_payer": "Self"
    })
    # 2. Duplicate record
    demographics_rows.append(demographics_rows[0].copy())
    # 3. Unmatched record in Medications (patient_id PAT-9999 doesn't exist)
    medications_rows.append({
        "patient_id": "PAT-9999", "medication_name": "Insulin", "medication_category": "Insulin",
        "prescription_date": "2026-01-01", "refill_date": "2026-02-01", "medication_status": "Active",
        "days_supplied": 30, "medication_adherence_indicator": 0.8
    })

    # Save to CSV files
    df_demo = pd.DataFrame(demographics_rows)
    df_meds = pd.DataFrame(medications_rows)
    df_labs = pd.DataFrame(labs_rows)
    df_gaps = pd.DataFrame(care_gaps_rows)

    df_demo.to_csv(os.path.join(output_dir, "patient_demographics.csv"), index=False)
    df_meds.to_csv(os.path.join(output_dir, "patient_medications.csv"), index=False)
    df_labs.to_csv(os.path.join(output_dir, "patient_labs.csv"), index=False)
    df_gaps.to_csv(os.path.join(output_dir, "patient_care_gaps.csv"), index=False)

    print(f"Successfully generated synthetic patient datasets in '{output_dir}'")
    print(f"Demographics: {len(df_demo)} records")
    print(f"Medications: {len(df_meds)} records")
    print(f"Labs: {len(df_labs)} records")
    print(f"Care Gaps: {len(df_gaps)} records")

if __name__ == "__main__":
    generate_synthetic_data()
