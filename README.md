# AI-Based Patient Risk Stratification and Scheduling Prioritization

A Python application that ingests, validates, consolidates, and stratifies multi-source healthcare patient data to recommend actionable scheduling windows and prioritize patient care outreach.

---

## 🏥 Overview

Healthcare teams receive patient data across demographics, active medications, laboratory results, and care gaps. This system consolidates patient data, evaluates clinical risk factors, assigns risk tiers (**High**, **Medium**, **Lower**, **Already Scheduled**), generates factor explanations, and recommends outreach timeframes (**1 Month**, **2 Months**, **3 Months**, **Already Scheduled**).

---

## 📁 Repository Structure

```
patient-risk-project/
├── data/
│   ├── input/                     # Raw input CSV/Excel datasets
│   └── output/                    # Exported CSVs & multi-tab Excel reports
├── config/
│   ├── care_gap_weights.csv       # Reference care gap weights & clinical priorities
│   └── risk_rules.yaml            # Configurable risk scoring parameters
├── src/
│   ├── data_loader.py             # File loading module
│   ├── data_validator.py          # Validation & Data Quality Report generator
│   ├── patient_matcher.py         # Multi-table record integration
│   ├── feature_engineering.py     # Derivation of clinical risk features
│   ├── risk_engine.py             # Configurable rules engine & factor explanation
│   ├── scheduling_engine.py       # Scheduling priority recommendation engine
│   ├── ml_model.py                # Machine learning classifier & evaluation
│   ├── report_generator.py        # Multi-tab openpyxl Excel generator
│   ├── dashboard.py               # Interactive Streamlit web app
│   └── main.py                    # Main pipeline orchestrator CLI
├── tests/                         # Pytest unit testing suite
├── notebooks/                     # Exploratory analysis Jupyter notebook
├── synthetic_data_generator.py    # Synthetic patient data generator
├── DATA_DICTIONARY.md             # Complete data dictionary
├── project_report.md              # Technical project report
├── README.md                      # Setup and execution guide
└── requirements.txt               # Dependencies
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Full Pipeline
Generates synthetic data (if missing), validates records, scores risk, trains ML models, and creates output files:
```bash
python src/main.py
```

To force-regenerate synthetic datasets:
```bash
python src/main.py --regen-data
```

### 3. Launch Interactive Streamlit Dashboard
```bash
streamlit run src/dashboard.py
```
*Or via CLI flag:*
```bash
python src/main.py --dashboard
```

### 4. Run Unit Tests
```bash
pytest tests/
```

### 5. Open Exploratory Notebook
```bash
jupyter notebook notebooks/exploratory_analysis.ipynb
```

---

## 📊 Outputs Generated

1. **Master CSV Output**: [`data/output/patient_risk_prioritization_results.csv`](file:///c:/Users/Abdhi%20Patel/OneDrive/Desktop/abdhi/data/output/patient_risk_prioritization_results.csv)
2. **Multi-Tab Excel Workbook**: [`data/output/patient_risk_prioritization_report.xlsx`](file:///c:/Users/Abdhi%20Patel/OneDrive/Desktop/abdhi/data/output/patient_risk_prioritization_report.xlsx)
   - Executive Summary
   - Patient Priority List
   - One-Month Scheduling List
   - Two-Month Scheduling List
   - Three-Month Scheduling List
   - Care-Gap Summary
   - Data-Quality Report
