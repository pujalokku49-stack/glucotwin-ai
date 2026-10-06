import json
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from app.config import DATA_STORE_DIR
from app.digital_twin.state import PatientProfile, Observation, DigitalTwinState
from app.digital_twin.engine import PatientDigitalTwin

class DigitalTwinManager:
    """
    Manages active PatientDigitalTwin instances in memory.
    Supports stepping through historical time series to simulate live streaming IoT ingestion.
    """
    _instance = None

    def __init__(self):
        self.patients_cache: Dict[str, PatientProfile] = {}
        self.timeseries_cache: Dict[str, pd.DataFrame] = {}
        self.active_twins: Dict[str, PatientDigitalTwin] = {}
        self.playback_pointers: Dict[str, int] = {}
        self._load_data()

    def _load_data(self):
        patients_file = DATA_STORE_DIR / "patients.json"
        if not patients_file.exists():
            raise FileNotFoundError(f"Patients file not found at {patients_file}. Run generator first.")
        
        with open(patients_file, "r") as f:
            raw_patients = json.load(f)
            for p in raw_patients:
                profile = PatientProfile(**p)
                self.patients_cache[profile.patient_id] = profile

        # Pre-cache demo patient time-series
        for pid in ["PT-101", "PT-102", "PT-103"]:
            ts_path = DATA_STORE_DIR / f"timeseries_{pid}.csv"
            if ts_path.exists():
                self.timeseries_cache[pid] = pd.read_csv(ts_path)

        # Initialize demo twins at realistic time index
        # PT-101: Eleanor Vance (Step 32, Morning, stable)
        # PT-102: Rajesh Kumar (Step 54, Post-lunch spike window)
        # PT-103: Marcus Chen (Step 54, High-carb spike vulnerability)
        self.reset_twin("PT-101", initial_step=32)
        self.reset_twin("PT-102", initial_step=54)
        self.reset_twin("PT-103", initial_step=54)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def list_patients(self) -> List[PatientProfile]:
        return list(self.patients_cache.values())

    def get_patient_profile(self, patient_id: str) -> Optional[PatientProfile]:
        return self.patients_cache.get(patient_id)

    def get_or_create_twin(self, patient_id: str) -> PatientDigitalTwin:
        if patient_id not in self.active_twins:
            self.reset_twin(patient_id)
        return self.active_twins[patient_id]

    def reset_twin(self, patient_id: str, initial_step: int = 40) -> PatientDigitalTwin:
        profile = self.patients_cache.get(patient_id)
        if not profile:
            raise ValueError(f"Patient {patient_id} not found.")

        # Load timeseries
        if patient_id in self.timeseries_cache:
            df = self.timeseries_cache[patient_id]
        else:
            ts_path = DATA_STORE_DIR / f"timeseries_{patient_id}.csv"
            if ts_path.exists():
                df = pd.read_csv(ts_path)
            else:
                full_ts = pd.read_csv(DATA_STORE_DIR / "timeseries.csv")
                df = full_ts[full_ts["patient_id"] == patient_id].reset_index(drop=True)
            self.timeseries_cache[patient_id] = df

        max_step = min(initial_step, len(df) - 1)
        history_start = max(0, max_step - 24)
        
        history = [
            Observation.from_raw_dict(df.iloc[i].to_dict())
            for i in range(history_start, max_step)
        ]
        current_obs = Observation.from_raw_dict(df.iloc[max_step].to_dict())

        twin = PatientDigitalTwin(profile, history)
        twin.ingest_observation(current_obs)
        self.active_twins[patient_id] = twin
        self.playback_pointers[patient_id] = max_step
        return twin

    def step_forward(self, patient_id: str, steps_to_advance: int = 1) -> DigitalTwinState:
        """Simulates ingestion of next wearable data packet (clock advance)."""
        twin = self.get_or_create_twin(patient_id)
        df = self.timeseries_cache.get(patient_id)
        if df is None:
            raise ValueError(f"No time-series data for {patient_id}")

        curr_ptr = self.playback_pointers.get(patient_id, 40)
        next_ptr = curr_ptr + steps_to_advance
        if next_ptr >= len(df):
            next_ptr = 24  # Loop back gracefully
        
        next_obs = Observation.from_raw_dict(df.iloc[next_ptr].to_dict())
        self.playback_pointers[patient_id] = next_ptr
        return twin.ingest_observation(next_obs)
