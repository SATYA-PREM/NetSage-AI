const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

async function request(path, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || 'Request failed');
    return body;
  } catch (error) {
    if (error instanceof TypeError) throw new Error('Backend unavailable');
    throw error;
  }
}

export const diagnoseCase = (input, inputType = 'text') =>
  request('/api/diagnose', { method: 'POST', body: JSON.stringify({ input, input_type: inputType }) });

export const getHistory = () => request('/api/history');
export const getCase = (caseId) => request(`/api/history/${caseId}`);
export const submitReview = (caseId, review) =>
  request(`/api/review/${caseId}`, { method: 'POST', body: JSON.stringify(review) });
export const getCases = () => request('/api/cases');
export const createCase = (caseData) =>
  request('/api/cases', { method: 'POST', body: JSON.stringify(caseData) });
export const getHealth = () => request('/api/health');

// --- NEW: Roadmap interaction ---
export const getRoadmap = (caseId) => request(`/api/roadmap/${caseId}`);
export const markStep = (caseId, stepId, status) =>
  request(`/api/step/${caseId}`, {
    method: 'POST',
    body: JSON.stringify({ step_id: stepId, status })
  });
export const continueCase = (caseId, evidence) =>
  request(`/api/continue/${caseId}`, {
    method: 'POST',
    body: JSON.stringify({ evidence })
  });
export const verifyCase = (caseId, result, detail = '') =>
  request(`/api/verify/${caseId}`, {
    method: 'POST',
    body: JSON.stringify({ result, detail })
  });
