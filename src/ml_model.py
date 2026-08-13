import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score

logger = logging.getLogger(__name__)

class RiskMLModel:
    FEATURE_COLS = [
        "age",
        "days_since_last_visit",
        "has_scheduled_appointment",
        "num_active_medications",
        "num_high_risk_medications",
        "num_abnormal_laboratory_results",
        "num_critical_laboratory_results",
        "num_open_care_gaps",
        "num_overdue_care_gaps",
        "total_care_gap_weight",
        "max_individual_care_gap_weight",
        "num_chronic_conditions"
    ]

    def __init__(self):
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.lr_model = LogisticRegression(max_iter=1000, random_state=42)
        self.dt_model = DecisionTreeClassifier(max_depth=5, random_state=42)

    def train_and_compare(self, df_processed):
        """
        Trains Random Forest, Logistic Regression, and Decision Tree on the features,
        comparing accuracy and feature importance against the rules-based ground truth.
        """
        df = df_processed.copy()

        # Prepare X and y
        X = df[self.FEATURE_COLS].fillna(0)
        y = df["risk_category"]

        if len(df) < 10:
            logger.warning("Dataset too small for reliable ML train/test split. Using full set.")
            X_train, X_test, y_train, y_test = X, X, y, y
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y if len(y.unique()) > 1 else None)

        # 1. Train Random Forest
        self.rf_model.fit(X_train, y_train)
        rf_preds = self.rf_model.predict(X_test)
        rf_acc = accuracy_score(y_test, rf_preds)
        rf_f1 = f1_score(y_test, rf_preds, average="weighted", zero_division=0)

        # 2. Train Logistic Regression
        self.lr_model.fit(X_train, y_train)
        lr_preds = self.lr_model.predict(X_test)
        lr_acc = accuracy_score(y_test, lr_preds)
        lr_f1 = f1_score(y_test, lr_preds, average="weighted", zero_division=0)

        # 3. Train Decision Tree
        self.dt_model.fit(X_train, y_train)
        dt_preds = self.dt_model.predict(X_test)
        dt_acc = accuracy_score(y_test, dt_preds)
        dt_f1 = f1_score(y_test, dt_preds, average="weighted", zero_division=0)

        # Feature Importance (Random Forest)
        importances = pd.DataFrame({
            "feature": self.FEATURE_COLS,
            "importance": self.rf_model.feature_importances_
        }).sort_values(by="importance", ascending=False)

        # Predict ML predictions for all rows in dataframe
        df["ml_predicted_risk_category"] = self.rf_model.predict(X)

        comparison_summary = {
            "random_forest": {"accuracy": round(rf_acc, 4), "f1_score": round(rf_f1, 4)},
            "logistic_regression": {"accuracy": round(lr_acc, 4), "f1_score": round(lr_f1, 4)},
            "decision_tree": {"accuracy": round(dt_acc, 4), "f1_score": round(dt_f1, 4)},
            "feature_importances": importances.to_dict(orient="records"),
            "inputs": self.FEATURE_COLS,
            "output": "risk_category (High Risk, Medium Risk, Lower Risk, No Immediate Action)"
        }

        logger.info(f"ML Model Training Complete. RF Accuracy: {rf_acc:.2f}, LR Accuracy: {lr_acc:.2f}, DT Accuracy: {dt_acc:.2f}")
        return df, comparison_summary
