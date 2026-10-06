import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.config import SAVED_MODELS_DIR, DISCLAIMER, SPIKE_THRESHOLD_MG_DL
from app.ml.features import FEATURE_NAMES, build_features_from_history
from app.digital_twin.state import (
    PatientProfile,
    Observation,
    RiskFactor,
    PredictionResult,
    ExplainabilityReport,
    WhatIfScenario,
    CounterfactualComparison,
    DigitalTwinState
)

# Friendly descriptions for clinical explanations
FEATURE_DESCRIPTIONS = {
    "current_glucose": ("Current Glucose Level", "Elevated current glucose increases proximity to postprandial spike threshold (>180 mg/dL).", "Current glucose is within normal fasting/pre-meal range."),
    "glucose_slope_hourly": ("Glucose Rate of Change", "Acute upward glucose velocity indicates active carbohydrate absorption or hepatic glucose release.", "Stable or downward glucose trajectory indicates balanced glucose disposal."),
    "glucose_delta_15m": ("15-Min Glucose Velocity", "Fast short-term glucose rise.", "Slow short-term change."),
    "glucose_roll_mean_1h": ("1-Hour Mean Glucose", "Sustained high 1-hour circulating glucose.", "Normal 1-hour average glucose."),
    "meal_carbs_recent": ("Recent Carbohydrate Ingestion", "High-carbohydrate meal stimulates rapid gut glucose influx.", "Low or moderate carbohydrate intake minimizes glycemic excursion."),
    "steps_1h": ("Physical Activity (Past 1 Hour)", "Recent physical activity accelerates GLUT4 translocation and muscular glucose uptake.", "Sedentary behavior reduces insulin-independent muscle glucose disposal."),
    "sleep_duration_hours": ("Sleep Duration", "Sufficient restorative sleep maintains optimal baseline insulin sensitivity.", "Sleep deprivation increases morning cortisol and autonomic insulin resistance."),
    "sleep_quality_score": ("Sleep Quality & Restoration", "High sleep quality supports normal autonomic regulation.", "Fragmented sleep elevates sympathetic tone and blunts insulin response."),
    "hba1c": ("Baseline HbA1c", "Elevated HbA1c reflects chronic hyperglycemia and higher baseline pancreatic beta-cell strain.", "Controlled HbA1c provides stronger metabolic resilience."),
    "bmi": ("Body Mass Index", "Elevated BMI is associated with higher peripheral insulin resistance.", "Normal BMI supports healthy insulin sensitivity."),
    "heart_rate": ("Heart Rate & Sympathetic Tone", "Elevated heart rate reflects sympathetic activation or postprandial cardiovascular work.", "Resting heart rate reflects relaxed autonomic state."),
    "fasting_glucose": ("Fasting Glucose History", "High baseline fasting glucose elevates entire postprandial curve.", "Normal fasting glucose maintains safe baseline buffer."),
    "sleep_debt_glucose_interaction": ("Sleep Debt x Glucose Strain", "Cumulative sleep loss amplifies glycemic volatility.", "Adequate sleep mitigates glucose volatility."),
    "activity_glucose_ratio": ("Activity-to-Glucose Ratio", "High activity relative to glucose level.", "Insufficient activity relative to circulating glucose."),
    "carb_activity_balance": ("Carb-to-Activity Balance", "High carbohydrate load unbuffered by physical activity.", "Carbohydrate load well-buffered by physical activity."),
    "metabolic_strain_index": ("Composite Metabolic Strain", "Combined chronic and acute glycemic load indicates elevated risk.", "Low composite metabolic strain.")
}

class ModelRegistry:
    """Singleton loader for ML models and SHAP explainer."""
    _instance = None

    def __init__(self):
        self.xgb_classifier = joblib.load(SAVED_MODELS_DIR / "main_xgb.joblib")
        self.traj_regressor = joblib.load(SAVED_MODELS_DIR / "trajectory_regressor.joblib")
        self.explainer = joblib.load(SAVED_MODELS_DIR / "shap_explainer.joblib")
        self.background_data = joblib.load(SAVED_MODELS_DIR / "train_background.joblib")
        print("ML Models and SHAP Explainer successfully loaded into memory.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class PatientDigitalTwin:
    """
    Patient-Specific Evolving Digital Twin.
    Maintains:
      - patient_profile (long-term/static EHR characteristics)
      - recent_observations (sliding memory window)
      - current_state (latest physiological observation)
      - current_features (engineered feature representation)
      - prediction (spike probability & 2-hour trajectory forecast)
      - risk_state (LOW / MODERATE / HIGH)
      - explainability (SHAP attribution)
    """

    def __init__(self, patient_profile: PatientProfile, initial_history: Optional[List[Observation]] = None):
        self.patient_profile = patient_profile
        self.history: List[Observation] = initial_history or []
        self.models = ModelRegistry.get_instance()
        
        # If history exists, latest is current state; else synthesize default observation
        if self.history:
            self.current_observation = self.history[-1]
            self.recent_history = self.history[:-1]
        else:
            self.current_observation = Observation(
                patient_id=patient_profile.patient_id,
                timestamp=datetime.now().isoformat(),
                glucose=patient_profile.fasting_glucose,
                heart_rate=72,
                hrv=52.0,
                steps=200,
                is_sleeping=0,
                sleep_duration_hours=patient_profile.typical_sleep_hours,
                sleep_quality_score=80.0,
                meal_event="None",
                meal_carbs_g=0.0
            )
            self.recent_history = []
        
        # Initial state computation
        self._sync_and_predict()

    def ingest_observation(self, obs: Observation) -> DigitalTwinState:
        """
        Step update: New wearable observation arrives ->
        Update patient state -> Recalculate features -> Run prediction -> Update risk.
        """
        self.recent_history.append(self.current_observation)
        # Keep sliding memory window to 96 steps (last 24 hours)
        if len(self.recent_history) > 96:
            self.recent_history = self.recent_history[-96:]
        
        self.current_observation = obs
        return self._sync_and_predict()

    def _sync_and_predict(self) -> DigitalTwinState:
        """Synchronizes EHR + Wearable stream, runs ML inference & SHAP."""
        patient_dict = self.patient_profile.model_dump()
        obs_dict = self.current_observation.model_dump()
        recent_dicts = [o.model_dump() for o in self.recent_history]

        # 1. Feature Engineering
        self.current_features = build_features_from_history(patient_dict, recent_dicts, obs_dict)
        feature_df = pd.DataFrame([self.current_features])[FEATURE_NAMES]

        # 2. Risk Probability Prediction
        risk_proba = float(self.models.xgb_classifier.predict_proba(feature_df)[0, 1])
        risk_pct = int(round(risk_proba * 100))
        
        if risk_pct >= 65:
            risk_level = "HIGH"
        elif risk_pct >= 35:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        # 3. Trajectory Multi-Horizon Forecasting (+30m, +60m, +90m, +120m)
        traj_vals = self.models.traj_regressor.predict(feature_df)[0]
        curr_g = float(self.current_observation.glucose)
        
        # Ensure predicted values stay physically realistic
        traj_dict = {
            "+30m": round(float(np.clip(traj_vals[0], 55.0, 380.0)), 1),
            "+60m": round(float(np.clip(traj_vals[1], 55.0, 380.0)), 1),
            "+90m": round(float(np.clip(traj_vals[2], 55.0, 380.0)), 1),
            "+120m": round(float(np.clip(traj_vals[3], 55.0, 380.0)), 1)
        }

        # Trend derivation
        max_proj = max(traj_dict.values())
        if max_proj >= curr_g + 25.0 or (traj_dict["+60m"] - curr_g) > 15.0:
            expected_trend = "RAPID_INCREASE"
        elif max_proj > curr_g + 8.0:
            expected_trend = "MILD_INCREASE"
        elif min(traj_dict.values()) < curr_g - 15.0:
            expected_trend = "DECREASING"
        else:
            expected_trend = "STEADY"

        self.prediction = PredictionResult(
            spike_risk_probability=round(risk_proba, 4),
            spike_risk_percent=risk_pct,
            risk_level=risk_level,
            prediction_horizon="Next 2 hours",
            expected_trend=expected_trend,
            predicted_trajectory=traj_dict,
            current_glucose=curr_g,
            model_version="XGBoost-v1.0 (Gradient Boosted)",
            generated_at=datetime.now().isoformat()
        )

        # 4. SHAP Explainability
        shap_values = self.models.explainer(feature_df)
        shap_row = shap_values.values[0]
        base_val = float(shap_values.base_values[0]) if hasattr(shap_values, "base_values") else 0.0

        risk_contributors = []
        # Sort by absolute SHAP impact
        sorted_indices = np.argsort(np.abs(shap_row))[::-1]
        
        for idx in sorted_indices[:7]:
            feat = FEATURE_NAMES[idx]
            val = float(self.current_features[feat])
            impact = float(shap_row[idx])
            direction = "INCREASES_RISK" if impact > 0 else "REDUCES_RISK"
            
            label, pos_desc, neg_desc = FEATURE_DESCRIPTIONS.get(
                feat, (feat.replace("_", " ").title(), "Contributes to spike vulnerability.", "Stabilizes glycemic response.")
            )
            explanation = pos_desc if impact > 0 else neg_desc
            
            risk_contributors.append(RiskFactor(
                feature=feat,
                label=label,
                impact_value=round(impact, 4),
                feature_value=round(val, 2),
                direction=direction,
                explanation=explanation
            ))

        summary = (
            f"The 2-hour spike risk is {risk_level} ({risk_pct}%), driven primarily by "
            f"{risk_contributors[0].label.lower()} ({'+' if risk_contributors[0].impact_value > 0 else ''}{risk_contributors[0].impact_value:.2f}) "
            f"and {risk_contributors[1].label.lower()}."
        )

        self.explanation = ExplainabilityReport(
            base_value=round(base_val, 4),
            top_risk_contributors=risk_contributors,
            summary_sentence=summary
        )

        self.last_synced_at = datetime.now().isoformat()
        return self.get_state()

    def get_state(self) -> DigitalTwinState:
        """Returns the full state representation."""
        return DigitalTwinState(
            patient_profile=self.patient_profile,
            current_observation=self.current_observation,
            current_features=self.current_features,
            prediction=self.prediction,
            explanation=self.explanation,
            recent_history=self.recent_history[-24:],  # Last 6 hours for fast frontend display
            status="ACTIVE",
            last_synced_at=self.last_synced_at
        )

    def simulate_counterfactual(self, scenario: WhatIfScenario) -> CounterfactualComparison:
        """
        Runs a What-If counterfactual simulation on a cloned twin state.
        Allows adjusting sleep, steps, carbs, current glucose, etc.
        """
        interventions = []
        sim_obs = self.current_observation.model_copy()
        sim_history = [o.model_copy() for o in self.recent_history]

        if scenario.sleep_duration_hours is not None:
            delta = scenario.sleep_duration_hours - sim_obs.sleep_duration_hours
            sim_obs.sleep_duration_hours = scenario.sleep_duration_hours
            interventions.append(f"Sleep adjusted from {self.current_observation.sleep_duration_hours}h to {scenario.sleep_duration_hours}h ({delta:+.1f}h)")

        if scenario.steps_1h is not None:
            delta = scenario.steps_1h - sim_obs.steps
            sim_obs.steps = scenario.steps_1h
            interventions.append(f"Physical activity past 1h adjusted to {scenario.steps_1h} steps ({delta:+d} steps)")

        if scenario.meal_carbs_g is not None:
            delta = scenario.meal_carbs_g - sim_obs.meal_carbs_g
            sim_obs.meal_carbs_g = scenario.meal_carbs_g
            interventions.append(f"Meal carbohydrate adjusted to {scenario.meal_carbs_g}g ({delta:+.0f}g)")

        if scenario.current_glucose is not None:
            delta = scenario.current_glucose - sim_obs.glucose
            sim_obs.glucose = scenario.current_glucose
            interventions.append(f"Starting glucose adjusted to {scenario.current_glucose} mg/dL ({delta:+.0f} mg/dL)")

        if scenario.heart_rate is not None:
            sim_obs.heart_rate = scenario.heart_rate
            interventions.append(f"Heart rate adjusted to {scenario.heart_rate} bpm")

        # Recalculate features on simulated counterfactual
        patient_dict = self.patient_profile.model_dump()
        sim_obs_dict = sim_obs.model_dump()
        sim_history_dicts = [o.model_dump() for o in sim_history]

        sim_features = build_features_from_history(patient_dict, sim_history_dicts, sim_obs_dict)
        sim_df = pd.DataFrame([sim_features])[FEATURE_NAMES]

        # ML Inference
        sim_risk_proba = float(self.models.xgb_classifier.predict_proba(sim_df)[0, 1])
        sim_risk_pct = int(round(sim_risk_proba * 100))
        sim_risk_level = "HIGH" if sim_risk_pct >= 65 else ("MODERATE" if sim_risk_pct >= 35 else "LOW")

        sim_traj_vals = self.models.traj_regressor.predict(sim_df)[0]
        sim_traj = {
            "+30m": round(float(np.clip(sim_traj_vals[0], 55.0, 380.0)), 1),
            "+60m": round(float(np.clip(sim_traj_vals[1], 55.0, 380.0)), 1),
            "+90m": round(float(np.clip(sim_traj_vals[2], 55.0, 380.0)), 1),
            "+120m": round(float(np.clip(sim_traj_vals[3], 55.0, 380.0)), 1)
        }

        delta_pct = sim_risk_pct - self.prediction.spike_risk_percent

        if delta_pct <= -15:
            interpretation = (
                f"Significant Risk Reduction ({delta_pct:+d}%): The simulated interventions (e.g. enhanced activity / "
                f"carb moderation) effectively stimulate insulin-independent muscular glucose disposal and blunt hepatic glucose influx."
            )
        elif delta_pct >= 15:
            interpretation = (
                f"Risk Escalation ({delta_pct:+d}%): The counterfactual scenario significantly increases postprandial glucose excursion."
            )
        else:
            interpretation = (
                f"Mild Risk Variation ({delta_pct:+d}%): The simulated physiological parameters show marginal shift in acute 2-hour spike likelihood."
            )

        return CounterfactualComparison(
            baseline_risk_percent=self.prediction.spike_risk_percent,
            baseline_risk_level=self.prediction.risk_level,
            simulated_risk_percent=sim_risk_pct,
            simulated_risk_level=sim_risk_level,
            risk_delta_percent=delta_pct,
            baseline_trajectory=self.prediction.predicted_trajectory,
            simulated_trajectory=sim_traj,
            interventions_applied=interventions,
            clinical_interpretation=interpretation,
            disclaimer="Model-based scenario simulation — not a medical recommendation."
        )
