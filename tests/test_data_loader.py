import os
import pytest
import pandas as pd
from src.data_loader import DataLoader
from src.data_validator import DataValidator
from synthetic_data_generator import generate_synthetic_data

@pytest.fixture(scope="module")
def setup_test_data(tmp_path_factory):
    test_dir = tmp_path_factory.mktemp("data_input")
    config_dir = tmp_path_factory.mktemp("config")

    # Write dummy care_gap_weights.csv in config_dir
    weights_csv = config_dir / "care_gap_weights.csv"
    weights_csv.write_text("care_gap_code,care_gap_name,clinical_priority,care_gap_weight,revenue_or_quality_impact,max_recommended_scheduling_timeframe_months\n"
                           "CG001,HbA1c Control Poor (>9.0%),High,25.0,High,1\n")

    generate_synthetic_data(output_dir=str(test_dir), num_patients=10)
    return str(test_dir), str(config_dir)

def test_data_loader_loads_datasets(setup_test_data):
    data_dir, config_dir = setup_test_data
    loader = DataLoader(data_dir=data_dir, config_dir=config_dir)
    datasets = loader.load_all_datasets()

    assert "demographics" in datasets
    assert "medications" in datasets
    assert "labs" in datasets
    assert "care_gaps" in datasets
    assert len(datasets["demographics"]) > 0

def test_data_validator_schema_and_cleaning(setup_test_data):
    data_dir, config_dir = setup_test_data
    loader = DataLoader(data_dir=data_dir, config_dir=config_dir)
    datasets = loader.load_all_datasets()

    validator = DataValidator()
    assert validator.validate_schema(datasets) is True

    df_demo_clean = validator.validate_and_clean_demographics(datasets["demographics"])
    assert "age" in df_demo_clean.columns
    assert len(df_demo_clean) > 0
