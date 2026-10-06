import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

FEATURE_NAMES = [
    # Static Patient EHR Features
    "age",
    "bmi",
    "diabetes_duration_years",
    "hba1c",
    "fasting_glucose",
    "systolic_bp",
    "diastolic_bp",
    "has_insulin",
    "has_metformin",
    "num_medications",
    
    # Dynamic Wearable Features
    "current_glucose",
    "glucose_delta_15m",
    "glucose_delta_30m",
    "glucose_slope_hourly",
    "glucose_roll_mean_1h",
    "glucose_roll_std_1h",
    "glucose_roll_mean_3h",
    "heart_rate",
    "hr_roll_mean_1h",
    "hr_delta_1h",
    "hrv",
    "hrv_roll_mean_1h",
    "steps_1h",
    "steps_3h",
    "sleep_duration_hours",
    "sleep_quality_score",
    "time_since_meal_min",
    "meal_carbs_recent",
    
    # Physiologically Grounded Interaction Features
    "sleep_debt_glucose_interaction",  # (8.0 - sleep) * current_glucose
    "activity_glucose_ratio",          # steps_1h / (current_glucose + 1)
    "carb_activity_balance",           # meal_carbs_recent / (steps_1h + 50)
    "bmi_glucose_slope_interaction",   # bmi * glucose_slope_hourly
    "metabolic_strain_index"           # (hba1c / 6.0) * (current_glucose / 100.0)
]

def extract_static_features_dict(patient: Dict[str, Any]) -> Dict[str, float]:
    """Converts a patient profile dict to static feature numerical dictionary."""
    meds = [m.lower() for m in patient.get("medications", [])]
    return {
        "age": float(patient.get("age", 55)),
        "bmi": float(patient.get("bmi", 28.0)),
        "diabetes_duration_years": float(patient.get("diabetes_duration_years", 5)),
        "hba1c": float(patient.get("hba1c", 7.0)),
        "fasting_glucose": float(patient.get("fasting_glucose", 120.0)),
        "systolic_bp": float(patient.get("systolic_bp", 125)),
        "diastolic_bp": float(patient.get("diastolic_bp", 80)),
        "has_insulin": 1.0 if any("insulin" in m for m in meds) else 0.0,
        "has_metformin": 1.0 if any("metformin" in m for m in meds) else 0.0,
        "num_medications": float(len(meds)),
    }

def build_features_from_history(
    patient: Dict[str, Any],
    recent_history: List[Dict[str, Any]],
    current_obs: Dict[str, Any]
) -> Dict[str, float]:
    """
    Computes real-time feature vector for an online Digital Twin state.
    recent_history is a list of recent observation dicts in chronological order.
    current_obs is the latest observation.
    """
    static_feats = extract_static_features_dict(patient)
    
    curr_g = float(current_obs.get("glucose", 120.0))
    curr_hr = float(current_obs.get("heart_rate", 72.0))
    curr_hrv = float(current_obs.get("hrv", 50.0))
    
    # Fallback to current if history empty
    if not recent_history:
        g_15m_ago = curr_g
        g_30m_ago = curr_g
        g_roll_1h = curr_g
        g_std_1h = 0.0
        g_roll_3h = curr_g
        hr_roll_1h = curr_hr
        hr_delta = 0.0
        hrv_roll_1h = curr_hrv
        steps_1h = int(current_obs.get("steps", 0))
        steps_3h = steps_1h
        time_since_meal = 180.0
        meal_carbs_recent = float(current_obs.get("meal_carbs_g", 0.0))
    else:
        # Combine history with current observation
        all_obs = recent_history + [current_obs]
        
        # 1 step ago = 15m ago
        g_15m_ago = all_obs[-2]["glucose"] if len(all_obs) >= 2 else curr_g
        # 2 steps ago = 30m ago
        g_30m_ago = all_obs[-3]["glucose"] if len(all_obs) >= 3 else g_15m_ago
        
        # 1 hour window = last 4 steps
        last_4 = all_obs[-4:]
        g_vals_1h = [o["glucose"] for o in last_4]
        hr_vals_1h = [o["heart_rate"] for o in last_4]
        hrv_vals_1h = [o["hrv"] for o in last_4]
        steps_1h = sum(o.get("steps", 0) for o in last_4)
        
        # 3 hour window = last 12 steps
        last_12 = all_obs[-12:]
        g_vals_3h = [o["glucose"] for o in last_12]
        steps_3h = sum(o.get("steps", 0) for o in last_12)
        
        g_roll_1h = float(np.mean(g_vals_1h))
        g_std_1h = float(np.std(g_vals_1h)) if len(g_vals_1h) > 1 else 0.0
        g_roll_3h = float(np.mean(g_vals_3h))
        
        hr_roll_1h = float(np.mean(hr_vals_1h))
        hr_delta = curr_hr - hr_roll_1h
        hrv_roll_1h = float(np.mean(hrv_vals_1h))
        
        # Meal search: look back through last 16 steps (4 hours)
        time_since_meal = 240.0
        meal_carbs_recent = float(current_obs.get("meal_carbs_g", 0.0))
        for step_back, o in enumerate(reversed(all_obs)):
            if o.get("meal_carbs_g", 0.0) > 0:
                time_since_meal = step_back * 15.0
                if step_back <= 4:  # within last 60 mins
                    meal_carbs_recent = max(meal_carbs_recent, float(o["meal_carbs_g"]))
                break

    g_delta_15m = curr_g - g_15m_ago
    g_delta_30m = curr_g - g_30m_ago
    glucose_slope_hourly = g_delta_15m * 4.0  # rate per hour based on last 15 min

    sleep_dur = float(current_obs.get("sleep_duration_hours", patient.get("typical_sleep_hours", 7.0)))
    sleep_qual = float(current_obs.get("sleep_quality_score", 75.0))

    # Interactions
    sleep_debt = max(0.0, 8.0 - sleep_dur)
    sleep_debt_glucose = sleep_debt * curr_g
    activity_glucose_ratio = steps_1h / (curr_g + 1.0)
    carb_activity_balance = meal_carbs_recent / (steps_1h + 50.0)
    bmi_glucose_slope = static_feats["bmi"] * glucose_slope_hourly
    metabolic_strain = (static_feats["hba1c"] / 6.0) * (curr_g / 100.0)

    feature_dict = {
        **static_feats,
        "current_glucose": curr_g,
        "glucose_delta_15m": g_delta_15m,
        "glucose_delta_30m": g_delta_30m,
        "glucose_slope_hourly": glucose_slope_hourly,
        "glucose_roll_mean_1h": g_roll_1h,
        "glucose_roll_std_1h": g_std_1h,
        "glucose_roll_mean_3h": g_roll_3h,
        "heart_rate": curr_hr,
        "hr_roll_mean_1h": hr_roll_1h,
        "hr_delta_1h": hr_delta,
        "hrv": curr_hrv,
        "hrv_roll_mean_1h": hrv_roll_1h,
        "steps_1h": float(steps_1h),
        "steps_3h": float(steps_3h),
        "sleep_duration_hours": sleep_dur,
        "sleep_quality_score": sleep_qual,
        "time_since_meal_min": float(time_since_meal),
        "meal_carbs_recent": float(meal_carbs_recent),
        "sleep_debt_glucose_interaction": sleep_debt_glucose,
        "activity_glucose_ratio": activity_glucose_ratio,
        "carb_activity_balance": carb_activity_balance,
        "bmi_glucose_slope_interaction": bmi_glucose_slope,
        "metabolic_strain_index": metabolic_strain,
    }
    return feature_dict


def compute_dataset_features(patients_list: List[Dict], timeseries_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Computes time-synchronized features for the full dataset using patient grouping
    to guarantee NO forward temporal leakage.
    Returns:
      X (features dataframe)
      y (binary spike label)
      y_traj (future trajectory at 30, 60, 90, 120 min)
    """
    patients_dict = {p["patient_id"]: p for p in patients_list}
    all_feature_rows = []
    
    # Process per patient to keep time series contiguous
    for pid, group in timeseries_df.groupby("patient_id", sort=False):
        patient = patients_dict.get(pid, {})
        static_feats = extract_static_features_dict(patient)
        
        group = group.copy().reset_index(drop=True)
        g = group["glucose"]
        hr = group["heart_rate"]
        hrv = group["hrv"]
        steps = group["steps"]
        carbs = group["meal_carbs_g"]
        sleep_dur = group["sleep_duration_hours"]
        sleep_qual = group["sleep_quality_score"]

        # Rolling statistics strictly looking BACKWARD (closed='right')
        g_15m_ago = g.shift(1).bfill()
        g_30m_ago = g.shift(2).bfill()
        g_roll_1h = g.rolling(window=4, min_periods=1).mean()
        g_std_1h = g.rolling(window=4, min_periods=1).std().fillna(0.0)
        g_roll_3h = g.rolling(window=12, min_periods=1).mean()

        hr_roll_1h = hr.rolling(window=4, min_periods=1).mean()
        hr_delta_1h = hr - hr_roll_1h
        hrv_roll_1h = hrv.rolling(window=4, min_periods=1).mean()

        steps_1h = steps.rolling(window=4, min_periods=1).sum()
        steps_3h = steps.rolling(window=12, min_periods=1).sum()

        carbs_recent = carbs.rolling(window=4, min_periods=1).max()
        
        # Calculate time since meal (approximate)
        time_since_meal = []
        last_meal_step = -999
        for i, c in enumerate(carbs):
            if c > 0:
                last_meal_step = i
            time_since_meal.append(min(240.0, (i - last_meal_step) * 15.0 if last_meal_step != -999 else 240.0))
        
        g_delta_15m = g - g_15m_ago
        g_delta_30m = g - g_30m_ago
        glucose_slope = g_delta_15m * 4.0

        sleep_debt = np.maximum(0.0, 8.0 - sleep_dur)
        sleep_debt_g = sleep_debt * g
        act_g_ratio = steps_1h / (g + 1.0)
        carb_act_bal = carbs_recent / (steps_1h + 50.0)
        bmi_g_slope = static_feats["bmi"] * glucose_slope
        strain_idx = (static_feats["hba1c"] / 6.0) * (g / 100.0)

        df_feats = pd.DataFrame({
            "patient_id": pid,
            "timestamp": group["timestamp"],
            **{k: [v] * len(group) for k, v in static_feats.items()},
            "current_glucose": g,
            "glucose_delta_15m": g_delta_15m,
            "glucose_delta_30m": g_delta_30m,
            "glucose_slope_hourly": glucose_slope,
            "glucose_roll_mean_1h": g_roll_1h,
            "glucose_roll_std_1h": g_std_1h,
            "glucose_roll_mean_3h": g_roll_3h,
            "heart_rate": hr,
            "hr_roll_mean_1h": hr_roll_1h,
            "hr_delta_1h": hr_delta_1h,
            "hrv": hrv,
            "hrv_roll_mean_1h": hrv_roll_1h,
            "steps_1h": steps_1h,
            "steps_3h": steps_3h,
            "sleep_duration_hours": sleep_dur,
            "sleep_quality_score": sleep_qual,
            "time_since_meal_min": time_since_meal,
            "meal_carbs_recent": carbs_recent,
            "sleep_debt_glucose_interaction": sleep_debt_g,
            "activity_glucose_ratio": act_g_ratio,
            "carb_activity_balance": carb_act_bal,
            "bmi_glucose_slope_interaction": bmi_g_slope,
            "metabolic_strain_index": strain_idx,
            "spike_2h": group["spike_2h"],
            "future_g30": group["future_g30"],
            "future_g60": group["future_g60"],
            "future_g90": group["future_g90"],
            "future_g120": group["future_g120"]
        })
        
        # Drop the last 8 steps per patient where future labels are NaN
        df_feats = df_feats.dropna(subset=["future_g120", "spike_2h"])
        all_feature_rows.append(df_feats)
        
    full_engineered = pd.concat(all_feature_rows, ignore_index=True)
    X = full_engineered[FEATURE_NAMES]
    y = full_engineered["spike_2h"]
    y_traj = full_engineered[["future_g30", "future_g60", "future_g90", "future_g120"]]
    
    return full_engineered, X, y, y_traj
