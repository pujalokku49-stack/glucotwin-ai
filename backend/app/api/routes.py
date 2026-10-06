import json
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional

from app.config import (
    APP_TITLE,
    APP_TAGLINE,
    DISCLAIMER,
    SAVED_MODELS_DIR,
    DATA_STORE_DIR
)
from app.digital_twin.state import (
    PatientProfile,
    DigitalTwinState,
    Observation,
    PredictionResult,
    ExplainabilityReport,
    WhatIfScenario,
    CounterfactualComparison
)
from app.digital_twin.manager import DigitalTwinManager

router = APIRouter()

@router.get("/system-info")
def get_system_info():
    """Returns application metadata, research tagline, and safety disclaimer."""
    return {
        "title": APP_TITLE,
        "tagline": APP_TAGLINE,
        "disclaimer": DISCLAIMER,
        "version": "1.0.0-hackathon-2026",
        "primary_model": "XGBoost Classifier + Multi-Horizon Regressor",
        "explainability": "SHAP (TreeExplainer)",
        "prediction_horizon": "2 Hours (120 Minutes)",
        "status": "OPERATIONAL"
    }

@router.get("/patients", response_model=List[PatientProfile])
def list_patients():
    """List all synthetic patient EHR profiles."""
    manager = DigitalTwinManager.get_instance()
    return manager.list_patients()

@router.get("/patients/{patient_id}", response_model=PatientProfile)
def get_patient(patient_id: str):
    """Get static EHR profile for a single patient."""
    manager = DigitalTwinManager.get_instance()
    profile = manager.get_patient_profile(patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    return profile

@router.get("/patients/{patient_id}/current-state", response_model=DigitalTwinState)
def get_current_state(patient_id: str):
    """
    Get full evolving Digital Twin state for a patient:
    profile + current observation + features + predictions + SHAP explanation + recent memory.
    """
    manager = DigitalTwinManager.get_instance()
    try:
        twin = manager.get_or_create_twin(patient_id)
        return twin.get_state()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/patients/{patient_id}/history", response_model=List[Observation])
def get_patient_history(patient_id: str, limit: int = Query(48, ge=8, le=192)):
    """
    Returns recent historical wearable observations for dashboard charts.
    """
    manager = DigitalTwinManager.get_instance()
    twin = manager.get_or_create_twin(patient_id)
    return (twin.recent_history + [twin.current_observation])[-limit:]

@router.get("/patients/{patient_id}/prediction", response_model=PredictionResult)
def get_patient_prediction(patient_id: str):
    """
    Returns active 2-hour glucose spike risk probability, risk level, and expected trajectory.
    """
    manager = DigitalTwinManager.get_instance()
    twin = manager.get_or_create_twin(patient_id)
    return twin.prediction

@router.get("/patients/{patient_id}/explanation", response_model=ExplainabilityReport)
def get_patient_explanation(patient_id: str):
    """
    Returns SHAP-derived top risk contributors with impact direction and explanations.
    """
    manager = DigitalTwinManager.get_instance()
    twin = manager.get_or_create_twin(patient_id)
    return twin.explanation

@router.post("/patients/{patient_id}/simulate", response_model=CounterfactualComparison)
def simulate_counterfactual(patient_id: str, scenario: WhatIfScenario):
    """
    Runs a What-If counterfactual scenario on the Digital Twin.
    Modifies selected parameters (sleep, steps, meal carbs, current glucose)
    and re-runs the ML pipeline to return a side-by-side risk and trajectory comparison.
    """
    manager = DigitalTwinManager.get_instance()
    twin = manager.get_or_create_twin(patient_id)
    return twin.simulate_counterfactual(scenario)

@router.post("/patients/{patient_id}/step", response_model=DigitalTwinState)
def step_simulation(patient_id: str, steps: int = Query(1, ge=1, le=8)):
    """
    Advances the streaming clock by 1 or more intervals (15 mins each) to simulate
    real-time IoT wearable data ingestion and state evolution.
    """
    manager = DigitalTwinManager.get_instance()
    try:
        return manager.step_forward(patient_id, steps_to_advance=steps)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/patients/{patient_id}/reset", response_model=DigitalTwinState)
def reset_patient_simulation(patient_id: str):
    """Resets patient simulation to its designated demo starting point."""
    manager = DigitalTwinManager.get_instance()
    initial_step = 32 if patient_id == "PT-101" else (54 if patient_id in ["PT-102", "PT-103"] else 40)
    twin = manager.reset_twin(patient_id, initial_step=initial_step)
    return twin.get_state()

@router.get("/model-metrics")
def get_model_metrics():
    """
    Returns actual, measured model evaluation metrics across Logistic Regression baseline,
    XGBoost primary model, Random Forest comparator, and trajectory forecasting.
    """
    metrics_file = SAVED_MODELS_DIR / "evaluation_report.json"
    if not metrics_file.exists():
        raise HTTPException(status_code=404, detail="Model metrics file not found. Run training first.")
    
    with open(metrics_file, "r") as f:
        data = json.load(f)
    return data
