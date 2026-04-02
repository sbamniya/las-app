"use client";
import { useState, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import type { ChatMessage, AssessmentScores } from "@/types";

interface UseAssessmentReturn {
  messages: ChatMessage[];
  scores: AssessmentScores;
  phase: string;
  isLoading: boolean;
  assessmentId: string | null;
  conversationId: string | null;
  sendMessage: (content: string) => Promise<void>;
  startAssessment: (mode: string, goal: string, industry?: string) => Promise<void>;
}

// Demo mode: runs entirely client-side without backend
export function useAssessment(): UseAssessmentReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [scores, setScores] = useState<AssessmentScores>({});
  const [phase, setPhase] = useState("welcome");
  const [isLoading, setIsLoading] = useState(false);
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [currentPillar, setCurrentPillar] = useState(0);
  const [pillarScores, setPillarScores] = useState<Record<string, number[]>>({
    culture: [], architecture: [], integration: [], talent: [],
  });

  const pillars = ["culture", "architecture", "integration", "talent"];
  const pillarQuestions: Record<string, string[]> = {
    culture: [
      "How would you describe your organization's relationship with AI today? Is it experimental, strategic, or somewhere in between?",
      "When a new AI initiative is proposed, what does the typical decision-making process look like?",
      "What percentage of your leadership team actively champions AI initiatives versus viewing them as IT projects?",
      "How does your organization handle the tension between innovation speed and risk management?",
    ],
    architecture: [
      "What does your current technology infrastructure look like? Cloud-based, on-premise, or hybrid?",
      "Describe your current cloud architecture. Are you multi-cloud, and how do you manage workload distribution?",
      "What is your API strategy? How many of your core systems expose APIs for integration?",
      "How do you handle data security and access control across your AI systems?",
    ],
    integration: [
      "How connected are your core business systems today? Can data flow between them easily?",
      "How many of your critical business workflows could you automate today with the data and systems you have?",
      "What middleware or integration platforms do you use? How standardized are your integration patterns?",
      "How ready are your systems for AI agent access? Do you have standardized interfaces?",
    ],
    talent: [
      "How would you describe the AI skill level across your organization?",
      "What training or upskilling programs do you have for AI and automation?",
      "Do you have dedicated AI/ML engineers, or is AI development handled by existing software teams?",
      "How prepared is your workforce to collaborate with AI agents?",
    ],
  };

  const heuristicScore = (text: string): number => {
    const lower = text.toLowerCase();
    let score = 0.5;
    const positive = ["established", "mature", "robust", "comprehensive", "advanced", "strategic", "automated", "integrated", "production", "enterprise"];
    const negative = ["no", "none", "haven't", "don't", "manual", "limited", "basic", "early", "struggling", "siloed"];
    const posCount = positive.filter(w => lower.includes(w)).length;
    const negCount = negative.filter(w => lower.includes(w)).length;
    if (posCount > negCount) score = Math.min(0.5 + posCount * 0.08, 0.95);
    else if (negCount > posCount) score = Math.max(0.5 - negCount * 0.08, 0.15);
    const words = text.split(" ").length;
    if (words > 80) score = Math.min(score + 0.05, 0.95);
    if (words < 10) score = Math.max(score - 0.10, 0.10);
    return Math.round(score * 1000) / 1000;
  };

  const computeScores = useCallback((allPillarScores: Record<string, number[]>): AssessmentScores => {
    const avg = (arr: number[]) => arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;
    const c = avg(allPillarScores.culture);
    const a = avg(allPillarScores.architecture);
    const i = avg(allPillarScores.integration);
    const t = avg(allPillarScores.talent);
    const caito = c * 0.25 + a * 0.25 + i * 0.25 + t * 0.25;
    const grade = caito >= 0.9 ? "A" : caito >= 0.8 ? "B" : caito >= 0.7 ? "C" : caito >= 0.6 ? "D" : "F";
    const gsti = c * 0.20 + a * 0.30 + i * 0.30 + t * 0.20;
    const trustLevel = gsti >= 0.8 ? "autonomous" : gsti >= 0.6 ? "trusted" : gsti >= 0.4 ? "conditional" : "untrusted";
    const risk = gsti >= 0.7 ? "low" : gsti >= 0.5 ? "medium" : gsti >= 0.35 ? "high" : "critical";

    return {
      caito: {
        overall: Math.round(caito * 1000) / 1000,
        grade,
        pillars: {
          culture: { raw: Math.round(c * 1000) / 1000, weighted: Math.round(c * 0.25 * 1000) / 1000 },
          architecture: { raw: Math.round(a * 1000) / 1000, weighted: Math.round(a * 0.25 * 1000) / 1000 },
          integration: { raw: Math.round(i * 1000) / 1000, weighted: Math.round(i * 0.25 * 1000) / 1000 },
          talent: { raw: Math.round(t * 1000) / 1000, weighted: Math.round(t * 0.25 * 1000) / 1000 },
        },
      },
      gsti: {
        overall: Math.round(gsti * 1000) / 1000,
        trust_level: trustLevel,
        deployment_risk: risk,
        autonomy_readiness: Math.round((a * 0.35 + i * 0.35 + c * 0.15 + t * 0.15) * 1000) / 1000,
      },
      raw: {
        score: Math.round((caito * 0.3 + gsti * 0.3 + caito * 0.4) * 1000) / 1000,
        grade: caito >= 0.8 ? "B" : "C",
      },
    };
  }, []);

  const startAssessment = useCallback(async (mode: string, goal: string, industry?: string) => {
    const aid = uuidv4();
    const cid = uuidv4();
    setAssessmentId(aid);
    setConversationId(cid);
    setPhase("onboarding");
    setQuestionIndex(0);
    setCurrentPillar(0);
    setPillarScores({ culture: [], architecture: [], integration: [], talent: [] });
    setScores({});

    const greeting: ChatMessage = {
      id: uuidv4(),
      role: "assistant",
      content:
        "Welcome to **FuzeBox AEOS Assess**. I'm your AI transformation diagnostic engine.\n\n" +
        "I'll conduct a comprehensive assessment of your organization's AI readiness using " +
        "the **CAITO framework** — evaluating Culture, Architecture, Integration, and Talent — " +
        "and generate your **Generative System Trust Index (GSTI)**, **Return on AI (RAI)**, " +
        "**Return on AI Agents (RAIA)**, and **Return on Agentic Workflows (RAW)** scores.\n\n" +
        "Before we begin:\n\n" +
        "1. **What industry are you in?** (Gaming/Hospitality, Healthcare, Financial Services, Enterprise SaaS, Automotive, Higher Education, Manufacturing)\n\n" +
        "2. **What is your primary transformation objective?** (Cost reduction, Revenue growth, Automation, Workforce augmentation, Agent deployment, Digital transformation)\n\n" +
        "3. **How deep should we go?**\n" +
        "   - **Quick Scan** (~5 min)\n" +
        "   - **Executive Assessment** (~15-20 min)\n" +
        "   - **Deep Diagnostic** (~45-60 min)\n\n" +
        "Tell me about your organization and what brought you here today.",
      timestamp: new Date(),
    };
    setMessages([greeting]);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    setIsLoading(true);
    const userMsg: ChatMessage = { id: uuidv4(), role: "user", content, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);

    await new Promise(r => setTimeout(r, 800 + Math.random() * 600));

    if (phase === "onboarding") {
      setPhase("assessment");
      const pillar = pillars[0];
      const q = pillarQuestions[pillar][0];
      const reply: ChatMessage = {
        id: uuidv4(),
        role: "assistant",
        content: `Thank you for that context. Let's begin the assessment.\n\n**Starting with Culture** — the foundation of AI transformation.\n\n${q}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, reply]);
      setIsLoading(false);
      return;
    }

    if (phase === "assessment") {
      const score = heuristicScore(content);
      const pillar = pillars[currentPillar];
      const newPillarScores = { ...pillarScores };
      newPillarScores[pillar] = [...newPillarScores[pillar], score];
      setPillarScores(newPillarScores);

      const newScores = computeScores(newPillarScores);
      setScores(newScores);

      const nextQIdx = questionIndex + 1;

      if (nextQIdx >= pillarQuestions[pillar].length) {
        const nextPillar = currentPillar + 1;
        if (nextPillar >= pillars.length) {
          // Assessment complete
          setPhase("reporting");
          const finalScores = computeScores(newPillarScores);
          setScores(finalScores);

          const cs = finalScores.caito!;
          const gs = finalScores.gsti!;

          const report = `## FuzeBox AEOS Assessment Report\n### AI Readiness & Agentic ROI Analysis\n\n---\n\n### CAITO Score: **${cs.overall.toFixed(3)}** (Grade: **${cs.grade}**)\n\n| Pillar | Raw Score | Weighted |\n|--------|-----------|----------|\n| Culture | ${cs.pillars.culture.raw.toFixed(3)} | ${cs.pillars.culture.weighted.toFixed(3)} |\n| Architecture | ${cs.pillars.architecture.raw.toFixed(3)} | ${cs.pillars.architecture.weighted.toFixed(3)} |\n| Integration | ${cs.pillars.integration.raw.toFixed(3)} | ${cs.pillars.integration.weighted.toFixed(3)} |\n| Talent | ${cs.pillars.talent.raw.toFixed(3)} | ${cs.pillars.talent.weighted.toFixed(3)} |\n\n---\n\n### GSTI (Trust Index): **${gs.overall.toFixed(3)}**\n- Trust Level: **${gs.trust_level.charAt(0).toUpperCase() + gs.trust_level.slice(1)}**\n- Deployment Risk: **${gs.deployment_risk.charAt(0).toUpperCase() + gs.deployment_risk.slice(1)}**\n- Autonomy Readiness: **${gs.autonomy_readiness.toFixed(3)}**\n\n---\n\nYour assessment is complete. You can explore the **Dashboard** tab for interactive visualizations, run **Simulations** to see improvement impacts, or ask me any questions about your results.`;

          const reply: ChatMessage = { id: uuidv4(), role: "assistant", content: report, timestamp: new Date() };
          setMessages(prev => [...prev, reply]);
          setIsLoading(false);
          return;
        }

        setCurrentPillar(nextPillar);
        setQuestionIndex(0);
        const nextPillarName = pillars[nextPillar].charAt(0).toUpperCase() + pillars[nextPillar].slice(1);
        const q = pillarQuestions[pillars[nextPillar]][0];
        const reply: ChatMessage = {
          id: uuidv4(),
          role: "assistant",
          content: `Thank you. That gives me a strong picture of your **${pillar.charAt(0).toUpperCase() + pillar.slice(1)}** dimension.\n\nLet's move to **${nextPillarName}**.\n\n${q}`,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, reply]);
      } else {
        setQuestionIndex(nextQIdx);
        const q = pillarQuestions[pillar][nextQIdx];
        const reply: ChatMessage = {
          id: uuidv4(),
          role: "assistant",
          content: q,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, reply]);
      }
      setIsLoading(false);
      return;
    }

    // Reporting phase — answer follow-up questions
    const reply: ChatMessage = {
      id: uuidv4(),
      role: "assistant",
      content: "Your assessment is complete. You can explore the **Dashboard** for interactive visualizations, run **Simulations** to model improvement scenarios, or ask me specific questions about any score or recommendation.",
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, reply]);
    setIsLoading(false);
  }, [phase, currentPillar, questionIndex, pillarScores, computeScores, pillars, pillarQuestions]);

  return { messages, scores, phase, isLoading, assessmentId, conversationId, sendMessage, startAssessment };
}
