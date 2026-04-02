"use client";
import { useState } from "react";
import { useAssessment } from "@/hooks/useAssessment";
import ChatInterface from "@/components/ChatInterface";
import Dashboard from "@/components/Dashboard";
import SimulationPanel from "@/components/SimulationPanel";

type Tab = "chat" | "dashboard" | "simulate";

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>("chat");
  const [started, setStarted] = useState(false);
  const {
    messages, scores, phase, isLoading, sendMessage, startAssessment,
  } = useAssessment();

  const handleStart = () => {
    startAssessment("executive", "digital_transformation");
    setStarted(true);
  };

  if (!started) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-fuzebox-navy px-6">
        <div className="max-w-2xl w-full text-center">
          {/* Logo */}
          <div className="mb-8">
            <div className="inline-flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-xl flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2L2 7l10 5 10-5-10-5z" />
                  <path d="M2 17l10 5 10-5" />
                  <path d="M2 12l10 5 10-5" />
                </svg>
              </div>
              <div className="text-left">
                <h1 className="text-2xl font-bold text-fuzebox-text tracking-tight">FuzeBox.AI</h1>
                <p className="text-xs text-fuzebox-cyan font-medium tracking-widest uppercase">AEOS Assess</p>
              </div>
            </div>
          </div>

          <h2 className="text-3xl md:text-4xl font-bold text-fuzebox-text mb-4 leading-tight">
            AI Readiness & Agentic ROI Platform
          </h2>
          <p className="text-fuzebox-dim text-lg mb-8 max-w-lg mx-auto">
            Deep diagnostic scoring engine for enterprise AI transformation.
            CAITO framework, Trust Index, and Return on AI Agents.
          </p>

          {/* Framework badges */}
          <div className="flex flex-wrap justify-center gap-2 mb-10">
            {[
              { name: "CAITO", color: "#3B82F6", desc: "AI Readiness" },
              { name: "GSTI", color: "#06B6D4", desc: "Trust Index" },
              { name: "RAI", color: "#10B981", desc: "Return on AI" },
              { name: "RAIA", color: "#8B5CF6", desc: "Return on Agents" },
              { name: "RAW", color: "#F59E0B", desc: "Agentic Workflows" },
            ].map((fw) => (
              <div
                key={fw.name}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-700/50 bg-fuzebox-surface"
              >
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: fw.color }} />
                <span className="text-xs font-semibold text-fuzebox-text">{fw.name}</span>
                <span className="text-[10px] text-fuzebox-muted">{fw.desc}</span>
              </div>
            ))}
          </div>

          <button
            onClick={handleStart}
            className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white px-8 py-3.5 rounded-xl font-semibold text-lg transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 animate-pulse-glow"
          >
            Begin Assessment
          </button>

          <p className="text-xs text-fuzebox-muted mt-6">
            Built on FuzeBox AEOS&trade; &middot; CAITO &middot; GSTI &middot; Patent Portfolio Protected
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-fuzebox-navy">
      {/* Header */}
      <header className="flex items-center justify-between px-5 py-3 border-b border-gray-700/50 bg-fuzebox-deep/80 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <div>
            <h1 className="text-sm font-bold text-fuzebox-text">FuzeBox AEOS Assess</h1>
            <p className="text-[10px] text-fuzebox-muted">AI Readiness & Agentic ROI Platform</p>
          </div>
        </div>

        {/* Phase indicator */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              phase === "reporting" ? "bg-emerald-400" : "bg-fuzebox-accent animate-pulse"
            }`} />
            <span className="text-xs text-fuzebox-dim capitalize">
              {phase === "onboarding" ? "Getting Started" :
               phase === "assessment" ? "Assessing..." :
               phase === "reporting" ? "Complete" : phase}
            </span>
          </div>

          {/* Live score mini */}
          {scores.caito && (
            <div className="flex items-center gap-3 text-xs">
              <span className="text-fuzebox-muted">CAITO:</span>
              <span className="font-mono font-bold text-fuzebox-accent">
                {(scores.caito.overall * 100).toFixed(0)}
              </span>
              {scores.gsti && (
                <>
                  <span className="text-fuzebox-muted">GSTI:</span>
                  <span className="font-mono font-bold text-fuzebox-cyan">
                    {(scores.gsti.overall * 100).toFixed(0)}
                  </span>
                </>
              )}
            </div>
          )}
        </div>
      </header>

      {/* Tab navigation */}
      <div className="flex border-b border-gray-700/50 bg-fuzebox-deep/50">
        {(
          [
            { key: "chat", label: "Assessment", icon: "M" },
            { key: "dashboard", label: "Dashboard", icon: "D" },
            { key: "simulate", label: "Simulate", icon: "S" },
          ] as const
        ).map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 px-4 py-2.5 text-sm font-medium transition-colors relative ${
              activeTab === tab.key
                ? "text-fuzebox-accent"
                : "text-fuzebox-muted hover:text-fuzebox-text"
            }`}
          >
            {tab.label}
            {activeTab === tab.key && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-fuzebox-accent" />
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "chat" && (
          <ChatInterface
            messages={messages}
            isLoading={isLoading}
            onSendMessage={sendMessage}
            phase={phase}
          />
        )}
        {activeTab === "dashboard" && <Dashboard scores={scores} />}
        {activeTab === "simulate" && (
          <SimulationPanel scores={scores} onSimulate={() => {}} />
        )}
      </div>
    </div>
  );
}
