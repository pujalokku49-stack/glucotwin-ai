import React from 'react';
import { HelpCircle, ArrowUpRight, ArrowDownRight, Lightbulb, Info } from 'lucide-react';

export default function ExplainabilityView({ explanation }) {
  if (!explanation) return null;

  const { top_risk_contributors, summary_sentence, base_value } = explanation;

  // Maximum impact for normalizing bar lengths
  const maxImpact = Math.max(...top_risk_contributors.map(c => Math.abs(c.impact_value)), 0.5);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-teal-950/50 border border-teal-800/40 text-teal-400">
            <Lightbulb className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs uppercase tracking-wider text-slate-400 font-medium">Explainable AI (XAI)</span>
            <h3 className="text-base font-bold text-white">SHAP Attribution: Why is Risk at this Level?</h3>
          </div>
        </div>

        <div className="text-xs text-slate-400 flex items-center gap-1.5 font-mono">
          <span>TreeExplainer</span>
          <span className="text-slate-600">|</span>
          <span>Base Value: {base_value}</span>
        </div>
      </div>

      {/* Narrative Synthesis */}
      <div className="my-3 bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 text-xs text-slate-300 flex items-start gap-2.5">
        <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-cyan-300 mr-1">Clinical Attribution Summary:</span>
          {summary_sentence}
        </div>
      </div>

      {/* SHAP Factor Waterfall / List */}
      <div className="space-y-2.5 mt-4">
        {top_risk_contributors.map((factor, idx) => {
          const isRisk = factor.direction === 'INCREASES_RISK';
          const impactMagnitude = Math.abs(factor.impact_value);
          const barWidthPercent = Math.min(100, Math.round((impactMagnitude / maxImpact) * 100));

          return (
            <div
              key={idx}
              className="bg-slate-950/40 hover:bg-slate-950/70 transition-colors p-3 rounded-lg border border-slate-800/70"
            >
              <div className="flex items-center justify-between text-xs mb-1.5">
                <div className="flex items-center gap-2">
                  <span className={`p-1 rounded ${isRisk ? 'bg-rose-950 text-rose-400' : 'bg-emerald-950 text-emerald-400'}`}>
                    {isRisk ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                  </span>
                  <span className="font-semibold text-white">{factor.label}</span>
                  <span className="text-[11px] text-slate-400 font-mono">
                    (Observed: {factor.feature_value})
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`font-mono text-xs font-bold ${isRisk ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {isRisk ? `+${factor.impact_value.toFixed(2)}` : factor.impact_value.toFixed(2)} SHAP
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                    isRisk ? 'bg-rose-950/80 text-rose-300 border border-rose-800/50' : 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/50'
                  }`}>
                    {isRisk ? 'Risk Driver' : 'Protective Factor'}
                  </span>
                </div>
              </div>

              {/* Impact Bar */}
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden my-2">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isRisk ? 'bg-gradient-to-r from-rose-600 to-rose-400' : 'bg-gradient-to-r from-emerald-600 to-emerald-400'
                  }`}
                  style={{ width: `${barWidthPercent}%` }}
                />
              </div>

              {/* Physiological Mechanism Explanation */}
              <div className="text-[11px] text-slate-400 mt-1 pl-1 border-l-2 border-slate-700">
                {factor.explanation}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
