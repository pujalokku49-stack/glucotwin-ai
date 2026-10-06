import React, { useState } from 'react';
import {
  Sliders,
  Play,
  RotateCcw,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  Sparkles,
  Footprints,
  Moon,
  Utensils,
  Activity,
  ArrowRight
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  CartesianGrid,
  Legend
} from 'recharts';

export default function WhatIfSimulator({ currentState, onSimulate, loading }) {
  const currentObs = currentState?.current_observation;
  const currentPred = currentState?.prediction;

  // Simulator local form inputs
  const [sleep, setSleep] = useState(currentObs?.sleep_duration_hours || 7.0);
  const [steps, setSteps] = useState(currentObs?.steps || 300);
  const [carbs, setCarbs] = useState(currentObs?.meal_carbs_g || 0);
  const [currentG, setCurrentG] = useState(currentObs?.glucose || 120);

  // Result state
  const [simulationResult, setSimulationResult] = useState(null);

  const handleRunSimulation = async () => {
    const payload = {
      sleep_duration_hours: parseFloat(sleep),
      steps_1h: parseInt(steps),
      meal_carbs_g: parseFloat(carbs),
      current_glucose: parseFloat(currentG),
    };
    try {
      const res = await onSimulate(payload);
      setSimulationResult(res);
    } catch (err) {
      console.error(err);
    }
  };

  const handleResetInputs = () => {
    if (currentObs) {
      setSleep(currentObs.sleep_duration_hours);
      setSteps(currentObs.steps);
      setCarbs(currentObs.meal_carbs_g);
      setCurrentG(currentObs.glucose);
      setSimulationResult(null);
    }
  };

  // Trajectory comparison chart data
  let comparisonChartData = [];
  if (simulationResult && currentPred) {
    comparisonChartData = [
      {
        time: 'Now',
        current: currentObs?.glucose || currentPred.current_glucose,
        simulated: parseFloat(currentG),
      },
      {
        time: '+30m',
        current: currentPred.predicted_trajectory['+30m'],
        simulated: simulationResult.simulated_trajectory['+30m'],
      },
      {
        time: '+60m',
        current: currentPred.predicted_trajectory['+60m'],
        simulated: simulationResult.simulated_trajectory['+60m'],
      },
      {
        time: '+90m',
        current: currentPred.predicted_trajectory['+90m'],
        simulated: simulationResult.simulated_trajectory['+90m'],
      },
      {
        time: '+120m',
        current: currentPred.predicted_trajectory['+120m'],
        simulated: simulationResult.simulated_trajectory['+120m'],
      },
    ];
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-cyan-950/50 border border-cyan-800/40 text-cyan-400">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs uppercase tracking-wider text-slate-400 font-medium">Digital Twin Sandbox</span>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              What-If Counterfactual Scenario Simulator
            </h3>
          </div>
        </div>

        {/* Mandatory Simulation Label */}
        <div className="bg-amber-950/50 border border-amber-600/40 px-2.5 py-1 rounded-md text-[11px] text-amber-300 font-medium">
          Model-based scenario simulation — not a medical recommendation
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 mt-4">
        {/* Controls Column (5 cols) */}
        <div className="lg:col-span-5 bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-4">
          <div className="text-xs font-semibold text-slate-300 uppercase tracking-wide flex items-center justify-between">
            <span>Intervention Variables</span>
            <button
              onClick={handleResetInputs}
              className="text-[11px] text-slate-400 hover:text-slate-200 flex items-center gap-1 font-normal"
            >
              <RotateCcw className="w-3 h-3" /> Reset
            </button>
          </div>

          {/* 1. Sleep Slider */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 flex items-center gap-1.5">
                <Moon className="w-3.5 h-3.5 text-indigo-400" /> Sleep Duration:
              </span>
              <span className="font-mono font-bold text-indigo-300">{sleep} hrs</span>
            </div>
            <input
              type="range"
              min="4.0"
              max="9.5"
              step="0.5"
              value={sleep}
              onChange={(e) => setSleep(e.target.value)}
              className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
              <span>4.0h (Deprived)</span>
              <span>7.5h (Optimal)</span>
              <span>9.5h</span>
            </div>
          </div>

          {/* 2. Steps Slider */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 flex items-center gap-1.5">
                <Footprints className="w-3.5 h-3.5 text-emerald-400" /> Activity Past 1h:
              </span>
              <span className="font-mono font-bold text-emerald-300">{parseInt(steps).toLocaleString()} steps</span>
            </div>
            <input
              type="range"
              min="0"
              max="6000"
              step="200"
              value={steps}
              onChange={(e) => setSteps(e.target.value)}
              className="w-full accent-emerald-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
              <span>0 (Sedentary)</span>
              <span>2,500 (Moderate Walk)</span>
              <span>6,000 (Vigorous)</span>
            </div>
          </div>

          {/* 3. Meal Carbs Slider */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 flex items-center gap-1.5">
                <Utensils className="w-3.5 h-3.5 text-amber-400" /> Meal Carbohydrates:
              </span>
              <span className="font-mono font-bold text-amber-300">{carbs}g carbs</span>
            </div>
            <input
              type="range"
              min="0"
              max="110"
              step="5"
              value={carbs}
              onChange={(e) => setCarbs(e.target.value)}
              className="w-full accent-amber-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
              <span>0g (Fasting)</span>
              <span>30g (Low-Carb)</span>
              <span>60g (Moderate)</span>
              <span>110g (High)</span>
            </div>
          </div>

          {/* 4. Current Glucose Input Slider */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-rose-400" /> Pre-Event Glucose:
              </span>
              <span className="font-mono font-bold text-rose-300">{currentG} mg/dL</span>
            </div>
            <input
              type="range"
              min="80"
              max="240"
              step="5"
              value={currentG}
              onChange={(e) => setCurrentG(e.target.value)}
              className="w-full accent-rose-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
              <span>80 (Fasting Normal)</span>
              <span>140 (Target Max)</span>
              <span>240 (Hyperglycemia)</span>
            </div>
          </div>

          {/* Run Button */}
          <button
            onClick={handleRunSimulation}
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-xs tracking-wide uppercase transition-all shadow-md flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            Run What-If Simulation
          </button>
        </div>

        {/* Results Comparison Column (7 cols) */}
        <div className="lg:col-span-7 bg-slate-950/60 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
          {!simulationResult ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
              <Sparkles className="w-8 h-8 text-slate-600 mb-2" />
              <p className="text-sm font-medium text-slate-300">Ready for Counterfactual Exploration</p>
              <p className="text-xs text-slate-400 max-w-sm mt-1">
                Adjust lifestyle variables on the left (e.g. increase post-meal steps to 3,500 or lower meal carbs) and click
                "Run What-If Simulation" to observe how the Digital Twin predicts glycemic outcome changes.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Comparison Header Badge */}
              <div className="grid grid-cols-2 gap-3 text-center">
                {/* Current State */}
                <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
                    Current Patient State
                  </span>
                  <div className="text-2xl font-black text-white mt-1">
                    {simulationResult.baseline_risk_percent}%
                  </div>
                  <span className="text-[11px] font-bold text-slate-300 uppercase">
                    {simulationResult.baseline_risk_level} RISK
                  </span>
                </div>

                {/* Simulated State */}
                <div className="bg-slate-900 p-3 rounded-lg border border-cyan-800/60">
                  <span className="text-[10px] uppercase tracking-wider text-cyan-400 font-semibold flex items-center justify-center gap-1">
                    <Sparkles className="w-3 h-3" /> Simulated State
                  </span>
                  <div className={`text-2xl font-black mt-1 ${
                    simulationResult.risk_delta_percent <= 0 ? 'text-emerald-400' : 'text-rose-400'
                  }`}>
                    {simulationResult.simulated_risk_percent}%
                  </div>
                  <div className="flex items-center justify-center gap-1 text-[11px] font-bold">
                    <span className="uppercase text-slate-200">{simulationResult.simulated_risk_level} RISK</span>
                    <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${
                      simulationResult.risk_delta_percent <= 0 ? 'bg-emerald-950 text-emerald-300' : 'bg-rose-950 text-rose-300'
                    }`}>
                      {simulationResult.risk_delta_percent > 0 ? `+${simulationResult.risk_delta_percent}%` : `${simulationResult.risk_delta_percent}%`}
                    </span>
                  </div>
                </div>
              </div>

              {/* Trajectory Comparison Chart */}
              <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                <div className="text-xs font-semibold text-slate-300 mb-2">
                  2-Hour Forecast Comparison: Baseline vs Simulated
                </div>
                <div className="h-36 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={comparisonChartData} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
                      <YAxis stroke="#64748b" fontSize={10} domain={[60, 'dataMax + 20']} tickLine={false} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                      />
                      <ReferenceLine y={180} stroke="#f43f5e" strokeDasharray="3 3" />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }} />
                      <Line
                        type="monotone"
                        dataKey="current"
                        name="Current Baseline"
                        stroke="#94a3b8"
                        strokeWidth={2}
                        dot={{ r: 3 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="simulated"
                        name="Simulated Scenario"
                        stroke="#06b6d4"
                        strokeWidth={2.5}
                        dot={{ r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Interventions Applied */}
              <div className="text-xs space-y-1">
                <span className="text-[11px] text-slate-400 font-semibold uppercase tracking-wide">
                  Simulated Adjustments:
                </span>
                <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
                  {simulationResult.interventions_applied.map((inv, idx) => (
                    <li key={idx}>{inv}</li>
                  ))}
                </ul>
              </div>

              {/* Clinical Interpretation */}
              <div className="bg-cyan-950/30 border border-cyan-800/40 p-2.5 rounded-lg text-xs text-cyan-200">
                <span className="font-semibold text-cyan-300 mr-1">Physiological Interpretation:</span>
                {simulationResult.clinical_interpretation}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
