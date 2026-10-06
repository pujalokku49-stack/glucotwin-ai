import os
from pathlib import Path
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

DOCS_DIR = Path(__file__).resolve().parent
PDF_PATH = DOCS_DIR / "architecture_diagram.pdf"

def create_architecture_pdf():
    c = canvas.Canvas(str(PDF_PATH), pagesize=landscape(letter))
    width, height = landscape(letter)  # 11 x 8.5 inches = 792 x 612 pt

    # Background
    c.setFillColor(colors.HexColor("#0f172a"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Top Header
    c.setFillColor(colors.HexColor("#10b981"))
    c.rect(40, height - 60, width - 80, 4, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(45, height - 42, "GlucoTwin AI — System Architecture & Data Flow")

    c.setFillColor(colors.HexColor("#94a3b8"))
    c.setFont("Helvetica", 10)
    c.drawString(45, height - 54, "Happiest Health Digital Twin Challenge 2026 | Decision-Support System")

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.HexColor("#34d399"))
    c.drawRightString(width - 45, height - 45, "“Simulate the Patient. Predict the Risk. Act Before the Spike.”")

    # Helper function to draw rounded container boxes
    def draw_box(x, y, w, h, title, subtitle, fill_color, stroke_color, text_color=colors.white):
        c.setFillColor(colors.HexColor(fill_color))
        c.setStrokeColor(colors.HexColor(stroke_color))
        c.setLineWidth(1.5)
        c.roundRect(x, y, w, h, 6, fill=1, stroke=1)

        c.setFillColor(text_color)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 10, y + h - 16, title)

        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 8)
        c.drawString(x + 10, y + h - 28, subtitle)

    # Helper to draw connecting arrows
    def draw_arrow(x1, y1, x2, y2, color="#10b981"):
        c.setStrokeColor(colors.HexColor(color))
        c.setFillColor(colors.HexColor(color))
        c.setLineWidth(1.5)
        c.line(x1, y1, x2, y2)
        # arrowhead
        p = c.beginPath()
        if x2 > x1 and y1 == y2:
            p.moveTo(x2, y2)
            p.lineTo(x2 - 6, y2 + 3)
            p.lineTo(x2 - 6, y2 - 3)
            p.close()
            c.drawPath(p, fill=1, stroke=0)
        elif y2 < y1 and x1 == x2:
            p.moveTo(x2, y2)
            p.lineTo(x2 - 3, y2 + 6)
            p.lineTo(x2 + 3, y2 + 6)
            p.close()
            c.drawPath(p, fill=1, stroke=0)

    # LAYER 1: DATA SOURCES (Left Column)
    draw_box(45, 410, 160, 110, "1. Static EHR Data", "Synthea-Structured Records", "#1e293b", "#334155")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#cbd5e1"))
    c.drawString(55, 470, "• Age, Sex, BMI, BP")
    c.drawString(55, 455, "• T2D Duration & Family History")
    c.drawString(55, 440, "• Baseline HbA1c & Fasting Glucose")
    c.drawString(55, 425, "• Medication Regimen & Adherence")

    draw_box(45, 270, 160, 120, "2. Wearable & IoT Stream", "Physiological Time-Series", "#1e293b", "#334155")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#cbd5e1"))
    c.drawString(55, 350, "• CGM Glucose (15-min packets)")
    c.drawString(55, 335, "• Continuous Heart Rate & HRV")
    c.drawString(55, 320, "• Step Count & METs Activity")
    c.drawString(55, 305, "• Sleep Duration & Architecture")
    c.drawString(55, 290, "• Meal Timing & Carbohydrate Load")

    # LAYER 2: INGESTION & SYNCHRONIZATION
    draw_box(240, 310, 140, 170, "3. Ingestion & Sync", "Temporal Alignment Engine", "#1e293b", "#0284c7")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#cbd5e1"))
    c.drawString(250, 435, "• Missing Packet Imputation")
    c.drawString(250, 420, "• Resampling to 15-min Grid")
    c.drawString(250, 405, "• Grouped Patient Windows")
    c.drawString(250, 390, "• Zero Temporal Leakage Audit")
    c.drawString(250, 375, "• Sliding 24h Memory Buffer")
    c.drawString(250, 345, "[Data Ingestion Layer]")

    draw_arrow(205, 465, 240, 420, "#38bdf8")
    draw_arrow(205, 330, 240, 360, "#38bdf8")

    # LAYER 3: FEATURE ENGINEERING
    draw_box(415, 310, 150, 170, "4. Feature Engineering", "Physiological Fusion Matrix", "#1e293b", "#eab308")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#cbd5e1"))
    c.drawString(425, 445, "• Static EHR Indicators")
    c.drawString(425, 430, "• Glucose Velocity & Hourly Slope")
    c.drawString(425, 415, "• 1h / 3h Rolling Glucose & HR")
    c.drawString(425, 400, "• Time Since Last Meal (min)")
    c.drawString(425, 385, "• Sleep Debt x Glucose Strain")
    c.drawString(425, 370, "• Activity / Glucose Ratio")
    c.drawString(425, 355, "• Carb / Activity Balance")
    c.drawString(425, 340, "• BMI x Glucose Slope Index")

    draw_arrow(380, 395, 415, 395, "#facc15")

    # LAYER 4: DIGITAL TWIN STATE ENGINE
    draw_box(240, 95, 325, 175, "5. Patient-Specific Digital Twin Engine", "Evolving Biological State Representation", "#064e3b", "#10b981")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#e2e8f0"))
    c.drawString(255, 230, "• patient_profile: Long-term EHR baseline characteristics")
    c.drawString(255, 215, "• historical_memory: Multi-day temporal memory & diurnal rhythms")
    c.drawString(255, 200, "• current_state: Live metabolic state (glucose, autonomic tone, sleep)")
    c.drawString(255, 185, "• state_updater: Event-driven recalibration upon each wearable packet")
    c.drawString(255, 170, "• counterfactual_fork: Clones twin state for sandbox what-if intervention")
    c.drawString(255, 140, "Core Digital Twin Logic:")
    c.drawString(255, 125, "New Wearable Observation -> Update State -> Recalculate Features -> Predict")

    draw_arrow(490, 310, 490, 270, "#10b981")

    # LAYER 5: ML PREDICTION ENGINE
    draw_box(600, 290, 150, 190, "6. ML Inference Engine", "Dual-Model Architecture", "#1e293b", "#a855f7")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#cbd5e1"))
    c.drawString(610, 440, "A. Primary Classifier:")
    c.drawString(615, 425, "• XGBoost Classifier")
    c.drawString(615, 410, "• 2-Hr Spike Risk (ROC: 0.989)")
    c.drawString(610, 385, "B. Multi-Horizon Regressor:")
    c.drawString(615, 370, "• Trajectory Forecast")
    c.drawString(615, 355, "• +30m, +60m, +90m, +120m")
    c.drawString(610, 330, "C. Explainable AI:")
    c.drawString(615, 315, "• SHAP TreeExplainer")

    draw_arrow(565, 395, 600, 395, "#c084fc")
    draw_arrow(500, 270, 600, 340, "#c084fc")

    # LAYER 6: PRESENTATION & WHAT-IF (Bottom Right)
    draw_box(600, 95, 150, 160, "7. Clinical Dashboard", "Doctor Decision-Support UI", "#1e293b", "#06b6d4")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#cbd5e1"))
    c.drawString(610, 215, "• Risk Gauge & Trend Alerts")
    c.drawString(610, 200, "• Interactive Trajectory Curve")
    c.drawString(610, 185, "• SHAP Attribution Waterfall")
    c.drawString(610, 170, "• What-If Simulator Sandbox")
    c.drawString(610, 155, "• Live Replay / Clock Step")
    c.drawString(610, 140, "• Historical Actual vs Pred")
    c.drawString(610, 115, "React + Vite + Tailwind")

    draw_arrow(675, 290, 675, 255, "#38bdf8")

    # Footer Disclaimer
    c.setFillColor(colors.HexColor("#475569"))
    c.rect(40, 25, width - 80, 20, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(width / 2, 31, "RESEARCH PROTOTYPE ONLY: Not a certified medical device. Does not provide clinical diagnosis or prescribe treatments.")

    c.save()
    print(f"Architecture PDF successfully generated -> {PDF_PATH}")

if __name__ == "__main__":
    create_architecture_pdf()
