const API_BASE = '/api';

export async function fetchSystemInfo() {
  const res = await fetch(`${API_BASE}/system-info`);
  if (!res.ok) throw new Error('Failed to fetch system info');
  return res.json();
}

export async function fetchPatients() {
  const res = await fetch(`${API_BASE}/patients`);
  if (!res.ok) throw new Error('Failed to fetch patients list');
  return res.json();
}

export async function fetchCurrentState(patientId) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/current-state`);
  if (!res.ok) throw new Error(`Failed to fetch state for patient ${patientId}`);
  return res.json();
}

export async function fetchPatientHistory(patientId, limit = 48) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/history?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch patient history');
  return res.json();
}

export async function fetchPrediction(patientId) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/prediction`);
  if (!res.ok) throw new Error('Failed to fetch prediction');
  return res.json();
}

export async function fetchExplanation(patientId) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/explanation`);
  if (!res.ok) throw new Error('Failed to fetch explanation');
  return res.json();
}

export async function simulateWhatIf(patientId, scenario) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scenario),
  });
  if (!res.ok) throw new Error('Simulation failed');
  return res.json();
}

export async function stepSimulation(patientId, steps = 1) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/step?steps=${steps}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Step simulation failed');
  return res.json();
}

export async function resetSimulation(patientId) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/reset`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Reset simulation failed');
  return res.json();
}

export async function fetchModelMetrics() {
  const res = await fetch(`${API_BASE}/model-metrics`);
  if (!res.ok) throw new Error('Failed to fetch model metrics');
  return res.json();
}
