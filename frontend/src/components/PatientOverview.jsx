import React from 'react';
import { User, Activity, Heart, Clock, FileText, Pill, ShieldAlert } from 'lucide-react';

export default function PatientOverview({ patients, selectedPatientId, onSelectPatient, profile, currentGlucose }) {
  if (!profile) return null;

  const demoPatients = [
    { id: 'PT-101', name: 'Eleanor Vance', tag: 'Stable / Low Risk', color: 'emerald' },
    { id: 'PT-102', name: 'Rajesh Kumar', tag: 'Moderate Risk', color: 'amber' },
    { id: 'PT-103', name: 'Marcus Chen', tag: 'High Risk Scenario', color: 'rose' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      {/* Demo Patient Selector Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="text-xs uppercase tracking-wider text-emerald-400 font-semibold mb-1 flex items-center gap-1.5">
            <User className="w-3.5 h-3.5" />
            Static EHR Patient Profile
          </div>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-white tracking-tight">{profile.name}</h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 font-mono">
              {profile.patient_id}
            </span>
            <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
              profile.risk_category === 'LOW' ? 'bg-emerald-950 text-emerald-300 border border-emerald-700/50' :
              profile.risk_category === 'HIGH' ? 'bg-rose-950 text-rose-300 border border-rose-700/50' :
              'bg-amber-950 text-amber-300 border border-amber-700/50'
            }`}>
              {profile.risk_category} RISK PROFILE
            </span>
          </div>
        </div>

        {/* Demo Cohort Switcher Buttons */}
        <div className="flex items-center gap-2">
          <div className="flex bg-slate-950/80 p-1 rounded-lg border border-slate-800">
            {demoPatients.map((dp) => {
              const active = selectedPatientId === dp.id;
              return (
                <button
                  key={dp.id}
                  onClick={() => onSelectPatient(dp.id)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    active 
                      ? 'bg-slate-800 text-white shadow-sm border border-slate-700 font-semibold' 
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <span className={`inline-block w-2 h-2 rounded-full mr-1.5 ${
                    dp.color === 'emerald' ? 'bg-emerald-400' : dp.color === 'rose' ? 'bg-rose-400' : 'bg-amber-400'
                  }`} />
                  {dp.name.split(' ')[0]}
                </button>
              );
            })}
          </div>

          {/* Full Cohort Dropdown */}
          <select
            value={selectedPatientId}
            onChange={(e) => onSelectPatient(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg px-2.5 py-2 focus:outline-none focus:border-emerald-500"
          >
            {patients.map((p) => (
              <option key={p.patient_id} value={p.patient_id}>
                {p.patient_id} - {p.name} ({p.risk_category})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Profile Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mt-4">
        <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">Demographics</div>
          <div className="text-base font-semibold text-white mt-1">
            {profile.age}y <span className="text-slate-400 text-xs font-normal">/ {profile.sex}</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">T2D: {profile.diabetes_duration_years} yrs</div>
        </div>

        <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">BMI</div>
          <div className="text-base font-semibold text-white mt-1">
            {profile.bmi} <span className="text-slate-400 text-xs font-normal">kg/m²</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">
            {profile.bmi < 25 ? 'Normal' : profile.bmi < 30 ? 'Overweight' : 'Obese'}
          </div>
        </div>

        <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">HbA1c</div>
          <div className={`text-base font-semibold mt-1 ${
            profile.hba1c < 7.0 ? 'text-emerald-400' : profile.hba1c < 8.5 ? 'text-amber-400' : 'text-rose-400'
          }`}>
            {profile.hba1c}%
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Target: &lt;7.0%</div>
        </div>

        <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">Fasting Glucose</div>
          <div className="text-base font-semibold text-white mt-1">
            {profile.fasting_glucose} <span className="text-slate-400 text-xs font-normal">mg/dL</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Baseline lab</div>
        </div>

        <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">Blood Pressure</div>
          <div className="text-base font-semibold text-white mt-1">{profile.blood_pressure}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">mmHg</div>
        </div>

        <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">Sleep & Activity</div>
          <div className="text-base font-semibold text-white mt-1">
            {profile.typical_sleep_hours}h <span className="text-slate-400 text-xs font-normal">/ night</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">{profile.baseline_activity_steps.toLocaleString()} steps/day</div>
        </div>

        <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">Current Glucose</div>
          <div className={`text-base font-bold mt-1 ${
            currentGlucose >= 180 ? 'text-rose-400' : currentGlucose >= 140 ? 'text-amber-400' : 'text-emerald-400'
          }`}>
            {currentGlucose ? `${currentGlucose} mg/dL` : '—'}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Live CGM Ingestion</div>
        </div>
      </div>

      {/* Medication & Clinical Notes Bar */}
      <div className="mt-3 pt-3 border-t border-slate-800/60 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-slate-400 flex items-center gap-1 font-medium">
            <Pill className="w-3.5 h-3.5 text-indigo-400" />
            Prescriptions:
          </span>
          {profile.medications.map((m, idx) => (
            <span key={idx} className="bg-indigo-950/60 border border-indigo-800/50 text-indigo-300 px-2 py-0.5 rounded text-[11px]">
              {m}
            </span>
          ))}
          <span className="text-slate-400 text-[11px] ml-1">
            (Adherence: <span className="text-slate-200 font-semibold">{Math.round(profile.medication_adherence * 100)}%</span>)
          </span>
        </div>

        <div className="text-slate-400 text-[11px] flex items-center gap-1.5 italic">
          <FileText className="w-3 h-3 text-slate-400" />
          <span>"{profile.clinical_notes}"</span>
        </div>
      </div>
    </div>
  );
}
