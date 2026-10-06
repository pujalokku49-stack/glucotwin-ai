import React, { useState, useEffect, useRef } from 'react';
import {
  Activity,
  Cpu,
  BarChart3,
  Sliders,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  FileText
} from 'lucide-react';

import {
  fetchPatients,
  fetchCurrentState,
  fetchPatientHistory,
  simulateWhatIf,
  stepSimulation,
  resetSimulation
} from './services/api';

import SafetyDisclaimer from './components/SafetyDisclaimer';
import PatientOverview from './components/PatientOverview';
import DigitalTwinStatus from './components/DigitalTwinStatus';
import PredictionPanel from './components/PredictionPanel';
import LiveTimeline from './components/LiveTimeline';
import ExplainabilityView from './components/ExplainabilityView';
import WhatIfSimulator from './components/WhatIfSimulator';
import HistoricalTrends from './components/HistoricalTrends';
import ModelMetricsView from './components/ModelMetricsView';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' or 'models'
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState('PT-101');
  const [state, setState] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const streamIntervalRef = useRef(null);

  // Initial load
  useEffect(() => {
    fetchPatients()
      .then((pts) => {
        setPatients(pts);
        if (pts.length > 0) {
          loadPatientData(pts[0].patient_id);
        }
      })
      .catch((err) => {
        console.error('Failed to load initial patients', err);
        setLoading(false);
      });
  }, []);

  const loadPatientData = async (patientId) => {
    setLoading(true);
    try {
      const [currState, hist] = await Promise.all([
        fetchCurrentState(patientId),
        fetchPatientHistory(patientId, 48),
      ]);
      setState(currState);
      setHistory(hist);
      setSelectedPatientId(patientId);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPatient = (patientId) => {
    if (isStreaming) {
      clearInterval(streamIntervalRef.current);
      setIsStreaming(false);
    }
    loadPatientData(patientId);
  };

  // Step forward simulation (ingest next 15-minute observation)
  const handleStepForward = async (steps = 1) => {
    try {
      const updatedState = await stepSimulation(selectedPatientId, steps);
      setState(updatedState);
      const updatedHist = await fetchPatientHistory(selectedPatientId, 48);
      setHistory(updatedHist);
    } catch (err) {
      console.error(err);
    }
  };

  // Reset simulation to designated scenario anchor
  const handleResetSimulation = async () => {
    try {
      const resetState = await resetSimulation(selectedPatientId);
      setState(resetState);
      const resetHist = await fetchPatientHistory(selectedPatientId, 48);
      setHistory(resetHist);
    } catch (err) {
      console.error(err);
    }
  };

  // Toggle live streaming replay (advances clock every 3 seconds)
  const handleToggleStreaming = () => {
    if (isStreaming) {
      clearInterval(streamIntervalRef.current);
      setIsStreaming(false);
    } else {
      setIsStreaming(true);
      streamIntervalRef.current = setInterval(async () => {
        try {
          const updatedState = await stepSimulation(selectedPatientId, 1);
          setState(updatedState);
          const updatedHist = await fetchPatientHistory(selectedPatientId, 48);
          setHistory(updatedHist);
        } catch (err) {
          console.error('Streaming error', err);
          clearInterval(streamIntervalRef.current);
          setIsStreaming(false);
        }
      }, 3000);
    }
  };

  useEffect(() => {
    return () => {
      if (streamIntervalRef.current) clearInterval(streamIntervalRef.current);
    };
  }, []);

  // Handle counterfactual what-if simulation call
  const handleWhatIfSimulate = async (scenario) => {
    return await simulateWhatIf(selectedPatientId, scenario);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Clinical Navigation Bar */}
      <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          {/* Logo & Tagline */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-lg">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black tracking-tight text-white">GlucoTwin AI</h1>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-700 font-semibold tracking-wider uppercase">
                  Digital Twin v1.0
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-700 font-medium hidden md:inline">
                  Happiest Health Challenge 2026
                </span>
              </div>
              <p className="text-xs text-slate-400 italic">
                “Simulate the Patient. Predict the Risk. Act Before the Spike.”
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              <Cpu className="w-4 h-4" />
              Patient Twin Dashboard
            </button>

            <button
              onClick={() => setActiveTab('models')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'models'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              Model Benchmarks & Metrics
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-5 space-y-5">
        {/* Safety Disclaimer Banner */}
        <SafetyDisclaimer />

        {activeTab === 'models' ? (
          <ModelMetricsView onBack={() => setActiveTab('dashboard')} />
        ) : (
          <>
            {/* Section A: Patient Overview & Cohort Switcher */}
            <PatientOverview
              patients={patients}
              selectedPatientId={selectedPatientId}
              onSelectPatient={handleSelectPatient}
              profile={state?.patient_profile}
              currentGlucose={state?.current_observation?.glucose}
            />

            {/* Sections B & D: Digital Twin Status & 2-Hour Prediction Panel */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <DigitalTwinStatus
                state={state}
                isStreaming={isStreaming}
                onToggleStreaming={handleToggleStreaming}
                onStepForward={handleStepForward}
                onResetSimulation={handleResetSimulation}
                loading={loading}
              />
              <PredictionPanel prediction={state?.prediction} />
            </div>

            {/* Section C: Live Patient Timeline (CGM, HR, Steps, Meals) */}
            <LiveTimeline history={history} />

            {/* Sections E & F: Explainable AI & What-If Simulation Sandbox */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <ExplainabilityView explanation={state?.explanation} />
              <WhatIfSimulator
                currentState={state}
                onSimulate={handleWhatIfSimulate}
                loading={loading}
              />
            </div>

            {/* Section G: Historical Trends, Correlations, and Actual vs Predicted */}
            <HistoricalTrends history={history} />
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 text-xs text-slate-400 py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-3">
          <div>
            <span className="font-semibold text-slate-300">GlucoTwin AI</span> — Designed for the{' '}
            <strong className="text-emerald-400">Happiest Health Digital Twin Challenge 2026</strong>.
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <span>XGBoost + SHAP Explainability</span>
            <span>&bull;</span>
            <span>Synthea EHR + Wearable IoT Telemetry</span>
            <span>&bull;</span>
            <span className="text-amber-400 font-medium">Research Prototype Only</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
