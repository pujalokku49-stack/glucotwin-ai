import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  CartesianGrid
} from 'recharts';
import { TrendingUp, AlertCircle, ShieldCheck, Flame, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export default function PredictionPanel({ prediction }) {
  if (!prediction) return null;

  const {
    spike_risk_percent,
    risk_level,
    expected_trend,
    predicted_trajectory,
    current_glucose
  } = prediction;

  // Build chart points connecting Current -> +30m -> +60m -> +90m -> +120m
  const chartData = [
    { time: 'Now', glucose: current_glucose, type: 'actual' },
    { time: '+30m', glucose: predicted_trajectory['+30m'], type: 'forecast' },
    { time: '+60m', glucose: predicted_trajectory['+60m'], type: 'forecast' },
    { time: '+90m', glucose: predicted_trajectory['+90m'], type: 'forecast' },
    { time: '+120m', glucose: predicted_trajectory['+120m'], type: 'forecast' },
  ];

  const riskBadgeStyles = {
    LOW: 'bg-emerald-950 text-emerald-300 border-emerald-600/60',
    MODERATE: 'bg-amber-950 text-amber-300 border-amber-600/60',
    HIGH: 'bg-rose-950 text-rose-300 border-rose-600/60'
  };

  const riskGradient = {
    LOW: 'from-emerald-500 to-teal-400',
    MODERATE: 'from-amber-500 to-orange-400',
    HIGH: 'from-rose-500 to-red-400'
  };

  const trendIcon = {
    RAPID_INCREASE: <ArrowUpRight className="w-4 h-4 text-rose-400" />,
    MILD_INCREASE: <ArrowUpRight className="w-4 h-4 text-amber-400" />,
    STEADY: <Minus className="w-4 h-4 text-emerald-400" />,
    DECREASING: <ArrowDownRight className="w-4 h-4 text-cyan-400" />
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-indigo-950/50 border border-indigo-800/40 text-indigo-400">
            <Flame className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <span className="text-xs uppercase tracking-wider text-slate-400 font-medium">Early Warning Engine</span>
            <h3 className="text-base font-bold text-white">2-Hour Glucose Spike Prediction</h3>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] uppercase tracking-wider text-slate-400">Horizon</span>
          <div className="text-xs font-semibold text-slate-200">Next 120 Minutes</div>
        </div>
      </div>

      {/* Main Prediction Score & Trajectory Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-4">
        {/* Risk Probability Card */}
        <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 flex flex-col justify-between items-center text-center">
          <span className="text-xs text-slate-400 uppercase tracking-wide font-medium">Spike Probability</span>
          <div className="my-2 relative flex items-center justify-center">
            {/* Circular Progress Ring */}
            <div className="relative w-28 h-28 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-800"
                  strokeWidth="3.2"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className={
                    risk_level === 'HIGH' ? 'text-rose-500' :
                    risk_level === 'MODERATE' ? 'text-amber-500' : 'text-emerald-500'
                  }
                  strokeDasharray={`${spike_risk_percent}, 100`}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-3xl font-extrabold text-white tracking-tight">{spike_risk_percent}%</span>
                <span className="text-[10px] text-slate-400 font-medium uppercase">Risk Score</span>
              </div>
            </div>
          </div>

          <div className={`px-3 py-1 rounded-full text-xs font-bold border tracking-wider uppercase ${riskBadgeStyles[risk_level] || riskBadgeStyles.LOW}`}>
            {risk_level} SPIKE RISK
          </div>
        </div>

        {/* Expected Trend & Trajectory Stats */}
        <div className="md:col-span-2 bg-slate-950/70 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 text-xs">
            <span className="text-slate-400 font-medium">Trajectory Dynamics</span>
            <div className="flex items-center gap-1 font-semibold text-slate-200">
              {trendIcon[expected_trend] || <Minus className="w-4 h-4" />}
              <span>{expected_trend.replace('_', ' ')}</span>
            </div>
          </div>

          {/* Forecast trajectory graph */}
          <div className="h-40 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 15, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis
                  domain={[60, 'dataMax + 25']}
                  stroke="#64748b"
                  fontSize={11}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val, name, item) => [`${val} mg/dL`, item.payload.time === 'Now' ? 'Current Baseline' : 'Predicted Forecast']}
                />
                {/* 180 mg/dL Spike Threshold */}
                <ReferenceLine
                  y={180}
                  stroke="#f43f5e"
                  strokeDasharray="4 4"
                  label={{ value: 'Spike Limit (180)', fill: '#f43f5e', fontSize: 10, position: 'insideTopRight' }}
                />
                {/* 140 mg/dL Normal Upper Target */}
                <ReferenceLine
                  y={140}
                  stroke="#10b981"
                  strokeDasharray="2 2"
                  label={{ value: 'Target Max (140)', fill: '#10b981', fontSize: 10, position: 'insideBottomRight' }}
                />
                <Line
                  type="monotone"
                  dataKey="glucose"
                  stroke={risk_level === 'HIGH' ? '#f43f5e' : risk_level === 'MODERATE' ? '#f59e0b' : '#10b981'}
                  strokeWidth={2.5}
                  dot={{ r: 4, strokeWidth: 1.5, fill: '#0f172a' }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Horizon Milestones values */}
          <div className="grid grid-cols-4 gap-2 pt-2 border-t border-slate-800/80 text-center">
            {['+30m', '+60m', '+90m', '+120m'].map((h) => {
              const val = predicted_trajectory[h];
              const isOver = val >= 180;
              return (
                <div key={h} className="bg-slate-900/60 p-1.5 rounded border border-slate-800/60">
                  <div className="text-[10px] text-slate-400 font-mono">{h}</div>
                  <div className={`text-xs font-bold mt-0.5 ${isOver ? 'text-rose-400' : 'text-slate-200'}`}>
                    {val} <span className="text-[9px] font-normal text-slate-400">mg/dL</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Clinical Guidance Footnote */}
      <div className="text-[11px] text-slate-400 flex items-center gap-1.5 pt-2 border-t border-slate-800">
        <AlertCircle className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        <span>
          Spike is defined as postprandial glucose reaching <strong>&ge;180 mg/dL</strong> or experiencing an acute rise of <strong>&ge;50 mg/dL</strong> within 2 hours.
        </span>
      </div>
    </div>
  );
}
