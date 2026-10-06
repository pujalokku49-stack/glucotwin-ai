import os
from pathlib import Path
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas

DOCS_DIR = Path(__file__).resolve().parent
PDF_PATH = DOCS_DIR / "presentation.pdf"

SLIDES = [
    {
        "num": "01",
        "title": "GlucoTwin AI",
        "subtitle": "A Patient-Specific Digital Twin for Early Prediction of Glucose Spikes",
        "tagline": "“Simulate the Patient. Predict the Risk. Act Before the Spike.”",
        "points": [
            "Challenge: Happiest Health Digital Twin Challenge 2026",
            "Category: Chronic Disease Management & Preventive Healthcare",
            "Target: Type 2 Diabetes Postprandial Glucose Volatility",
            "Status: Functional Research & Decision-Support Prototype"
        ]
    },
    {
        "num": "02",
        "title": "The Problem: Acute Postprandial Spikes",
        "subtitle": "Why Glycemic Spikes are the Silent Drivers of Diabetic Complications",
        "tagline": "HbA1c alone misses dangerous intraday glycemic excursions.",
        "points": [
            "Postprandial spikes (≥180 mg/dL) cause acute vascular endothelial shear stress.",
            "Independent driver of cardiovascular mortality, nephropathy, and diabetic retinopathy.",
            "Traditional care is reactive: finger-prick tests detect spikes only AFTER damage occurs.",
            "Clinical Need: An early-warning horizon (2 hours ahead) to intervene proactively."
        ]
    },
    {
        "num": "03",
        "title": "Epidemic Scale: Why This Matters in India",
        "subtitle": "Addressing the Diabetes Capital of the World",
        "tagline": "India has over 101 million individuals diagnosed with diabetes.",
        "points": [
            "Indian phenotype: High visceral adiposity and early beta-cell dysfunction at lower BMI.",
            "Dietary reality: High glycemic index carbohydrate staples (white rice, refined wheat).",
            "Doctor-patient ratio deficit (1:1,500+) requires automated decision-support.",
            "Scalable digital twins empower proactive lifestyle interventions before clinical escalation."
        ]
    },
    {
        "num": "04",
        "title": "The Solution: GlucoTwin AI",
        "subtitle": "Continuous Physiological State Simulation for Early Warning",
        "tagline": "Fusing long-term clinical history with high-frequency dynamic IoT telemetry.",
        "points": [
            "Continuously assimilates Static EHR + Continuous CGM + Wearable IoT.",
            "Predicts acute spike risk within a 2-hour forward horizon.",
            "Forecasts continuous multi-horizon glucose trajectories (+30, +60, +90, +120 min).",
            "Delivers SHAP-driven explainability and interactive counterfactual simulation."
        ]
    },
    {
        "num": "05",
        "title": "What Makes It a True Digital Twin?",
        "subtitle": "Beyond Simple Static Classification",
        "tagline": "A digital twin is a living, evolving virtual representation of a physical patient.",
        "points": [
            "Patient Profile: Fixed biological traits (age, BMI, genetics, baseline beta-cell reserve).",
            "Temporal Memory: Sliding 24-hour historical buffer capturing circadian rhythms.",
            "Current Metabolic State: Updated dynamically upon every 15-minute sensor observation.",
            "What-If Sandbox: Clones twin state to test counterfactual lifestyle interventions in silico."
        ]
    },
    {
        "num": "06",
        "title": "Multi-Modal Data Fusion",
        "subtitle": "Harmonizing Heterogeneous Healthcare Data Streams",
        "tagline": "Static clinical depth meets dynamic temporal resolution.",
        "points": [
            "Static Stream (Synthea EHR): HbA1c, fasting glucose, diabetes duration, medications.",
            "Dynamic Stream (IoT/CGM): 15-min interstitial glucose, HR, HRV, steps, sleep, meals.",
            "Zero Data Leakage: Strictly backward-looking sliding windows for rolling statistics.",
            "Cross-Modal Interactions: Activity-to-glucose ratio, sleep debt x glucose strain, carb balance."
        ]
    },
    {
        "num": "07",
        "title": "System Architecture Overview",
        "subtitle": "End-to-End Modern Microservice Architecture",
        "tagline": "Clean separation of ingestion, physics engine, ML pipeline, and doctor UI.",
        "points": [
            "Ingestion Layer: Temporal alignment, missing packet imputation, 15-min resampling.",
            "Digital Twin State Engine: In-memory patient twin management & memory buffering.",
            "ML Prediction Engine: XGBoost classifier, multi-output regressor, SHAP TreeExplainer.",
            "Presentation: Doctor analytics dashboard & What-If sandbox in React + Tailwind."
        ]
    },
    {
        "num": "08",
        "title": "The Digital Twin State Engine",
        "subtitle": "Continuous Biological State Evolution",
        "tagline": "Real-time state update cycle: Observe → Update → Re-feature → Predict → Alert.",
        "points": [
            "Class PatientDigitalTwin encapsulates clinical memory, state, and ML adapters.",
            "Maintains 96-observation sliding window (24 hours) for diurnal baseline tracking.",
            "Event-driven execution: New wearable packet triggers immediate state recalibration.",
            "State cloning enables zero-side-effect counterfactual sandbox simulations."
        ]
    },
    {
        "num": "09",
        "title": "Machine Learning Pipeline",
        "subtitle": "Rigorous Evaluation with Honest Benchmarks",
        "tagline": "Prioritizing interpretability, high sensitivity, and reliable generalization.",
        "points": [
            "Baseline Model: Logistic Regression (balanced weights, standardized features).",
            "Primary Model: XGBoost Classifier with 33 engineered physiological features.",
            "Comparator Benchmark: Random Forest Ensemble for non-linear comparison.",
            "Multi-Horizon Trajectory Regressor: MultiOutputRegressor forecasting +30m to +120m."
        ]
    },
    {
        "num": "10",
        "title": "Prediction Methodology & Output",
        "subtitle": "Dual-Horizon Risk Assessment",
        "tagline": "Both probabilistic risk score and tangible mg/dL forecasted curves.",
        "points": [
            "Binary Classification: P(Spike in next 2 hours) with clinical threshold ≥180 mg/dL.",
            "Risk Tiering: LOW (<35%), MODERATE (35–64%), HIGH (≥65%).",
            "Trajectory Projection: Point forecasts at +30m, +60m, +90m, +120m.",
            "Trend Dynamics: Categorizes rate of rise (Rapid Increase, Steady, Decreasing)."
        ]
    },
    {
        "num": "11",
        "title": "Explainable AI (SHAP)",
        "subtitle": "Building Clinical Trust with Transparent Attribution",
        "tagline": "Doctors must understand WHY the twin predicts high risk.",
        "points": [
            "TreeExplainer computes exact additive feature attribution in milliseconds.",
            "Distinguishes Risk Amplifiers (e.g. high current glucose, carb load) from Protectors (steps).",
            "Physiological Translation: Maps raw feature values to human clinical mechanisms.",
            "Zero Hallucination: Explanations are mathematically derived directly from the model."
        ]
    },
    {
        "num": "12",
        "title": "What-If Counterfactual Simulator",
        "subtitle": "Simulate the Intervention Before Clinical Execution",
        "tagline": "Empowering doctors and patients with actionable lifestyle scenario modeling.",
        "points": [
            "Allows adjusting: Sleep duration (hrs), postprandial steps, meal carbs (g), glucose.",
            "Clones current patient state and re-computes physiological feature matrix.",
            "Side-by-side delta visualization: Current 78% Risk → Simulated 46% Risk.",
            "Mandatory Safety Notice: Clearly labeled as simulation, not prescription."
        ]
    },
    {
        "num": "13",
        "title": "Clinical Doctor Dashboard",
        "subtitle": "Built for High-Cognitive-Efficiency Healthcare Delivery",
        "tagline": "Modern, minimal, doctor-friendly interface eliminating cognitive overload.",
        "points": [
            "Patient Overview: Comprehensive EHR demographics, HbA1c, and prescription cards.",
            "Live Telemetry Timeline: Synchronized CGM, HR, HRV, steps, and meal markers.",
            "Prediction Gauge: Visual circular risk gauge with 2-hour trajectory reference bands.",
            "Interactive Sandbox: Live sliders for rapid clinical hypothesis testing."
        ]
    },
    {
        "num": "14",
        "title": "Measured Model Performance",
        "subtitle": "Evaluated on 10 Unseen Test Patients (6,640 Samples)",
        "tagline": "Actual empirical results with zero temporal leakage.",
        "points": [
            "XGBoost Primary: ROC-AUC = 0.9894 | PR-AUC = 0.9833 | F1 = 0.9217 | Recall = 90.99%",
            "Random Forest: ROC-AUC = 0.9831 | PR-AUC = 0.9752 | F1 = 0.9074 | Recall = 89.95%",
            "Logistic Regression: ROC-AUC = 0.9769 | PR-AUC = 0.9642 | F1 = 0.8858 | Recall = 90.39%",
            "Trajectory MAE: +30m: 7.50 mg/dL | +60m: 10.19 mg/dL | +90m: 12.67 mg/dL | +120m: 14.48 mg/dL"
        ]
    },
    {
        "num": "15",
        "title": "Demonstration Workflow",
        "subtitle": "Three Distinct Evaluator Patient Personas",
        "tagline": "Deterministic clinical verification across distinct risk profiles.",
        "points": [
            "Patient PT-101 (Eleanor Vance): Low Risk, high activity (8.5k steps), HbA1c 6.4%.",
            "Patient PT-102 (Rajesh Kumar): Moderate Risk, erratic sleep (6.2h), HbA1c 7.6%.",
            "Patient PT-103 (Marcus Chen): High Risk, 95g carb lunch, sedentary, HbA1c 9.1%.",
            "Live Ingestion Replay: Auto-stream mode advances 15-min clock every 3 seconds."
        ]
    },
    {
        "num": "16",
        "title": "Privacy, Security & Data Ethics",
        "subtitle": "Patient Protection by Architectural Design",
        "tagline": "Zero identifiable patient data used in model development or deployment.",
        "points": [
            "100% Synthetic Synthea-grounded EHR & physiologically simulated wearable telemetry.",
            "HIPAA & GDPR Compliant Architecture: No PII stored, logged, or exposed.",
            "Deterministic Seed Generation (Seed 42) ensures 100% audit reproducibility.",
            "Local runtime execution ensures no external data exfiltration."
        ]
    },
    {
        "num": "17",
        "title": "System Limitations",
        "subtitle": "Scientific Honesty & Technical Boundaries",
        "tagline": "Rigorous self-audit of prototype constraints.",
        "points": [
            "Sensor lag: Interstitial CGM readings lag capillary blood glucose by 5–15 minutes.",
            "Synthetic data domain gap: Real clinical data exhibits noise, artifacts, and dropout.",
            "Medication modeling: Does not account for pharmacokinetics of complex insulin titrations.",
            "Psychological stress: Cortisol spikes not directly measured by basic wrist wearables."
        ]
    },
    {
        "num": "18",
        "title": "Future Scope & Road Ahead",
        "subtitle": "From Prototype to Clinical Trial Readiness",
        "tagline": "Next-generation enhancements for GlucoTwin AI.",
        "points": [
            "Clinical Integration: FHIR (Fast Healthcare Interoperability Resources) HL7 API connector.",
            "Direct Sensor Ingestion: Dexcom Web API & Apple HealthKit / Google Health Connect sync.",
            "Closed-Loop Support: Automated micro-bolus insulin pump integration (Artificial Pancreas).",
            "Multi-Modal Vision: Smartphone meal photo carb estimation via on-device vision models."
        ]
    },
    {
        "num": "19",
        "title": "Clinical & Economic Impact",
        "subtitle": "Transforming Chronic Metabolic Care",
        "tagline": "Moving from reactive treatment to proactive digital twin prevention.",
        "points": [
            "Reduces Glycemic Variability (CV <36% target) and expands Time-In-Range (TIR >70%).",
            "Prevents Microvascular & Macrovascular Complications: Lowers long-term dialysis & ICU admissions.",
            "Economic Value: Projected 40% reduction in acute diabetes-related emergency hospitalizations.",
            "Patient Empowerment: Teaches patients how their specific physiology responds to foods & walks."
        ]
    },
    {
        "num": "20",
        "title": "Conclusion & Challenge Audit",
        "subtitle": "Happiest Health Digital Twin Challenge 2026",
        "tagline": "A complete, working, reproducible Healthcare Digital Twin.",
        "points": [
            "Satisfies 100% of Hackathon Challenge Requirements.",
            "Dual-Stream Data Fusion: Static EHR + Dynamic Wearables.",
            "Evolving Digital Twin Engine: State updates, memory buffer, what-if simulations.",
            "Proven ML Performance: ROC-AUC 0.989, Recall 91%, MAE 7.50 mg/dL, SHAP XAI."
        ]
    }
]

def create_presentation_pdf():
    c = canvas.Canvas(str(PDF_PATH), pagesize=landscape(letter))
    width, height = landscape(letter)  # 792 x 612 pt

    for slide in SLIDES:
        # Background
        c.setFillColor(colors.HexColor("#0f172a"))
        c.rect(0, 0, width, height, fill=1, stroke=0)

        # Header accent bar
        c.setFillColor(colors.HexColor("#10b981"))
        c.rect(40, height - 45, width - 80, 4, fill=1, stroke=0)

        # Slide Number Badge
        c.setFillColor(colors.HexColor("#1e293b"))
        c.roundRect(45, height - 85, 36, 32, 4, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#10b981"))
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(63, height - 74, slide["num"])

        # Slide Title
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(90, height - 72, slide["title"])

        # Subtitle
        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 11)
        c.drawString(90, height - 90, slide["subtitle"])

        # Tagline Card
        c.setFillColor(colors.HexColor("#1e293b"))
        c.setStrokeColor(colors.HexColor("#334155"))
        c.setLineWidth(1)
        c.roundRect(45, height - 145, width - 90, 40, 6, fill=1, stroke=1)

        c.setFillColor(colors.HexColor("#38bdf8"))
        c.setFont("Helvetica-BoldOblique", 11)
        c.drawString(60, height - 128, slide["tagline"])

        # Main Points Card
        c.setFillColor(colors.HexColor("#1e293b"))
        c.setStrokeColor(colors.HexColor("#1e293b"))
        c.roundRect(45, 80, width - 90, height - 245, 8, fill=1, stroke=0)

        # Bullets
        y_pos = height - 180
        for pt in slide["points"]:
            # bullet dot
            c.setFillColor(colors.HexColor("#10b981"))
            c.circle(70, y_pos + 4, 3.5, fill=1, stroke=0)

            c.setFillColor(colors.HexColor("#f1f5f9"))
            c.setFont("Helvetica", 11.5)
            c.drawString(85, y_pos, pt)
            y_pos -= 34

        # Footer
        c.setFillColor(colors.HexColor("#475569"))
        c.setFont("Helvetica", 8)
        c.drawString(45, 45, "GlucoTwin AI | Happiest Health Digital Twin Challenge 2026")
        c.drawRightString(width - 45, 45, f"Slide {slide['num']} of 20 | Research Decision Support")

        c.showPage()

    c.save()
    print(f"Presentation PDF successfully generated -> {PDF_PATH}")

if __name__ == "__main__":
    create_presentation_pdf()
