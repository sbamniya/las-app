const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "API request failed");
  }
  return res.json();
}

export const api = {
  // Organizations
  createOrg: (data: any) =>
    apiCall("/api/assessments/organizations", { method: "POST", body: JSON.stringify(data) }),

  // Assessments
  createAssessment: (data: any) =>
    apiCall("/api/assessments/", { method: "POST", body: JSON.stringify(data) }),
  getAssessment: (id: string) =>
    apiCall(`/api/assessments/${id}`),

  // Chat
  startChat: (assessmentId: string, mode: string, goal: string, industry?: string) =>
    apiCall(
      `/api/chat/start?assessment_id=${assessmentId}&mode=${mode}&transformation_goal=${goal}${industry ? `&industry=${industry}` : ""}`,
      { method: "POST" }
    ),
  sendMessage: (data: { content: string; assessment_id: string; conversation_id: string }) =>
    apiCall("/api/chat/message", { method: "POST", body: JSON.stringify(data) }),

  // Scoring
  calculateAgentScore: (data: any) =>
    apiCall("/api/scoring/agent-score", { method: "POST", body: JSON.stringify(data) }),
  calculateFullROI: (data: any) =>
    apiCall("/api/scoring/full-roi", { method: "POST", body: JSON.stringify(data) }),

  // Reports
  generateReport: (assessmentId: string) =>
    apiCall("/api/reports/generate", { method: "POST", body: JSON.stringify({ assessment_id: assessmentId }) }),
  generateRecommendations: (assessmentId: string) =>
    apiCall(`/api/reports/recommendations?assessment_id=${assessmentId}`, { method: "POST" }),

  // Simulation
  simulate: (data: any) =>
    apiCall("/api/assessments/simulate", { method: "POST", body: JSON.stringify(data) }),
};
