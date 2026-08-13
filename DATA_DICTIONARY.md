# Data Dictionary: Patient Risk Stratification & Scheduling System

This document specifies input and output data schemas, data types, required flags, and field definitions used throughout the application.

---

## 1. Input Datasets

### A. Patient Demographics (`data/input/patient_demographics.csv`)
| Column Name | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `patient_id` | String | Yes | Unique alphanumeric patient identifier (e.g., `PAT-0001`). |
| `first_name` | String | Yes | Patient given name. |
| `last_name` | String | Yes | Patient surname. |
| `date_of_birth` | Date (YYYY-MM-DD) | Yes | Patient birth date used to calculate age. |
| `age` | Integer | No | Patient age in years. Calculated automatically if blank. |
| `gender` | String | Yes | Administrative gender (Male/Female/Other). |
| `zip_code` | String | No | 5-digit residential postal code. |
| `primary_care_provider` | String | Yes | Assigned primary care physician (PCP). |
| `clinic` | String | Yes | Primary clinical facility location. |
| `last_visit_date` | Date (YYYY-MM-DD) | Yes | Date of last completed clinical encounter. |
| `next_scheduled_appointment_date` | Date (YYYY-MM-DD) | No | Date of future scheduled appointment, if any. |
| `insurance_or_payer` | String | No | Primary health insurance payer (e.g., Medicare, Medicaid). |

### B. Patient Medications (`data/input/patient_medications.csv`)
| Column Name | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `patient_id` | String | Yes | Foreign key referencing Demographics. |
| `medication_name` | String | Yes | Generic or brand medication name. |
| `medication_category` | String | Yes | Clinical drug class (e.g., Anticoagulants, Statins, Insulin). |
| `prescription_date` | Date (YYYY-MM-DD) | No | Date prescription was ordered. |
| `refill_date` | Date (YYYY-MM-DD) | No | Date of last prescription refill. |
| `medication_status` | String | Yes | `Active` or `Discontinued`. |
| `days_supplied` | Integer | No | Medication supply duration in days. |
| `medication_adherence_indicator` | Float | No | Proportion of days covered (0.0 to 1.0). |

### C. Patient Laboratory Results (`data/input/patient_labs.csv`)
| Column Name | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `patient_id` | String | Yes | Foreign key referencing Demographics. |
| `laboratory_test_name` | String | Yes | Laboratory test name (e.g., HbA1c, Blood Pressure, LDL). |
| `result_value` | String/Float | Yes | Quantitative lab result value. |
| `units` | String | No | Units of measurement (e.g., %, mmHg, mg/dL). |
| `reference_range` | String | No | Normal clinical reference interval. |
| `abnormal_result_indicator` | String | Yes | `Y` (Abnormal), `Critical` (Severely Abnormal), or `N` (Normal). |
| `test_date` | Date (YYYY-MM-DD) | Yes | Date specimen was collected. |
| `result_status` | String | No | `Final`, `Pending`, or `Amended`. |

### D. Patient Care Gaps (`data/input/patient_care_gaps.csv`)
| Column Name | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `patient_id` | String | Yes | Foreign key referencing Demographics. |
| `care_gap_code` | String | Yes | Standardized care gap code (e.g., `CG001`). |
| `care_gap_name` | String | Yes | Descriptive title of care gap. |
| `care_gap_description` | String | No | Clinical objective of the care gap. |
| `date_care_gap_was_identified` | Date (YYYY-MM-DD) | No | Date care gap was opened. |
| `care_gap_due_date` | Date (YYYY-MM-DD) | Yes | Targeted completion deadline. |
| `care_gap_status` | String | Yes | `Open`, `Overdue`, or `Closed`. |
| `last_completed_date` | Date (YYYY-MM-DD) | No | Date gap was previously completed. |
| `recommended_frequency` | String | No | Recurrence interval (e.g., Annual, Bi-annual). |

### E. Care-Gap Weightage (`config/care_gap_weights.csv`)
| Column Name | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `care_gap_code` | String | Yes | Primary key care gap code. |
| `care_gap_name` | String | Yes | Official care gap name. |
| `clinical_priority` | String | Yes | `High`, `Medium`, or `Low`. |
| `care_gap_weight` | Float | Yes | Numeric weight penalty assigned to open gap (e.g., 25.0). |
| `revenue_or_quality_impact` | String | No | HEDIS / Quality measure financial impact. |
| `max_recommended_scheduling_timeframe_months` | Integer | Yes | Maximum recommended outreach delay (1, 2, or 3 months). |

---

## 2. Engineered Output Features & Results (`data/output/patient_risk_prioritization_results.csv`)

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `patient_id` | String | Master patient identifier. |
| `age` | Integer | Calculated patient age in years. |
| `days_since_last_visit` | Integer | Elapsed days between reference date and last clinical visit. |
| `has_scheduled_appointment` | Integer (0/1) | Binary flag indicating if future appointment is confirmed. |
| `num_active_medications` | Integer | Count of active non-discontinued medications. |
| `num_high_risk_medications` | Integer | Count of active high-risk medications (anticoagulants, insulin, opioids, etc.). |
| `num_abnormal_laboratory_results` | Integer | Count of latest abnormal lab tests. |
| `num_critical_laboratory_results` | Integer | Count of latest critically abnormal lab tests. |
| `num_open_care_gaps` | Integer | Count of unfulfilled care gaps. |
| `num_overdue_care_gaps` | Integer | Count of care gaps past their due date. |
| `total_care_gap_weight` | Float | Sum of weights for all open/overdue care gaps. |
| `max_individual_care_gap_weight` | Float | Maximum weight among patient's open care gaps. |
| `highest_priority_care_gap` | String | Name of open care gap with highest clinical weight. |
| `calculated_risk_score` | Float | Configurable overall risk score ($0.0 - 100.0+$). |
| `risk_category` | String | `High Risk`, `Medium Risk`, `Lower Risk`, or `No Immediate Action or Already Scheduled`. |
| `recommended_scheduling_window` | String | `Schedule Within One Month`, `Schedule Within Two Months`, `Schedule Within Three Months`, or `Already Scheduled or No Scheduling Needed`. |
| `primary_reason_for_prioritization` | String | Human-readable factor explanation for assigned tier. |
