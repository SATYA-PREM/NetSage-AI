const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
      signal: controller.signal,
    });
    const text = await response.text();
    let data = {};
    try {
      data = text ? JSON.parse(text) : {};
    } catch {
      data = { detail: text };
    }
    if (!response.ok) {
      throw new Error(data.detail || data.message || `Request failed with status ${response.status}`);
    }
    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The diagnosis timed out. Check the backend and Gemini API configuration.");
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export async function getHealth() {
  return request("/health");
}
export async function getCases() {
  return request("/api/cases");
}
export async function getCase(caseId) {
  return request(`/api/cases/${encodeURIComponent(caseId)}`);
}
export async function runDiagnosis(payload) {
  return request("/api/diagnosis", {
    method: "POST",
    body: JSON.stringify({
      case_id: payload.case_id || "CUSTOM",
      symptom: payload.symptom || "",
      topology: payload.topology || payload.topology_note || "",
      command_output: payload.command_output || payload.show_outputs || "",
    }),
  });
}
export async function getReviews() {
  return request("/api/reviews");
}
export async function createReview(payload) {
  return request("/api/reviews", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
export async function getDashboard() {
  return request("/api/dashboard");
}

export const api = {
  getHealth,
  getCases,
  getCase,
  runDiagnosis,
  getReviews,
  createReview,
  getDashboard,
};