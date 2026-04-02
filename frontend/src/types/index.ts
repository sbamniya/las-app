export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  scores?: Record<string, number>;
}

export interface AssessmentScores {
  caito?: {
    overall: number;
    grade: string;
    pillars: Record<string, { raw: number; weighted: number }>;
    benchmark_delta?: Record<string, number>;
  };
  gsti?: {
    overall: number;
    trust_level: string;
    deployment_risk: string;
    autonomy_readiness: number;
  };
  rai?: { ratio: number; payback_months?: number };
  raia?: { ratio: number; per_agent?: any[] };
  raw?: { score: number; grade: string; components?: Record<string, number> };
  total_roi?: { score: number; grade: string };
}

export interface Assessment {
  id: string;
  organization_id: string;
  mode: string;
  transformation_goal: string;
  status: string;
  caito_score?: number;
  caito_grade?: string;
  gsti_score?: number;
  rai_score?: number;
  raia_score?: number;
  raw_score?: number;
  total_roi?: number;
  gaps?: any[];
  opportunities?: any[];
  recommendations?: any;
  roadmap?: any;
  agent_deployment_plan?: any;
}

export interface SimulationResult {
  original_caito: number;
  simulated_caito: number;
  delta: number;
  pillar_deltas: Record<string, number>;
}
