import React from 'react';
import { Cpu, Play, Pause, FastForward, RotateCcw, Activity, Clock, Database, Radio } from 'lucide-react';

export default function DigitalTwinStatus({
  state,
  isStreaming,
  onToggleStreaming,
  onStepForward,
  onResetSimulation,
  loading
}) {
  if (!state) return null;

  const { status, last_synced_at, prediction, current_observation } = state;
  const riskColor = 
    prediction.risk_level === 'HIGH' ? 'text-rose-400 bg-rose-950/80 border-rose-700/60' :
    prediction.risk_level === 'MODERATE' ? 'text-amber-400 bg-amber-950/80 border-amber-700/60' :
    'text-emerald-400 bg-emerald-950/80 border-emerald-700/60';

  const timeFormatted = current_observation?.timestamp ? 
    new Date(current_observation.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 
    '--:--';

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
      {/* Top Header */}
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-emerald-950/50 border border-emerald-800/40 text-emerald-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-slate-400 font-medium">Digital Twin Engine</div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Physiological State Engine
                <span className="flex items-center gap-1.5 text-[11px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800/60 font-semibold font-mono">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  {status}
                </span>
              </h3>
            </div>
          </div>

          <div className="text-right">
            <span className="text-[11px] text-slate-400">Metabolic Risk State:</span>
            <div className={`mt-0.5 px-3 py-1 rounded-md text-xs font-bold border tracking-wide uppercase ${riskColor}`}>
              {prediction.risk_level} METABOLIC RISK
            </div>
          </div>
        </div>

        {/* Status Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 my-4">
          <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase tracking-wide flex items-center gap-1">
              <Clock className="w-3 h-3 text-slate-400" /> Virtual Time
            </span>
            <div className="text-sm font-bold text-white mt-1 font-mono">{timeFormatted}</div>
          </div>

          <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase tracking-wide flex items-center gap-1">
              <Radio className="w-3 h-3 text-emerald-400" /> Ingestion Frequency
            </span>
            <div className="text-sm font-bold text-slate-200 mt-1">15 min (CGM)</div>
          </div>

          <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase tracking-wide flex items-center gap-1">
              <Database className="w-3 h-3 text-indigo-400" /> Memory Buffer
            </span>
            <div className="text-sm font-bold text-slate-200 mt-1">{state.recent_history.length + 1} observations</div>
          </div>

          <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase tracking-wide flex items-center gap-1">
              <Activity className="w-3 h-3 text-amber-400" /> Model Pipeline
            </span>
            <div className="text-xs font-bold text-slate-300 mt-1 truncate" title={prediction.model_version}>
              XGBoost + SHAP
            </div>
          </div>
        </div>

        {/* Evolving State Pipeline Flow */}
        <div className="bg-slate-950/80 p-2.5 rounded-lg border border-slate-800/80 text-[11px] text-slate-400 flex items-center justify-between overflow-x-auto gap-2">
          <div className="flex items-center gap-1.5 shrink-0">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            <span>Wearables IoT Ingestion</span>
          </div>
          <span className="text-slate-600 font-bold">&rarr;</span>
          <div className="flex items-center gap-1.5 shrink-0">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            <span>Time Sync & Memory</span>
          </div>
          <span className="text-slate-600 font-bold">&rarr;</span>
          <div className="flex items-center gap-1.5 shrink-0">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            <span>Feature Engineering</span>
          </div>
          <span className="text-slate-600 font-bold">&rarr;</span>
          <div className="flex items-center gap-1.5 shrink-0">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span>Digital Twin Forecast</span>
          </div>
        </div>
      </div>

      {/* Streaming Replay Controls */}
      <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between flex-wrap gap-2">
        <div className="text-xs text-slate-400 flex items-center gap-1.5">
          <span className="font-medium text-slate-300">IoT Simulation Replay:</span>
          Advance time to simulate continuous wearable streaming
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onStepForward(1)}
            disabled={loading || isStreaming}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors disabled:opacity-50 border border-slate-700"
            title="Ingest next 15-minute wearable observation packet"
          >
            <FastForward className="w-3.5 h-3.5 text-cyan-400" />
            Step +15m
          </button>

          <button
            onClick={onToggleStreaming}
            disabled={loading}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
              isStreaming
                ? 'bg-rose-950 text-rose-300 border-rose-700 hover:bg-rose-900'
                : 'bg-emerald-950 text-emerald-300 border-emerald-700 hover:bg-emerald-900'
            }`}
          >
            {isStreaming ? (
              <>
                <Pause className="w-3.5 h-3.5" /> Stop Stream
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5" /> Auto-Stream (3s)
              </>
            )}
          </button>

          <button
            onClick={onResetSimulation}
            disabled={loading}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-400 hover:text-slate-200 border border-slate-700"
            title="Reset to scenario starting point"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
