import os
import sys
import argparse
import logging
import pandas as pd

# Add root project dir to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from synthetic_data_generator import generate_synthetic_data
from src.data_loader import DataLoader
from src.data_validator import DataValidator
from src.patient_matcher import PatientMatcher
from src.feature_engineering import FeatureEngineer
from src.risk_engine import RiskEngine
from src.scheduling_engine import SchedulingEngine
from src.ml_model import RiskMLModel
from src.report_generator import ExcelReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_pipeline(data_dir="data/input", config_dir="config", output_dir="data/output", force_regen_data=False):
    print("=" * 70)
    print("  AI-Based Patient Risk Stratification & Scheduling Prioritization")
    print("=" * 70)

    # 1. Check or Generate Synthetic Data
    if force_regen_data or not os.path.exists(os.path.join(data_dir, "patient_demographics.csv")):
        logger.info("Generating synthetic patient input datasets...")
        generate_synthetic_data(output_dir=data_dir, num_patients=100)

    # 2. Data Ingestion
    logger.info("Step 1: Loading raw datasets...")
    loader = DataLoader(data_dir=data_dir, config_dir=config_dir)
    datasets = loader.load_all_datasets()

    # 3. Data Validation & Quality Reporting
    logger.info("Step 2: Validating schema and data quality...")
    validator = DataValidator()
    validator.validate_schema(datasets)

    df_demo_clean = validator.validate_and_clean_demographics(datasets["demographics"])
    valid_pids = set(df_demo_clean["patient_id"])

    df_meds_clean = validator.validate_and_clean_medications(datasets["medications"], valid_pids)
    df_labs_clean = validator.validate_and_clean_labs(datasets["labs"], valid_pids)
    df_gaps_clean = validator.validate_and_clean_care_gaps(datasets["care_gaps"], valid_pids, datasets["care_gap_weights"])
    df_quality_report = validator.get_data_quality_report()

    # 4. Patient Record Integration
    logger.info("Step 3: Consolidating patient records...")
    matcher = PatientMatcher()
    patient_records, weights_lookup = matcher.consolidate_patient_data(
        df_demo_clean, df_meds_clean, df_labs_clean, df_gaps_clean, datasets["care_gap_weights"]
    )

    # 5. Feature Engineering
    logger.info("Step 4: Engineering clinical and operational risk features...")
    feature_engineer = FeatureEngineer(ref_date="2026-08-01")
    df_features = feature_engineer.extract_features(patient_records)

    # 6. Configurable Rules-Based Risk Engine
    logger.info("Step 5: Executing rules-based risk engine & factor explanation...")
    risk_engine = RiskEngine(config_path=os.path.join(config_dir, "risk_rules.yaml"))
    df_risk = risk_engine.calculate_patient_risk(df_features)

    # 7. Scheduling Prioritization Engine
    logger.info("Step 6: Executing scheduling prioritization engine...")
    scheduling_engine = SchedulingEngine()
    df_processed = scheduling_engine.assign_scheduling_priority(df_risk)

    # 8. AI / Machine Learning Model Training & Evaluation
    logger.info("Step 7: Training ML models (Random Forest, Logistic Regression, Decision Tree)...")
    ml_model = RiskMLModel()
    df_processed, ml_summary = ml_model.train_and_compare(df_processed)

    # 9. Save Output Datasets & Excel Report
    logger.info("Step 8: Exporting patient risk results and generating Excel workbook...")
    os.makedirs(output_dir, exist_ok=True)
    results_csv = os.path.join(output_dir, "patient_risk_prioritization_results.csv")
    df_processed.to_csv(results_csv, index=False)

    report_gen = ExcelReportGenerator(output_dir=output_dir)
    excel_path = report_gen.generate_excel_report(df_processed, df_quality_report)

    print("\n" + "=" * 70)
    print("  Pipeline Execution Summary")
    print("=" * 70)
    print(f"Total Patients Analyzed: {len(df_processed)}")
    print(f"High Risk Patients:      {len(df_processed[df_processed['risk_category'] == 'High Risk'])}")
    print(f"Medium Risk Patients:    {len(df_processed[df_processed['risk_category'] == 'Medium Risk'])}")
    print(f"Lower Risk Patients:     {len(df_processed[df_processed['risk_category'] == 'Lower Risk'])}")
    print(f"Schedule 1-Month Group:  {len(df_processed[df_processed['recommended_scheduling_window'] == 'Schedule Within One Month'])}")
    print(f"Data Quality Issues:     {len(df_quality_report)} logged")
    print(f"ML Classifier Accuracy:  Random Forest ({ml_summary['random_forest']['accuracy']:.2%}), Logistic Reg ({ml_summary['logistic_regression']['accuracy']:.2%})")
    print(f"Master Output CSV:       {results_csv}")
    print(f"Multi-Tab Excel Report:  {excel_path}")
    print("=" * 70 + "\n")

    return df_processed, df_quality_report, ml_summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Patient Risk Stratification & Scheduling Engine")
    parser.add_argument("--regen-data", action="store_true", help="Force regenerate synthetic data")
    parser.add_argument("--dashboard", action="store_true", help="Launch Streamlit dashboard after pipeline run")
    args = parser.parse_args()

    df_processed, df_quality_report, ml_summary = run_pipeline(force_regen_data=args.regen_data)

    if args.dashboard:
        import subprocess
        logger.info("Launching Streamlit Dashboard...")
        subprocess.run(["streamlit", "run", "src/dashboard.py"])
