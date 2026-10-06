import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
  Legend
} from 'recharts';
import { Activity, Heart, Footprints, Utensils, Moon } from 'lucide-react';

export default function LiveTimeline({ history }) {
  if (!history || history.length === 0) return null;

  const [activeMetric, setActiveMetric] = useState('all'); // 'all', 'glucose', 'hr', 'steps'

  // Format observations for chart
  const formattedData = history.map((obs) => {
    const d = new Date(obs.timestamp);
    const timeStr = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return {
      time: timeStr,
      glucose: obs.glucose,
      heartRate: obs.heart_rate,
      hrv: obs.hrv,
      steps: obs.steps,
      mealCarbs: obs.meal_carbs_g,
      mealEvent: obs.meal_event !== 'None' ? obs.meal_event : null,
      isSleeping: obs.is_sleeping,
    };
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-emerald-950/50 border border-emerald-800/40 text-emerald-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs uppercase tracking-wider text-slate-400 font-medium">Dynamic Multi-Modal Stream</span>
            <h3 className="text-base font-bold text-white">Live Patient Timeline & Ingested IoT Telemetry</h3>
          </div>
        </div>

        {/* Metric Filter Chips */}
        <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => setActiveMetric('all')}
            className={`px-2.5 py-1 rounded font-medium transition-colors ${
              activeMetric === 'all' ? 'bg-slate-800 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Combined View
          </button>
          <button
            onClick={() => setActiveMetric('glucose')}
            className={`px-2.5 py-1 rounded font-medium transition-colors ${
              activeMetric === 'glucose' ? 'bg-emerald-950 text-emerald-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            CGM Glucose
          </button>
          <button
            onClick={() => setActiveMetric('hr')}
            className={`px-2.5 py-1 rounded font-medium transition-colors ${
              activeMetric === 'hr' ? 'bg-rose-950 text-rose-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            HR & HRV
          </button>
          <button
            onClick={() => setActiveMetric('steps')}
            className={`px-2.5 py-1 rounded font-medium transition-colors ${
              activeMetric === 'steps' ? 'bg-cyan-950 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Activity & Meals
          </button>
        </div>
      </div>

      {/* Main Chart */}
      <div className="h-72 w-full mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={formattedData} margin={{ top: 15, right: 20, left: -15, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} />
            
            {/* Primary Left Axis: Glucose (mg/dL) */}
            <YAxis
              yAxisId="glucose"
              domain={[60, 'dataMax + 25']}
              stroke="#10b981"
              fontSize={11}
              tickLine={false}
              label={{ value: 'Glucose (mg/dL)', angle: -90, position: 'insideLeft', fill: '#10b981', fontSize: 10 }}
            />

            {/* Secondary Right Axis: Heart Rate & Steps */}
            <YAxis
              yAxisId="secondary"
              orientation="right"
              domain={[0, 'dataMax + 200']}
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              label={{ value: 'HR (bpm) / Steps', angle: 90, position: 'insideRight', fill: '#94a3b8', fontSize: 10 }}
            />

            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
              formatter={(value, name, item) => {
                if (name === 'CGM Glucose') return [`${value} mg/dL`, name];
                if (name === 'Heart Rate') return [`${value} bpm`, name];
                if (name === 'Steps') return [`${value} steps`, name];
                return [value, name];
              }}
            />

            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />

            {/* Clinical Reference Lines for Glucose */}
            <ReferenceLine
              yAxisId="glucose"
              y={180}
              stroke="#f43f5e"
              strokeDasharray="4 4"
              label={{ value: 'Spike Threshold (180 mg/dL)', fill: '#f43f5e', fontSize: 10, position: 'insideTopLeft' }}
            />
            <ReferenceLine
              yAxisId="glucose"
              y={140}
              stroke="#34d399"
              strokeDasharray="2 2"
              label={{ value: 'Normal Upper (140 mg/dL)', fill: '#34d399', fontSize: 10, position: 'insideBottomLeft' }}
            />

            {/* Steps as Semi-Transparent Cyan Bars */}
            {(activeMetric === 'all' || activeMetric === 'steps') && (
              <Bar
                yAxisId="secondary"
                dataKey="steps"
                name="Steps"
                fill="#06b6d4"
                opacity={0.35}
                radius={[2, 2, 0, 0]}
              />
            )}

            {/* Heart Rate as Amber Line */}
            {(activeMetric === 'all' || activeMetric === 'hr') && (
              <Line
                yAxisId="secondary"
                type="monotone"
                dataKey="heartRate"
                name="Heart Rate"
                stroke="#f59e0b"
                strokeWidth={1.5}
                dot={false}
              />
            )}

            {/* CGM Glucose Line */}
            {(activeMetric === 'all' || activeMetric === 'glucose') && (
              <Line
                yAxisId="glucose"
                type="monotone"
                dataKey="glucose"
                name="CGM Glucose"
                stroke="#10b981"
                strokeWidth={2.5}
                dot={{ r: 2.5, fill: '#10b981' }}
                activeDot={{ r: 5 }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Timeline Event Annotations (Meals & Activity) */}
      <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 flex-wrap gap-2">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2.5 h-0.5 bg-emerald-400 inline-block" /> CGM Glucose
          </span>
          <span className="flex items-center gap-1.5 text-amber-400">
            <span className="w-2.5 h-0.5 bg-amber-400 inline-block" /> Heart Rate (bpm)
          </span>
          <span className="flex items-center gap-1.5 text-cyan-400">
            <span className="w-2.5 h-2 bg-cyan-400/40 inline-block rounded-xs" /> Step Activity
          </span>
        </div>

        <div className="flex items-center gap-3 text-[11px]">
          <span className="text-slate-400">Target Euglycemic Zone: 70 – 140 mg/dL</span>
          <span className="text-rose-400 font-medium">Hyperglycemic Excursion: &ge;180 mg/dL</span>
        </div>
      </div>
    </div>
  );
}
