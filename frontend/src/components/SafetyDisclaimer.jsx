import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

export default function SafetyDisclaimer() {
  return (
    <div className="bg-amber-950/40 border border-amber-500/30 rounded-lg p-3 text-xs text-amber-200/90 flex items-start gap-3 shadow-sm">
      <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold text-amber-300 mr-1.5 uppercase tracking-wide">
          Research & Clinical Decision-Support Demonstration:
        </span>
        This software prototype is developed for the <strong>Happiest Health Digital Twin Challenge 2026</strong>. 
        It is an AI-driven physiological simulation tool designed to assist healthcare professionals in anticipating metabolic risk. 
        It is <strong>NOT a medical device</strong>, does NOT provide clinical diagnosis, and must NOT replace clinical judgment or direct patient assessment.
      </div>
    </div>
  );
}
