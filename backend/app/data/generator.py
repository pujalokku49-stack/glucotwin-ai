import json
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from app.config import (
    DATA_STORE_DIR,
    SPIKE_THRESHOLD_MG_DL,
    ACUTE_RISE_THRESHOLD,
    STEP_INTERVAL_MINUTES
)

# Fix seeds for 100% reproducible data generation
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

DEMO_PATIENTS = [
    {
        "patient_id": "PT-101",
        "name": "Eleanor Vance",
        "age": 52,
        "sex": "Female",
        "bmi": 24.2,
        "diabetes_duration_years": 2,
        "hba1c": 6.4,
        "fasting_glucose": 108.0,
        "blood_pressure": "118/76",
        "systolic_bp": 118,
        "diastolic_bp": 76,
        "medications": ["Metformin 500mg"],
        "medication_adherence": 0.95,
        "family_history": True,
        "risk_category": "LOW",
        "baseline_activity_steps": 8500,
        "typical_sleep_hours": 7.5,
        "diet_style": "Mediterranean / Low-GI",
        "clinical_notes": "Well-controlled Type 2 Diabetes. Highly active, adheres to balanced diet. Low risk of severe acute spikes."
    },
    {
        "patient_id": "PT-102",
        "name": "Rajesh Kumar",
        "age": 58,
        "sex": "Male",
        "bmi": 28.5,
        "diabetes_duration_years": 6,
        "hba1c": 7.6,
        "fasting_glucose": 134.0,
        "blood_pressure": "134/84",
        "systolic_bp": 134,
        "diastolic_bp": 84,
        "medications": ["Metformin 1000mg", "Sitagliptin 100mg"],
        "medication_adherence": 0.85,
        "family_history": True,
        "risk_category": "MODERATE",
        "baseline_activity_steps": 4200,
        "typical_sleep_hours": 6.2,
        "diet_style": "Moderate-Carb / Irregular Timing",
        "clinical_notes": "Sub-optimally managed T2D. Erratic work schedule, occasional late high-carb dinners causing postprandial spikes."
    },
    {
        "patient_id": "PT-103",
        "name": "Marcus Chen",
        "age": 64,
        "sex": "Male",
        "bmi": 33.1,
        "diabetes_duration_years": 12,
        "hba1c": 9.1,
        "fasting_glucose": 168.0,
        "blood_pressure": "148/92",
        "systolic_bp": 148,
        "diastolic_bp": 92,
        "medications": ["Metformin 1000mg", "Glimepiride 2mg"],
        "medication_adherence": 0.75,
        "family_history": True,
        "risk_category": "HIGH",
        "baseline_activity_steps": 2100,
        "typical_sleep_hours": 5.0,
        "diet_style": "High-Carb / Fast Food",
        "clinical_notes": "Poorly controlled T2D with high insulin resistance and metabolic fatigue. Severe postprandial spike vulnerability."
    }
]

def generate_cohort_patients(n_additional: int = 47) -> List[Dict]:
    """Generate synthetic Synthea-style EHR patient profiles."""
    first_names_m = ["James", "Robert", "John", "David", "William", "Arjun", "Vikram", "Carlos", "Ahmed", "Chen", "Wei"]
    first_names_f = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Priya", "Ananya", "Maria", "Fatima", "Mei", "Sunita"]
    last_names = ["Smith", "Patel", "Johnson", "Williams", "Brown", "Sharma", "Rodriguez", "Khan", "Gupta", "Zhang", "Kim"]

    patients = list(DEMO_PATIENTS)
    for i in range(1, n_additional + 1):
        pid = f"PT-{103 + i:03d}"
        sex = "Male" if random.random() > 0.5 else "Female"
        first = random.choice(first_names_m if sex == "Male" else first_names_f)
        last = random.choice(last_names)
        age = int(np.clip(np.random.normal(57, 10), 36, 78))
        bmi = round(float(np.clip(np.random.normal(29.0, 4.5), 20.5, 42.0)), 1)
        duration = int(np.clip(np.random.exponential(5) + 1, 1, 25))
        
        # HbA1c correlated with BMI and duration
        base_hba1c = 6.0 + (bmi - 22) * 0.12 + duration * 0.08 + np.random.normal(0, 0.5)
        hba1c = round(float(np.clip(base_hba1c, 5.7, 11.5)), 1)
        
        fasting_glucose = round(float(np.clip(70 + hba1c * 10 + np.random.normal(0, 8), 90, 220)), 1)
        systolic = int(np.clip(110 + (bmi - 20) * 1.2 + age * 0.3 + np.random.normal(0, 8), 105, 175))
        diastolic = int(np.clip(70 + (bmi - 20) * 0.6 + np.random.normal(0, 5), 65, 105))
        
        meds = ["Metformin 500mg"]
        if hba1c > 7.5:
            meds.append(random.choice(["Sitagliptin 100mg", "Empagliflozin 10mg", "Glimepiride 1mg"]))
        if hba1c > 8.8:
            meds.append("Basal Insulin Glargine 14u")

        risk = "LOW" if hba1c < 7.0 and bmi < 26 else ("HIGH" if hba1c >= 8.5 or bmi >= 32 else "MODERATE")
        sleep_hours = round(float(np.clip(np.random.normal(6.5, 1.0), 4.5, 8.5)), 1)
        steps = int(np.clip(np.random.normal(4500 if risk == "MODERATE" else (7500 if risk == "LOW" else 2500), 1200), 1000, 12000))

        patients.append({
            "patient_id": pid,
            "name": f"{first} {last}",
            "age": age,
            "sex": sex,
            "bmi": bmi,
            "diabetes_duration_years": duration,
            "hba1c": hba1c,
            "fasting_glucose": fasting_glucose,
            "blood_pressure": f"{systolic}/{diastolic}",
            "systolic_bp": systolic,
            "diastolic_bp": diastolic,
            "medications": meds,
            "medication_adherence": round(random.uniform(0.70, 0.98), 2),
            "family_history": random.random() > 0.3,
            "risk_category": risk,
            "baseline_activity_steps": steps,
            "typical_sleep_hours": sleep_hours,
            "diet_style": "Standard Diet",
            "clinical_notes": f"Synthetic cohort profile. Evaluated T2D duration of {duration} years."
        })
    return patients


def simulate_patient_timeseries(patient: Dict, days: int = 7) -> pd.DataFrame:
    """
    Simulates a physiologically grounded time-series with 15-minute resolution.
    Incorporates:
      - Circadian baseline
      - Meal digestion and glycemic peaks (delayed Gaussian curves)
      - Physical activity (steps, METs) increasing insulin sensitivity & glucose disposal
      - Sleep duration & sleep debt impact on insulin resistance
      - Dynamic heart rate and HRV response
    """
    total_steps = days * 24 * 4  # 4 intervals per hour = 96 per day
    start_time = datetime(2026, 10, 1, 0, 0, 0)
    
    # Patient physiological parameters
    bmi = patient["bmi"]
    hba1c = patient["hba1c"]
    fasting_g = patient["fasting_glucose"]
    insulin_resistance = (bmi / 22.0) * (hba1c / 6.0) * (1.0 + patient["diabetes_duration_years"] * 0.02)
    
    # Medication attenuation factor
    med_strength = len(patient["medications"]) * 0.12
    ir_effective = max(0.8, insulin_resistance * (1.0 - med_strength))

    records = []
    
    current_glucose = fasting_g
    active_meal_glucose = 0.0
    active_exercise_debt = 0.0

    for step in range(total_steps):
        dt = start_time + timedelta(minutes=step * STEP_INTERVAL_MINUTES)
        hour = dt.hour + dt.minute / 60.0
        day_idx = step // 96
        
        # 1. Circadian Baseline (dawn phenomenon around 05:00-08:00)
        circadian_offset = 6.0 * math.sin((hour - 4.0) * math.pi / 12.0)
        if 4.5 <= hour <= 7.5:
            circadian_offset += (ir_effective * 5.0)  # Dawn phenomenon
            
        # 2. Sleep state
        is_sleeping = (hour >= 23.0 or hour < 6.5)
        sleep_quality = 85.0 if is_sleeping else 0.0
        sleep_duration_today = patient["typical_sleep_hours"]
        sleep_debt_penalty = max(0.0, (7.0 - sleep_duration_today) * 5.0)

        # 3. Meals
        # Typical meal windows:
        # Breakfast: 08:00 - 08:30
        # Lunch: 12:30 - 13:00
        # Snack: 16:30 - 17:00
        # Dinner: 19:30 - 20:00
        meal_event = "None"
        meal_carbs_g = 0.0
        
        if dt.minute == 0:
            if dt.hour == 8:
                meal_event = "Breakfast"
                meal_carbs_g = np.random.choice([25, 45, 65], p=[0.3, 0.5, 0.2])
            elif dt.hour == 13:
                meal_event = "Lunch"
                meal_carbs_g = np.random.choice([35, 60, 90], p=[0.25, 0.5, 0.25])
            elif dt.hour == 17 and random.random() > 0.4:
                meal_event = "Snack"
                meal_carbs_g = np.random.choice([15, 30], p=[0.6, 0.4])
            elif dt.hour == 20:
                meal_event = "Dinner"
                meal_carbs_g = np.random.choice([40, 70, 100], p=[0.25, 0.5, 0.25])

        # Patient specific risk tuning for demo profiles
        if patient["patient_id"] == "PT-103" and dt.hour == 13:
            meal_carbs_g = 95.0  # Marcus Chen high carb trigger
        elif patient["patient_id"] == "PT-101" and dt.hour in [8, 13, 20]:
            meal_carbs_g = min(meal_carbs_g, 40.0)  # Eleanor healthy carbs

        if meal_carbs_g > 0:
            # Bolus absorption added to active pool
            active_meal_glucose += meal_carbs_g * (0.85 * ir_effective)

        # 4. Meal Glucose Influx & Clearance
        # Slow absorption decay over 2-3 hours
        meal_absorption_rate = 0.14
        absorbed_delta = active_meal_glucose * meal_absorption_rate
        active_meal_glucose -= absorbed_delta

        # 5. Physical Activity (Steps & Intensity)
        if is_sleeping:
            steps_interval = int(np.random.exponential(5))
            hr = int(np.clip(np.random.normal(58, 4), 48, 70))
            hrv = round(float(np.clip(np.random.normal(65, 8), 40, 95)), 1)
        else:
            base_steps = patient["baseline_activity_steps"] / (16 * 4)  # steps per 15 min
            activity_surge = 0
            # Morning walk or post-lunch walk
            if dt.hour in [9, 14, 18] and random.random() > 0.3:
                activity_surge = np.random.randint(400, 1200)
            steps_interval = int(np.clip(base_steps + activity_surge + np.random.normal(0, 80), 0, 1800))
            
            # HR depends on steps
            hr = int(np.clip(68 + (steps_interval / 40.0) + np.random.normal(0, 4), 58, 155))
            # HRV inversely correlated with stress / exercise
            hrv = round(float(np.clip(55 - (steps_interval / 60.0) + np.random.normal(0, 5), 18, 80)), 1)

        # Activity glucose disposal
        glucose_disposal = (steps_interval / 600.0) * (4.5 / ir_effective)

        # 6. Glucose autoregressive update toward physiological baseline
        target_baseline = fasting_g + circadian_offset + sleep_debt_penalty
        restoring_force = (target_baseline - current_glucose) * 0.08
        noise = np.random.normal(0, 1.8)

        current_glucose = current_glucose + absorbed_delta - glucose_disposal + restoring_force + noise
        current_glucose = max(65.0, min(360.0, current_glucose))

        records.append({
            "patient_id": patient["patient_id"],
            "timestamp": dt.isoformat(),
            "glucose": round(float(current_glucose), 1),
            "heart_rate": hr,
            "hrv": hrv,
            "steps": steps_interval,
            "is_sleeping": int(is_sleeping),
            "sleep_duration_hours": sleep_duration_today,
            "sleep_quality_score": sleep_quality,
            "meal_event": meal_event,
            "meal_carbs_g": float(meal_carbs_g),
        })

    df = pd.DataFrame(records)
    
    # Calculate Ground-Truth Future Trajectory and Spike Label
    # Look ahead 8 steps (120 minutes = 8 * 15m)
    future_g30 = df["glucose"].shift(-2)
    future_g60 = df["glucose"].shift(-4)
    future_g90 = df["glucose"].shift(-6)
    future_g120 = df["glucose"].shift(-8)
    
    # Max future glucose in next 8 steps (inclusive)
    # rolling window forward
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=8)
    max_future_2h = df["glucose"].rolling(window=indexer, min_periods=1).max()
    acute_rise_2h = max_future_2h - df["glucose"]

    df["future_g30"] = future_g30
    df["future_g60"] = future_g60
    df["future_g90"] = future_g90
    df["future_g120"] = future_g120
    df["max_future_2h"] = max_future_2h
    
    # Binary Spike Label: True if peak >= 180 or acute rise >= 50 mg/dL within 2 hours
    df["spike_2h"] = ((max_future_2h >= SPIKE_THRESHOLD_MG_DL) | (acute_rise_2h >= ACUTE_RISE_THRESHOLD)).astype(int)

    return df


def generate_and_save_all_data():
    """Generates full cohort EHR and time series, saving to SQLite and JSON."""
    patients = generate_cohort_patients(n_additional=47)
    
    # Save patient profiles
    patients_file = DATA_STORE_DIR / "patients.json"
    with open(patients_file, "w") as f:
        json.dump(patients, f, indent=2)
    print(f"Generated {len(patients)} patient EHR profiles -> {patients_file}")

    all_dfs = []
    for p in patients:
        df_p = simulate_patient_timeseries(p, days=7)
        all_dfs.append(df_p)
    
    full_df = pd.concat(all_dfs, ignore_index=True)
    csv_file = DATA_STORE_DIR / "timeseries.csv"
    full_df.to_csv(csv_file, index=False)
    print(f"Generated {len(full_df)} wearable time-series steps -> {csv_file}")
    
    # Save demo scenarios separately for fast lookup
    for dp in DEMO_PATIENTS:
        p_sub = full_df[full_df["patient_id"] == dp["patient_id"]]
        p_sub.to_csv(DATA_STORE_DIR / f"timeseries_{dp['patient_id']}.csv", index=False)

    return patients, full_df


if __name__ == "__main__":
    generate_and_save_all_data()
