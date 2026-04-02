"use client";
import type { AssessmentScores } from "@/types";
import ScoreGauge from "./ScoreGauge";
import RadarChart from "./RadarChart";
import ROIWaterfall from "./ROIWaterfall";

interface DashboardProps {
  scores: AssessmentScores;
}

export default function Dashboard({ scores }: DashboardProps) {
  const caito = scores.caito;
  const gsti = scores.gsti;
  const raw = scores.raw;

  if (!caito) {
    return (
      <div className="flex items-center justify-center h-full text-fuzebox-muted">
        <div className="text-center">
          <div className="text-6xl mb-4 opacity-30">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="mx-auto">
              <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
              <path d="M3 3v5h5" />
              <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
              <path d="M16 16h5v5" />
            </svg>
          </div>
          <p className="text-lg font-medium">Assessment in Progress</p>
          <p className="text-sm mt-1">Scores will appear here as the assessment progresses</p>
        </div>
      </div>
    );
  }

  const radarData = Object.entries(caito.pillars).map(([pillar, data]) => ({
    pillar,
    score: data.raw,
    benchmark: 0.55,
  }));

  const trustColor = gsti
    ? gsti.trust_level === "autonomous" ? "#10B981"
      : gsti.trust_level === "trusted" ? "#3B82F6"
      : gsti.trust_level === "conditional" ? "#F59E0B"
      : "#F43F5E"
    : "#6B7280";

  const riskColor = gsti
    ? gsti.deployment_risk === "low" ? "#10B981"
      : gsti.deployment_risk === "medium" ? "#F59E0B"
      : gsti.deployment_risk === "high" ? "#F43F5E"
      : "#DC2626"
    : "#6B7280";

  return (
    <div className="h-full overflow-y-auto p-5 space-y-6">
      {/* Score Gauges Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-4 flex flex-col items-center">
          <ScoreGauge score={caito.overall} label="CAITO" grade={caito.grade} />
          <span className="text-[10px] text-fuzebox-muted mt-1">AI Readiness</span>
        </div>
        <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-4 flex flex-col items-center">
          <ScoreGauge score={gsti?.overall || 0} label="GSTI" color={trustColor} />
          <span className="text-[10px] text-fuzebox-muted mt-1">Trust Index</span>
        </div>
        <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-4 flex flex-col items-center">
          <ScoreGauge score={raw?.score || 0} label="RAW" color="#10B981" grade={raw?.grade} />
          <span className="text-[10px] text-fuzebox-muted mt-1">Agentic Workflows</span>
        </div>
        <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-4 flex flex-col items-center">
          <ScoreGauge score={gsti?.autonomy_readiness || 0} label="Autonomy" color="#8B5CF6" />
          <span className="text-[10px] text-fuzebox-muted mt-1">Agent Ready</span>
        </div>
      </div>

      {/* CAITO Radar */}
      <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-fuzebox-text mb-3 uppercase tracking-wider">
          CAITO Pillar Analysis
        </h3>
        <RadarChart data={radarData} />
      </div>

      {/* Trust & Risk Indicators */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-4">
          <h4 className="text-xs font-semibold text-fuzebox-dim uppercase tracking-wider mb-3">Trust Level</h4>
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: trustColor }} />
            <span className="text-lg font-bold capitalize" style={{ color: trustColor }}>
              {gsti?.trust_level || "N/A"}
            </span>
          </div>
        </div>
        <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-4">
          <h4 className="text-xs font-semibold text-fuzebox-dim uppercase tracking-wider mb-3">Deployment Risk</h4>
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: riskColor }} />
            <span className="text-lg font-bold capitalize" style={{ color: riskColor }}>
              {gsti?.deployment_risk || "N/A"}
            </span>
          </div>
        </div>
      </div>

      {/* ROI Waterfall */}
      <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-fuzebox-text mb-3 uppercase tracking-wider">
          ROI Waterfall — AI to Agents to Workflows
        </h3>
        <ROIWaterfall
          caitoScore={caito.overall}
          gstiScore={gsti?.overall || 0}
          rawScore={raw?.score}
        />
      </div>

      {/* Pillar Details */}
      <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-fuzebox-text mb-3 uppercase tracking-wider">
          Pillar Breakdown
        </h3>
        <div className="space-y-3">
          {Object.entries(caito.pillars).map(([pillar, data]) => {
            const pct = data.raw * 100;
            const barColor = pct >= 75 ? "#10B981" : pct >= 50 ? "#3B82F6" : pct >= 35 ? "#F59E0B" : "#F43F5E";
            return (
              <div key={pillar}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium capitalize text-fuzebox-text">{pillar}</span>
                  <span className="text-sm font-mono" style={{ color: barColor }}>
                    {pct.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full h-2 bg-fuzebox-deep rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-1000 ease-out"
                    style={{ width: `${pct}%`, backgroundColor: barColor }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
