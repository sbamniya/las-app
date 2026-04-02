"use client";
import { useState } from "react";
import type { AssessmentScores } from "@/types";

interface SimulationPanelProps {
  scores: AssessmentScores;
  onSimulate: (changes: Record<string, number>) => void;
}

export default function SimulationPanel({ scores, onSimulate }: SimulationPanelProps) {
  const [changes, setChanges] = useState<Record<string, number>>({
    culture: 0,
    architecture: 0,
    integration: 0,
    talent: 0,
  });
  const [simResult, setSimResult] = useState<{
    original: number;
    simulated: number;
    delta: number;
  } | null>(null);

  if (!scores.caito) {
    return (
      <div className="flex items-center justify-center h-full text-fuzebox-muted p-6">
        <p>Complete the assessment first to run simulations.</p>
      </div>
    );
  }

  const runSimulation = () => {
    const caito = scores.caito!;
    const originalPillars = caito.pillars;

    let simulated = 0;
    const pillarNames = ["culture", "architecture", "integration", "talent"] as const;
    for (const p of pillarNames) {
      const original = originalPillars[p].raw;
      const improved = Math.min(1.0, Math.max(0.0, original + changes[p] / 100));
      simulated += improved * 0.25;
    }

    const delta = simulated - caito.overall;
    setSimResult({
      original: caito.overall,
      simulated: Math.round(simulated * 1000) / 1000,
      delta: Math.round(delta * 1000) / 1000,
    });
  };

  return (
    <div className="h-full overflow-y-auto p-5 space-y-6">
      <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-fuzebox-text mb-1 uppercase tracking-wider">
          Scenario Simulator
        </h3>
        <p className="text-xs text-fuzebox-muted mb-4">
          Adjust improvement percentages to see projected impact on your CAITO score.
        </p>

        <div className="space-y-5">
          {(["culture", "architecture", "integration", "talent"] as const).map((pillar) => {
            const currentScore = scores.caito!.pillars[pillar].raw;
            return (
              <div key={pillar}>
                <div className="flex justify-between items-center mb-1.5">
                  <span className="text-sm font-medium capitalize text-fuzebox-text">{pillar}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-fuzebox-muted">
                      Current: {(currentScore * 100).toFixed(0)}%
                    </span>
                    <span className="text-xs font-mono text-fuzebox-accent">
                      {changes[pillar] > 0 ? "+" : ""}{changes[pillar]}%
                    </span>
                  </div>
                </div>
                <input
                  type="range"
                  min={-30}
                  max={40}
                  value={changes[pillar]}
                  onChange={(e) =>
                    setChanges((prev) => ({ ...prev, [pillar]: parseInt(e.target.value) }))
                  }
                  className="w-full h-1.5 bg-fuzebox-deep rounded-full appearance-none cursor-pointer accent-fuzebox-accent"
                />
                <div className="flex justify-between text-[10px] text-fuzebox-muted mt-0.5">
                  <span>-30%</span>
                  <span>0</span>
                  <span>+40%</span>
                </div>
              </div>
            );
          })}
        </div>

        <button
          onClick={runSimulation}
          className="mt-5 w-full bg-fuzebox-accent hover:bg-blue-600 text-white rounded-xl py-2.5 font-medium transition-colors"
        >
          Run Simulation
        </button>
      </div>

      {simResult && (
        <div className="bg-fuzebox-surface border border-gray-700/50 rounded-xl p-5 animate-fade-in-up">
          <h3 className="text-sm font-semibold text-fuzebox-text mb-4 uppercase tracking-wider">
            Simulation Results
          </h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-fuzebox-dim">
                {(simResult.original * 100).toFixed(1)}
              </div>
              <div className="text-xs text-fuzebox-muted mt-1">Current CAITO</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-fuzebox-accent">
                {(simResult.simulated * 100).toFixed(1)}
              </div>
              <div className="text-xs text-fuzebox-muted mt-1">Projected CAITO</div>
            </div>
            <div>
              <div
                className={`text-2xl font-bold ${
                  simResult.delta >= 0 ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {simResult.delta >= 0 ? "+" : ""}
                {(simResult.delta * 100).toFixed(1)}
              </div>
              <div className="text-xs text-fuzebox-muted mt-1">Delta</div>
            </div>
          </div>

          <div className="mt-4 p-3 bg-fuzebox-deep rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-fuzebox-muted">Current</span>
              <span className="text-xs text-fuzebox-muted">Projected</span>
            </div>
            <div className="relative h-3 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="absolute h-full bg-fuzebox-muted rounded-full transition-all"
                style={{ width: `${simResult.original * 100}%` }}
              />
              <div
                className="absolute h-full bg-fuzebox-accent rounded-full transition-all"
                style={{ width: `${simResult.simulated * 100}%`, opacity: 0.7 }}
              />
            </div>
          </div>

          <div className="mt-4 text-xs text-fuzebox-dim">
            {simResult.delta > 0.05 ? (
              <p>
                This scenario shows significant improvement potential. Prioritize the pillars
                with the highest improvement sliders to maximize ROI.
              </p>
            ) : simResult.delta > 0 ? (
              <p>
                Moderate improvement projected. Consider increasing investment in
                Architecture and Integration for greater impact.
              </p>
            ) : (
              <p>
                The projected changes show a decrease. Review the pillar adjustments
                to ensure alignment with your transformation goals.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
