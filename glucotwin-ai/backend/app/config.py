import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_STORE_DIR = BASE_DIR / "data_store"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"

DATA_STORE_DIR.mkdir(parents=True, exist_ok=True)
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_STORE_DIR / "glucotwin.db"

# Prediction settings
SPIKE_THRESHOLD_MG_DL = 180.0
ACUTE_RISE_THRESHOLD = 50.0
PREDICTION_HORIZON_MINUTES = 120
STEP_INTERVAL_MINUTES = 15

# App details
APP_TITLE = "GlucoTwin AI — A Patient-Specific Digital Twin for Early Prediction of Glucose Spikes"
APP_TAGLINE = "Simulate the Patient. Predict the Risk. Act Before the Spike."
DISCLAIMER = (
    "RESEARCH & DEMONSTRATION ONLY: GlucoTwin AI is a proof-of-concept digital twin decision-support "
    "system designed for hackathon/evaluation purposes. It is NOT a certified medical device, does not "
    "provide clinical diagnosis, and must not replace clinical medical judgment."
)
