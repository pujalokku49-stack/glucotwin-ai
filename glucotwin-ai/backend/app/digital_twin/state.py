from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import pandas as pd

class PatientProfile(BaseModel):
    patient_id: str
    name: str
    age: int
    sex: str
    bmi: float
    diabetes_duration_years: int
    hba1c: float
    fasting_glucose: float
    blood_pressure: str
    systolic_bp: int
    diastolic_bp: int
    medications: List[str]
    medication_adherence: float
    family_history: bool
    risk_category: str
    baseline_activity_steps: int
    typical_sleep_hours: float
    diet_style: str
    clinical_notes: str

class Observation(BaseModel):
    patient_id: str
    timestamp: str
    glucose: float
    heart_rate: int
    hrv: float
    steps: int
    is_sleeping: int = 0
    sleep_duration_hours: float = 7.0
    sleep_quality_score: float = 80.0
    meal_event: Optional[str] = "None"
    meal_carbs_g: float = 0.0

    @classmethod
    def from_raw_dict(cls, data: Dict[str, Any]) -> "Observation":
        clean = dict(data)
        if pd.isna(clean.get("meal_event")):
            clean["meal_event"] = "None"
        if pd.isna(clean.get("meal_carbs_g")):
            clean["meal_carbs_g"] = 0.0
        return cls(**clean)


class RiskFactor(BaseModel):
    feature: str
    label: str
    impact_value: float  # SHAP value
    feature_value: float
    direction: str       # "INCREASES_RISK" or "REDUCES_RISK"
    explanation: str

class PredictionResult(BaseModel):
    spike_risk_probability: float  # e.g. 0.82
    spike_risk_percent: int        # e.g. 82
    risk_level: str                # "LOW", "MODERATE", "HIGH"
    prediction_horizon: str = "Next 2 hours"
    expected_trend: str            # "RAPID_INCREASE", "STEADY", "DECREASING"
    predicted_trajectory: Dict[str, float]  # {"+30m": 138.0, "+60m": 157.0, ...}
    current_glucose: float
    model_version: str = "XGBoost-v1.0"
    generated_at: str

class ExplainabilityReport(BaseModel):
    base_value: float
    top_risk_contributors: List[RiskFactor]
    summary_sentence: str

class WhatIfScenario(BaseModel):
    sleep_duration_hours: Optional[float] = None
    steps_1h: Optional[int] = None
    meal_carbs_g: Optional[float] = None
    current_glucose: Optional[float] = None
    heart_rate: Optional[int] = None

class CounterfactualComparison(BaseModel):
    baseline_risk_percent: int
    baseline_risk_level: str
    simulated_risk_percent: int
    simulated_risk_level: str
    risk_delta_percent: int
    baseline_trajectory: Dict[str, float]
    simulated_trajectory: Dict[str, float]
    interventions_applied: List[str]
    clinical_interpretation: str
    disclaimer: str

class DigitalTwinState(BaseModel):
    patient_profile: PatientProfile
    current_observation: Observation
    current_features: Dict[str, float]
    prediction: PredictionResult
    explanation: ExplainabilityReport
    recent_history: List[Observation]
    status: str = "ACTIVE"
    last_synced_at: str
