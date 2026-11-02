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
│   └── output/                    # Exported CSVs, multi-tab Excel reports, & scheduled appointments
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
│   ├── dashboard.py               # Streamlit Analytics + RAG Chatbot & Appointment UI
│   ├── main.py                    # Main pipeline orchestrator CLI
│   ├── rag/                       # RAG Chatbot & Appointment Engine
│   │   ├── knowledge_base.py      # Clinical protocols & patient profile knowledge store
│   │   ├── retriever.py           # Hybrid TF-IDF vector + metadata retriever
│   │   ├── appointment_scheduler.py# Clinical risk-tier slot allocator & booking manager
│   │   └── chatbot.py             # Multi-provider LLM chatbot (Gemini, OpenAI, Groq, Local RAG)
│   └── api/                       # REST API Backend
│       └── app.py                 # FastAPI endpoints (/api/chat, /api/slots, /api/appointments)
├── tests/                         # Pytest unit testing suite (10 automated tests)
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

### 3. Launch Interactive Streamlit Dashboard & RAG Chatbot
```bash
streamlit run src/dashboard.py
```
*Or via CLI flag:*
```bash
python src/main.py --dashboard
```

### 4. Launch FastAPI REST API Backend
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```
*Or via CLI flag:*
```bash
python src/main.py --api
```
- Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Interactive ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 5. Run Unit Tests
```bash
pytest tests/
```

---

## 🤖 AI RAG Chatbot & Risk-Based Appointment Scheduling

The system includes **CareNavigator AI**, a Retrieval-Augmented Generation (RAG) assistant designed to guide patients and healthcare coordinators.

### Key Capabilities:
1. **Clinical Risk Explanation**: Explains why a patient is categorized as **High Risk**, **Medium Risk**, or **Lower Risk** based on clinical risk scores, lab results, medications, and overdue care gaps.
2. **Care Gap Guidance**: Details specific clinical protocols for open care gaps (e.g. HbA1c control >9.0%, uncontrolled blood pressure, diabetic retinopathy eye exam, mammograms).
3. **Emergency Triage**: Automatically recognizes acute red-flag symptoms (chest pain, stroke signs, severe dyspnea) and directs patients to emergency care immediately.
4. **Risk-Based Slot Allocation**: Generates valid date and time slots matching the patient's assigned PCP, clinic, and clinical urgency window:
   - **High Risk**: Urgently scheduled within **1 to 14 days** (or within 1 month). Prioritizes morning fasting slots.
   - **Medium Risk**: Scheduled within **15 to 45 days** (within 1-2 months).
   - **Lower Risk**: Routine checkups within **45 to 90 days** (within 2-3 months).
5. **Real-Time Booking & Dataset Synchronization**: Books appointments, creates confirmation records (`APT-XXXX`), and synchronizes back to `data/output/patient_risk_prioritization_results.csv` and `data/output/scheduled_appointments.json`.

### Supported LLM Providers & API Setup:
- **Built-in Local RAG (Default)**: Runs 100% locally and offline using TF-IDF semantic vector similarity. No external API key or credit card needed!
- **Google Gemini**: Set `GEMINI_API_KEY` (Free API key at [Google AI Studio](https://aistudio.google.com/app/apikey)).
- **OpenAI**: Set `OPENAI_API_KEY` ([OpenAI API Keys](https://platform.openai.com/api-keys)).
- **Groq (Llama-3)**: Set `GROQ_API_KEY` (Free ultra-fast inference at [Groq Console](https://console.groq.com/keys)).

---

## 📊 Outputs Generated

1. **Master CSV Output**: [`data/output/patient_risk_prioritization_results.csv`](file:///c:/Users/Abdhi%20Patel/OneDrive/Desktop/abdhi/data/output/patient_risk_prioritization_results.csv)
2. **Multi-Tab Excel Workbook**: [`data/output/patient_risk_prioritization_report.xlsx`](file:///c:/Users/Abdhi%20Patel/OneDrive/Desktop/abdhi/data/output/patient_risk_prioritization_report.xlsx)
3. **Live Scheduled Appointments**: [`data/output/scheduled_appointments.json`](file:///c:/Users/Abdhi%20Patel/OneDrive/Desktop/abdhi/data/output/scheduled_appointments.json)
