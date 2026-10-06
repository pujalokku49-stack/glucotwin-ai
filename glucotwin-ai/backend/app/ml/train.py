import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    mean_absolute_error,
    root_mean_squared_error
)
from xgboost import XGBClassifier, XGBRegressor
import shap

from app.config import DATA_STORE_DIR, SAVED_MODELS_DIR
from app.ml.features import (
    FEATURE_NAMES,
    compute_dataset_features
)

def train_and_evaluate_models():
    print("Loading raw EHR and time-series datasets...")
    with open(DATA_STORE_DIR / "patients.json", "r") as f:
        patients = json.load(f)
    timeseries_df = pd.read_csv(DATA_STORE_DIR / "timeseries.csv")

    print("Computing engineered feature matrix...")
    full_df, X, y, y_traj = compute_dataset_features(patients, timeseries_df)
    
    # Patient-Aware Split:
    # Reserve 10 patients entirely for test (including PT-101, PT-102, PT-103 for deterministic demo consistency)
    test_patient_ids = ["PT-101", "PT-102", "PT-103", "PT-104", "PT-105", "PT-106", "PT-107", "PT-108", "PT-109", "PT-110"]
    train_mask = ~full_df["patient_id"].isin(test_patient_ids)
    test_mask = full_df["patient_id"].isin(test_patient_ids)

    X_train = X[train_mask]
    y_train = y[train_mask]
    y_traj_train = y_traj[train_mask]

    X_test = X[test_mask]
    y_test = y[test_mask]
    y_traj_test = y_traj[test_mask]

    print(f"Dataset split: Train shape = {X_train.shape}, Test shape = {X_test.shape}")
    print(f"Train spike prevalence: {y_train.mean():.3f}, Test spike prevalence: {y_test.mean():.3f}")

    # Standard Scaler for Linear Baseline
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Baseline: Logistic Regression
    print("\n--- Training Baseline: Logistic Regression ---")
    lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    lr.fit(X_train_scaled, y_train)
    y_pred_lr = lr.predict(X_test_scaled)
    y_proba_lr = lr.predict_proba(X_test_scaled)[:, 1]

    cm_lr = confusion_matrix(y_test, y_pred_lr).tolist()
    metrics_lr = {
        "model_name": "Logistic Regression (Baseline)",
        "roc_auc": round(float(roc_auc_score(y_test, y_proba_lr)), 4),
        "pr_auc": round(float(average_precision_score(y_test, y_proba_lr)), 4),
        "f1": round(float(f1_score(y_test, y_pred_lr)), 4),
        "precision": round(float(precision_score(y_test, y_pred_lr)), 4),
        "recall": round(float(recall_score(y_test, y_pred_lr)), 4),
        "confusion_matrix": cm_lr,
        "description": "Linear baseline with balanced class weights on standardized features."
    }
    print(f"LR Results: ROC-AUC={metrics_lr['roc_auc']}, PR-AUC={metrics_lr['pr_auc']}, F1={metrics_lr['f1']}, Recall={metrics_lr['recall']}")

    # 2. Main Model: XGBoost Classifier
    print("\n--- Training Main Model: XGBoost Classifier ---")
    scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)
    xgb = XGBClassifier(
        n_estimators=160,
        max_depth=5,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric="logloss"
    )
    xgb.fit(X_train, y_train)
    y_pred_xgb = xgb.predict(X_test)
    y_proba_xgb = xgb.predict_proba(X_test)[:, 1]

    cm_xgb = confusion_matrix(y_test, y_pred_xgb).tolist()
    metrics_xgb = {
        "model_name": "XGBoost Classifier (Primary)",
        "roc_auc": round(float(roc_auc_score(y_test, y_proba_xgb)), 4),
        "pr_auc": round(float(average_precision_score(y_test, y_proba_xgb)), 4),
        "f1": round(float(f1_score(y_test, y_pred_xgb)), 4),
        "precision": round(float(precision_score(y_test, y_pred_xgb)), 4),
        "recall": round(float(recall_score(y_test, y_pred_xgb)), 4),
        "confusion_matrix": cm_xgb,
        "description": "Gradient-boosted decision trees with clinical interaction terms."
    }
    print(f"XGB Results: ROC-AUC={metrics_xgb['roc_auc']}, PR-AUC={metrics_xgb['pr_auc']}, F1={metrics_xgb['f1']}, Recall={metrics_xgb['recall']}")

    # 3. Comparator Model: Random Forest Classifier
    print("\n--- Training Comparator: Random Forest Classifier ---")
    rf = RandomForestClassifier(n_estimators=120, max_depth=7, class_weight="balanced", random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    y_proba_rf = rf.predict_proba(X_test)[:, 1]

    cm_rf = confusion_matrix(y_test, y_pred_rf).tolist()
    metrics_rf = {
        "model_name": "Random Forest",
        "roc_auc": round(float(roc_auc_score(y_test, y_proba_rf)), 4),
        "pr_auc": round(float(average_precision_score(y_test, y_proba_rf)), 4),
        "f1": round(float(f1_score(y_test, y_pred_rf)), 4),
        "precision": round(float(precision_score(y_test, y_pred_rf)), 4),
        "recall": round(float(recall_score(y_test, y_pred_rf)), 4),
        "confusion_matrix": cm_rf,
        "description": "Ensemble bagging model serving as non-linear benchmark."
    }
    print(f"RF Results: ROC-AUC={metrics_rf['roc_auc']}, PR-AUC={metrics_rf['pr_auc']}, F1={metrics_rf['f1']}, Recall={metrics_rf['recall']}")

    # 4. Trajectory Forecasting: Multi-Output XGBoost Regressor
    print("\n--- Training Multi-Horizon Trajectory Regressor ---")
    traj_regressor = MultiOutputRegressor(
        XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.08,
            random_state=42
        )
    )
    traj_regressor.fit(X_train, y_traj_train)
    y_traj_pred = traj_regressor.predict(X_test)

    horizons = ["+30m", "+60m", "+90m", "+120m"]
    traj_metrics = {}
    for i, h in enumerate(horizons):
        mae = float(mean_absolute_error(y_traj_test.iloc[:, i], y_traj_pred[:, i]))
        rmse = float(root_mean_squared_error(y_traj_test.iloc[:, i], y_traj_pred[:, i]))
        traj_metrics[h] = {"mae": round(mae, 2), "rmse": round(rmse, 2)}
        print(f"Trajectory {h}: MAE = {mae:.2f} mg/dL, RMSE = {rmse:.2f} mg/dL")

    # 5. SHAP TreeExplainer
    print("\n--- Initializing SHAP TreeExplainer on XGBoost Model ---")
    explainer = shap.TreeExplainer(xgb)

    # Save models and artifacts
    joblib.dump(scaler, SAVED_MODELS_DIR / "scaler.joblib")
    joblib.dump(lr, SAVED_MODELS_DIR / "baseline_lr.joblib")
    joblib.dump(xgb, SAVED_MODELS_DIR / "main_xgb.joblib")
    joblib.dump(rf, SAVED_MODELS_DIR / "comparator_rf.joblib")
    joblib.dump(traj_regressor, SAVED_MODELS_DIR / "trajectory_regressor.joblib")
    joblib.dump(explainer, SAVED_MODELS_DIR / "shap_explainer.joblib")
    
    # Save test sample background for SHAP reference
    joblib.dump(X_train.sample(min(200, len(X_train)), random_state=42), SAVED_MODELS_DIR / "train_background.joblib")

    # Save evaluation metrics JSON
    evaluation_report = {
        "evaluation_date": pd.Timestamp.now().isoformat(),
        "total_patients": len(patients),
        "test_patient_ids": test_patient_ids,
        "n_train_samples": int(len(X_train)),
        "n_test_samples": int(len(X_test)),
        "models": {
            "logistic_regression": metrics_lr,
            "xgboost": metrics_xgb,
            "random_forest": metrics_rf
        },
        "trajectory_metrics": traj_metrics,
        "feature_importances": {
            feat: round(float(imp), 4)
            for feat, imp in zip(FEATURE_NAMES, xgb.feature_importances_)
        }
    }
    with open(SAVED_MODELS_DIR / "evaluation_report.json", "w") as f:
        json.dump(evaluation_report, f, indent=2)

    print(f"\nAll models, SHAP explainer, and evaluation report saved successfully to {SAVED_MODELS_DIR}")
    return evaluation_report

if __name__ == "__main__":
    train_and_evaluate_models()
