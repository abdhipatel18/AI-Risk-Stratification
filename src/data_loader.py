import os
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, data_dir="data/input", config_dir="config"):
        self.data_dir = data_dir
        self.config_dir = config_dir

    def load_file(self, filepath):
        """Loads a CSV or Excel file based on extension."""
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()
        if ext in [".csv"]:
            df = pd.read_csv(filepath, dtype=str)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath, dtype=str)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        logger.info(f"Loaded {len(df)} records from {filepath}")
        return df

    def load_all_datasets(self, 
                          demographics_file="patient_demographics.csv",
                          medications_file="patient_medications.csv",
                          labs_file="patient_labs.csv",
                          care_gaps_file="patient_care_gaps.csv",
                          care_gap_weights_file="care_gap_weights.csv"):
        """Loads all required healthcare data files."""
        datasets = {}

        demo_path = os.path.join(self.data_dir, demographics_file)
        meds_path = os.path.join(self.data_dir, medications_file)
        labs_path = os.path.join(self.data_dir, labs_file)
        gaps_path = os.path.join(self.data_dir, care_gaps_file)
        weights_path = os.path.join(self.config_dir, care_gap_weights_file)

        datasets["demographics"] = self.load_file(demo_path)
        datasets["medications"] = self.load_file(meds_path)
        datasets["labs"] = self.load_file(labs_path)
        datasets["care_gaps"] = self.load_file(gaps_path)
        datasets["care_gap_weights"] = self.load_file(weights_path)

        return datasets

if __name__ == "__main__":
    loader = DataLoader()
    try:
        datasets = loader.load_all_datasets()
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")
