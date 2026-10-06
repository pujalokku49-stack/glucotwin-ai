# GlucoTwin AI — 20+ Minute Demonstration Script & Jury Walkthrough

**Title:** GlucoTwin AI — A Patient-Specific Digital Twin for Early Prediction of Glucose Spikes  
**Tagline:** “Simulate the Patient. Predict the Risk. Act Before the Spike.”  
**Challenge:** Happiest Health Digital Twin Challenge 2026  
**Target Audience:** Clinical Experts, AI/ML Evaluators, Healthcare Jury  

---

## Timing Breakdown Overview

| Timestamp | Phase | Topic / Action | Primary Screen / Visual |
| :--- | :--- | :--- | :--- |
| **00:00 – 02:00** | Introduction | Problem Statement & Clinical Motivation in India | Slide 1–3 / Dashboard Landing |
| **02:00 – 05:00** | Foundations | What Makes It a True Patient-Specific Digital Twin? | Slide 4–5 & Digital Twin Status Card |
| **05:00 – 08:00** | Architecture | Multi-Modal Data Fusion & Engineering Pipeline | Architecture Diagram & Data Layer |
| **08:00 – 12:00** | Machine Learning | Dual-Model Pipeline, Validation, Zero-Leakage & SHAP | Model Evaluation Tab & Metrics Table |
| **12:00 – 17:00** | Live UI Demo | Live Ingestion Replay across 3 Distinct Patient Profiles | Active Dashboard, Replay & CGM Timeline |
| **17:00 – 19:30** | Sandbox | Interactive What-If Counterfactual Simulation | What-If Simulator & Trajectory Overlay |
| **19:30 – 21:30** | Conclusion | Clinical Impact, Limitations, Ethical Auditing & Q&A | Slide 16–20 / Audit Table |

---

## Detailed Minute-by-Minute Script

### Minute 00:00 – 02:00: Problem & Motivation (Why Acute Spikes Matter)
- **Speaker:** "Respected judges, clinical experts, and evaluators. Welcome to the demonstration of **GlucoTwin AI** — a patient-specific digital twin designed for the early prediction and prevention of postprandial glucose spikes in Type 2 Diabetes.
- Every clinician knows the grim reality: HbA1c is a three-month rolling average. Two patients can share the exact same HbA1c of 7.5%, yet one experiences severe daily glycemic excursions while the other maintains steady euglycemia. Acute postprandial spikes above 180 mg/dL inflict acute vascular endothelial shear stress, trigger oxidative damage, and accelerate microvascular and macrovascular complications — from diabetic retinopathy and nephropathy to silent myocardial infarctions.
- In India, with over 101 million individuals living with diabetes and a distinct high-visceral-fat, high-carbohydrate dietary phenotype, reactive finger-prick testing fails. By the time a patient pricks their finger and discovers a glucose of 220 mg/dL, the metabolic injury has already occurred.
- Our core question: **Can we simulate the patient's living metabolic state to predict an acute glucose spike 2 hours before it happens, and give clinicians and patients the power to intervene?**"

### Minute 02:00 – 05:00: The Digital Twin Concept (Beyond Classification)
- **Speaker:** "Let us make an essential distinction: **GlucoTwin AI is not a simple classification model.** A classification script takes a row of numbers and outputs a static label. A **Healthcare Digital Twin** is a living, evolving computational replica of an individual patient's physiology.
- In GlucoTwin AI, each patient possesses:
  1. **Long-Term Patient Profile:** Immutable and historical EHR characteristics — age, BMI, diabetes duration, baseline HbA1c, fasting glucose, and pharmacotherapy regimen.
  2. **Historical Memory Buffer:** A 24-hour sliding physiological window (96 intervals) capturing circadian rhythms, sleep debt, and diurnal insulin resistance.
  3. **Current Metabolic State:** The synchronized physiological state updated every 15 minutes as wearable IoT and CGM observations arrive.
  4. **Multi-Horizon Trajectory Forecast:** Continuous glucose forecasts at +30, +60, +90, and +120 minutes.
  5. **What-If Counterfactual Sandbox:** The ability to clone the twin's state in silico, simulate behavioral interventions — like a 20-minute post-meal walk or reduced carbohydrate intake — and observe the predicted change in risk before the patient takes action."

### Minute 05:00 – 08:00: Multi-Modal Data Fusion & System Architecture
- **Speaker:** "Let us examine the architecture (as illustrated in our exported `architecture_diagram.pdf`).
- Healthcare data arrives across two fundamentally distinct streams:
  - **Static EHR Data:** Generated following Synthea standards, capturing baseline clinical depth without privacy risks.
  - **Dynamic Time-Series Telemetry:** 15-minute resolution packets containing Continuous Interstitial Glucose (CGM), Heart Rate, Heart Rate Variability (RMSSD), Step counts, Sleep duration, and Meal events.
- In our **Data Ingestion & Synchronization Layer**, we apply strict backward-looking rolling windows. There is **zero temporal data leakage**: rolling averages, standard deviations, and glucose velocities (slope per hour) are calculated exclusively from past observations.
- Furthermore, we engineer physiologically grounded cross-modal interaction terms:
  - *Sleep Debt × Glucose Strain:* How sleep deprivation amplifies glucose volatility.
  - *Carbohydrate-to-Activity Balance:* The ratio of ingested carbs to recent muscular glucose disposal.
  - *BMI × Glucose Velocity:* Interaction between adiposity-driven insulin resistance and acute glucose surge rate."

### Minute 08:00 – 12:00: Machine Learning Pipeline, Validation & Explainability
- **Speaker:** "Now let us navigate to the **Model Benchmarks & Metrics** tab on the dashboard.
- We hold ourselves to strict scientific evaluation standards. We report actual measured metrics on 10 independent hold-out test patients (6,640 observations) who were completely unseen during training (26,560 observations):
  - **Logistic Regression Baseline:** Achieves ROC-AUC of 0.9769, F1-Score of 0.8858, and Recall of 90.39%.
  - **Random Forest Benchmark:** Achieves ROC-AUC of 0.9831, F1-Score of 0.9074, and Recall of 89.95%.
  - **Primary XGBoost Classifier:** Outperforms all benchmarks with an **ROC-AUC of 0.9894**, **PR-AUC of 0.9833**, and **F1-Score of 0.9217**.
- *Why is PR-AUC and Recall crucial?* In diabetes management, a False Negative (failing to alert an imminent spike) leaves the patient unbuffered, whereas a False Positive prompts lifestyle caution. With **90.99% Sensitivity**, GlucoTwin AI provides an exceptional clinical safety margin.
- For trajectory forecasting, our Multi-Output Regressor delivers an MAE of **7.50 mg/dL at +30m**, expanding realistically to **14.48 mg/dL at +120m**, well within clinical sensor tolerance.
- For Explainability, we integrate **SHAP TreeExplainer**. Every single prediction decomposes mathematically into directional feature attributions — separating acute risk drivers from protective factors with zero LLM hallucination."

### Minute 12:00 – 17:00: Live Dashboard Demonstration & Cohort Personas
- **Speaker:** "Let us return to the **Patient Twin Dashboard** and examine our 3 distinct demo patients.
- **Patient 1: Eleanor Vance (PT-101) — Low Risk Profile:**
  - Eleanor is 52, BMI 24.2, HbA1c 6.4%, highly active (8,500 daily steps), adhering to a low-GI Mediterranean diet.
  - Look at her Digital Twin Status: Status is **ACTIVE**, Metabolic State is **LOW RISK (0% Spike Probability)**.
  - Her 2-hour projected trajectory stays flat and safely in the euglycemic band (120–135 mg/dL).
  - In the Live Timeline, her CGM curve is completely stable within the 70–140 mg/dL target zone.
- **Patient 2: Rajesh Kumar (PT-102) — Moderate Risk Profile:**
  - Let us switch to Rajesh (PT-102). Rajesh is 58, BMI 28.5, HbA1c 7.6%, with erratic sleep (6.2h) and moderate activity.
  - We advance the streaming replay using the **Step +15m** or **Auto-Stream** button.
  - Notice the dynamic state evolution: As his pre-lunch observation arrives, his risk shifts to Moderate. The SHAP explainability card immediately highlights *Elevated Baseline HbA1c* and *Moderate Carbohydrate Intake* as the active drivers.
- **Patient 3: Marcus Chen (PT-103) — High Risk Scenario:**
  - Now let us select Marcus Chen (PT-103). Marcus is 64, BMI 33.1 (Obese), HbA1c 9.1%, sleeping only 5.0 hours, and has just consumed a 95g carbohydrate meal while remaining sedentary.
  - Notice how the Digital Twin immediately transitions into **HIGH METABOLIC RISK**.
  - Risk Probability reaches **100%**.
  - The 2-Hour Trajectory Forecast projects an alarming surge well past the 180 mg/dL red danger threshold line, climbing towards 250 mg/dL.
  - The SHAP breakdown clearly shows: Top risk contributor is *High Pre-Meal Circulating Glucose (+4.32 SHAP)* and *Recent Carbohydrate Ingestion (+1.01 SHAP)*."

### Minute 17:00 – 19:30: What-If Counterfactual Sandbox Simulation
- **Speaker:** "Now let us enter the most innovative capability of GlucoTwin AI: **The What-If Counterfactual Simulator**.
- Suppose Dr. Sharma is reviewing Marcus Chen's case. Instead of simply warning Marcus, the doctor tests an intervention:
  - In the sandbox controls on the left, we adjust:
    - *Meal Carbohydrate:* Reduced from 95g to 25g (low-glycemic lunch substitution).
    - *Post-Meal Activity:* Increased from 150 to 3,500 steps (a brisk 25-minute postprandial walk).
    - *Sleep Duration:* Adjusted from 5.0h to 7.5h.
  - We click **'Run What-If Simulation'**.
  - The Digital Twin engine clones Marcus's internal state, re-calculates the complete 33-dimensional feature matrix, and re-executes the model pipeline.
  - Look at the side-by-side comparison:
    - Current Patient State vs Simulated State.
    - Notice the projected trajectory comparison chart: The simulated cyan curve dramatically decouples from the baseline gray curve, demonstrating how muscular glucose disposal and carbohydrate moderation attenuate the postprandial peak.
  - And notice our prominent clinical guardrail: *'Model-based scenario simulation — not a medical recommendation.'*"

### Minute 19:30 – 21:30: Ethical Governance, Limitations, Future Roadmap & Conclusion
- **Speaker:** "Before we conclude, let us address regulatory, ethical, and clinical governance:
  1. **Safety & Scope:** GlucoTwin AI is strictly a research and clinical decision-support tool. It does not diagnose diabetes and does not dispense prescriptions.
  2. **Privacy:** Zero real patient identifiable information is used. All EHR profiles follow Synthea schemas, and all time-series data is generated deterministically (Random Seed 42).
  3. **Limitations:** We recognize that interstitial CGM data has an inherent 5–15 minute physiological lag compared to venous blood, and that emotional stress (cortisol surges) is only partially captured via heart-rate variability.
  4. **Future Roadmap:** We plan to integrate HL7 FHIR connectors for EHR interoperability, direct Apple HealthKit / Dexcom API ingestion, and smartphone meal photo vision models.
- In summary: **GlucoTwin AI** bridges the gap between static electronic health records and continuous wearable IoT telemetry. It transforms diabetes management from a reactive firefighting exercise into an anticipatory, preventative science.
- *Simulate the Patient. Predict the Risk. Act Before the Spike.*
- Thank you, and we welcome your questions!"
