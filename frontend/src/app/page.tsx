'use client';

import { useEffect, useRef, useState } from "react";

const FRAMEWORKS = [
  {
    key: "caito",
    label: "CAITO",
    full: "AI Readiness",
    color: "#0066FF",
    icon: "◆",
  },
  {
    key: "gsti",
    label: "GSTI",
    full: "Trust Index",
    color: "#00C896",
    icon: "◇",
  },
  {
    key: "rai",
    label: "RAI",
    full: "Return on AI",
    color: "#FF6B2B",
    icon: "△",
  },
  {
    key: "raia",
    label: "RAIA",
    full: "Return on Agents",
    color: "#8B5CF6",
    icon: "○",
  },
  {
    key: "raw",
    label: "RAW",
    full: "Agentic Workflows",
    color: "#F43F5E",
    icon: "□",
  },
];

const NAV_ITEMS = [
  {
    label: "Assess",
    children: [
      "AI Readiness Scan",
      "Trust Index Audit",
      "Agentic ROI Model",
      "Workflow Scoring",
    ],
  },
  {
    label: "Frameworks",
    children: [
      "CAITO Overview",
      "GSTI Methodology",
      "Units of Potential",
      "Coordination Tax",
    ],
  },
  {
    label: "Benchmarks",
    children: [
      "Industry Comparisons",
      "Maturity Curves",
      "Peer Analysis",
      "Trend Data",
    ],
  },
  {
    label: "Reports",
    children: ["Executive Summary", "Deep Dive", "Action Plan", "Export Data"],
  },
];

const PROMPTS = [
  "How ready is my org for agentic AI?",
  "Score our AI governance maturity",
  "What's our Return on AI Agents?",
  "Map our coordination tax across teams",
  "Benchmark us against industry peers",
  "Identify our highest-ROI automation zones",
];

const SAMPLE_METRICS = [
  { label: "CAITO Score", value: 72, max: 100, color: "#0066FF", delta: "+8" },
  {
    label: "Trust Velocity",
    value: 84,
    max: 100,
    color: "#00C896",
    delta: "+12",
  },
  {
    label: "Coordination Tax",
    value: 31,
    max: 100,
    color: "#F43F5E",
    delta: "-5",
    inverse: true,
  },
  {
    label: "Agentic Readiness",
    value: 58,
    max: 100,
    color: "#8B5CF6",
    delta: "+15",
  },
];

const BENCHMARK_DATA = [
  { category: "Data Infrastructure", you: 78, industry: 62 },
  { category: "AI Governance", you: 65, industry: 54 },
  { category: "Agent Orchestration", you: 42, industry: 38 },
  { category: "Trust Framework", you: 84, industry: 59 },
  { category: "Workflow Automation", you: 71, industry: 67 },
];

// Animated number
interface AnimNumProps {
  target: number;
  duration?: number;
}
function AnimNum({ target, duration = 1200 }: AnimNumProps) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    let start = 0;
    const step = target / (duration / 16);
    const id = setInterval(() => {
      start += step;
      if (start >= target) {
        setVal(target);
        clearInterval(id);
      } else setVal(Math.round(start));
    }, 16);
    return () => clearInterval(id);
  }, [target, duration]);
  return <span>{val}</span>;
}

// Radial gauge
interface GaugeProps {
  value: number;
  max: number;
  color: string;
  size?: number;
  stroke?: number;
}
function Gauge({ value, max, color, size = 80, stroke = 6 }: GaugeProps) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = value / max;
  const [anim, setAnim] = useState(0);
  useEffect(() => {
    const id = setTimeout(() => setAnim(pct), 100);
    return () => clearTimeout(id);
  }, [pct]);
  return (
    <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="#F0F0F0"
        strokeWidth={stroke}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={stroke}
        strokeDasharray={circ}
        strokeDashoffset={circ * (1 - anim)}
        strokeLinecap="round"
        style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1)" }}
      />
    </svg>
  );
}

// Horizontal bar for benchmarks
interface BenchBarProps {
  you: number;
  industry: number;
  color: string;
  delay?: number;
}
function BenchBar({ you, industry, color, delay = 0 }: BenchBarProps) {
  const [show, setShow] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setShow(true), delay);
    return () => clearTimeout(t);
  }, [delay]);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <div
        style={{
          position: "relative",
          height: 8,
          background: "#F4F4F5",
          borderRadius: 4,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            height: "100%",
            borderRadius: 4,
            background: color,
            width: show ? `${you}%` : "0%",
            transition: "width 1s cubic-bezier(.4,0,.2,1)",
          }}
        />
      </div>
      <div
        style={{
          position: "relative",
          height: 6,
          background: "#F4F4F5",
          borderRadius: 3,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            height: "100%",
            borderRadius: 3,
            background: "#D4D4D8",
            width: show ? `${industry}%` : "0%",
            transition: "width 1.2s cubic-bezier(.4,0,.2,1)",
          }}
        />
      </div>
    </div>
  );
}

export default function AEOSAssess() {
  const [activeNav, setActiveNav] = useState<number | null>(null);
  const [query, setQuery] = useState<string>("");
  const [phase, setPhase] = useState<"home" | "assessing" | "results">("home");
  const [activeFramework, setActiveFramework] = useState<string | null>(null);
  const [showMetrics, setShowMetrics] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (phase === "assessing") {
      const t = setTimeout(() => {
        setPhase("results");
        setShowMetrics(true);
      }, 2800);
      return () => clearTimeout(t);
    }
  }, [phase]);

  const handleSubmit = (text?: string) => {
    setQuery(text || query);
    if ((text || query).trim()) setPhase("assessing");
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#FAFAFA",
        fontFamily: "'DM Sans', 'Helvetica Neue', sans-serif",
        color: "#18181B",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500&display=swap"
        rel="stylesheet"
      />

      {/* Subtle grid bg */}
      <div
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 0,
          opacity: 0.35,
          backgroundImage:
            "radial-gradient(circle at 1px 1px, #D4D4D8 0.5px, transparent 0)",
          backgroundSize: "32px 32px",
        }}
      />

      {/* Accent glow */}
      <div
        style={{
          position: "fixed",
          top: -200,
          right: -200,
          width: 600,
          height: 600,
          zIndex: 0,
          background:
            "radial-gradient(circle, rgba(0,102,255,0.06) 0%, transparent 70%)",
          borderRadius: "50%",
        }}
      />

      {/* ── NAV ── */}
      <nav
        style={{
          position: "sticky",
          top: 0,
          zIndex: 100,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 40px",
          height: 64,
          background: "rgba(250,250,250,0.85)",
          backdropFilter: "blur(20px)",
          borderBottom: "1px solid #E4E4E7",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 7,
              background: "linear-gradient(135deg, #0066FF, #00C896)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontSize: 13,
              fontWeight: 700,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            F
          </div>
          <span
            style={{ fontWeight: 700, fontSize: 16, letterSpacing: "-0.02em" }}
          >
            FuzeBox
            <span style={{ color: "#71717A", fontWeight: 400 }}>.AI</span>
          </span>
          <span
            style={{
              marginLeft: 8,
              fontSize: 10,
              fontWeight: 600,
              letterSpacing: "0.08em",
              background: "#F4F4F5",
              color: "#71717A",
              padding: "3px 8px",
              borderRadius: 4,
              fontFamily: "'JetBrains Mono', monospace",
              textTransform: "uppercase",
            }}
          >
            AEOS Assess
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          {NAV_ITEMS.map((item, i) => (
            <div
              key={i}
              style={{ position: "relative" }}
              onMouseEnter={() => setActiveNav(i)}
              onMouseLeave={() => setActiveNav(null)}
            >
              <button
                style={{
                  background: "none",
                  border: "none",
                  padding: "8px 14px",
                  cursor: "pointer",
                  fontSize: 13,
                  fontWeight: 500,
                  color: activeNav === i ? "#18181B" : "#71717A",
                  borderRadius: 8,
                  transition: "all 0.2s",
                  fontFamily: "inherit",
                }}
              >
                {item.label}
                <span style={{ marginLeft: 4, fontSize: 9, opacity: 0.5 }}>
                  ▼
                </span>
              </button>
              {activeNav === i && (
                <div
                  style={{
                    position: "absolute",
                    top: "100%",
                    left: 0,
                    marginTop: 4,
                    background: "#fff",
                    border: "1px solid #E4E4E7",
                    borderRadius: 12,
                    padding: 6,
                    minWidth: 200,
                    boxShadow: "0 12px 40px rgba(0,0,0,0.08)",
                    animation: "fadeIn 0.15s ease",
                  }}
                >
                  {item.children.map((child, j) => (
                    <div
                      key={j}
                      style={{
                        padding: "10px 14px",
                        fontSize: 13,
                        color: "#3F3F46",
                        borderRadius: 8,
                        cursor: "pointer",
                        transition: "background 0.15s",
                      }}
                      onMouseEnter={(e) =>
                        (e.currentTarget.style.background = "#F4F4F5")
                      }
                      onMouseLeave={(e) =>
                        (e.currentTarget.style.background = "transparent")
                      }
                    >
                      {child}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button
            style={{
              background: "none",
              border: "1px solid #E4E4E7",
              padding: "7px 16px",
              borderRadius: 8,
              fontSize: 13,
              fontWeight: 500,
              cursor: "pointer",
              color: "#3F3F46",
              fontFamily: "inherit",
            }}
          >
            Sign In
          </button>
          <button
            style={{
              background: "#18181B",
              border: "none",
              padding: "7px 18px",
              borderRadius: 8,
              fontSize: 13,
              fontWeight: 500,
              cursor: "pointer",
              color: "#fff",
              fontFamily: "inherit",
            }}
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* ── MAIN ── */}
      <main
        style={{
          position: "relative",
          zIndex: 1,
          maxWidth: 1100,
          margin: "0 auto",
          padding: "0 40px",
        }}
      >
        {/* HERO / INPUT */}
        <section
          style={{
            paddingTop: phase === "results" ? 40 : 100,
            transition: "padding-top 0.6s cubic-bezier(.4,0,.2,1)",
            textAlign: "center",
          }}
        >
          {phase === "home" && (
            <>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  background: "#fff",
                  border: "1px solid #E4E4E7",
                  borderRadius: 20,
                  padding: "5px 14px",
                  fontSize: 12,
                  color: "#71717A",
                  marginBottom: 24,
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    background: "#00C896",
                  }}
                />
                Patent Protected · AEOS 12-Layer Architecture
              </div>
              <h1
                style={{
                  fontSize: 52,
                  fontWeight: 700,
                  lineHeight: 1.1,
                  letterSpacing: "-0.035em",
                  margin: "0 0 16px",
                  maxWidth: 700,
                  marginLeft: "auto",
                  marginRight: "auto",
                }}
              >
                Enterprise AI
                <br />
                <span
                  style={{
                    background: "linear-gradient(135deg, #0066FF, #00C896)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                  }}
                >
                  Readiness Engine
                </span>
              </h1>
              <p
                style={{
                  fontSize: 17,
                  color: "#71717A",
                  maxWidth: 520,
                  margin: "0 auto 40px",
                  lineHeight: 1.6,
                  fontWeight: 400,
                }}
              >
                Deep diagnostic scoring across CAITO, Trust Index, Return on AI,
                and Agentic Workflows. Know exactly where you stand.
              </p>
            </>
          )}

          {/* Search / input bar */}
          <div
            style={{
              maxWidth: 680,
              margin: "0 auto",
              background: "#fff",
              borderRadius: 16,
              border: "1px solid #E4E4E7",
              boxShadow:
                phase === "home"
                  ? "0 8px 40px rgba(0,0,0,0.06)"
                  : "0 2px 12px rgba(0,0,0,0.04)",
              padding: 6,
              transition: "box-shadow 0.4s",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 10,
                  background: "linear-gradient(135deg, #0066FF, #00C896)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#fff"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                >
                  <circle cx="11" cy="11" r="7" />
                  <line x1="16.5" y1="16.5" x2="21" y2="21" />
                </svg>
              </div>
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                placeholder="Ask about your AI readiness, trust score, or agentic ROI..."
                style={{
                  flex: 1,
                  border: "none",
                  outline: "none",
                  fontSize: 15,
                  background: "transparent",
                  color: "#18181B",
                  fontFamily: "inherit",
                  padding: "10px 0",
                }}
              />
              <button
                onClick={() => handleSubmit()}
                style={{
                  background: "#18181B",
                  border: "none",
                  borderRadius: 10,
                  padding: "10px 20px",
                  color: "#fff",
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: "pointer",
                  fontFamily: "inherit",
                  whiteSpace: "nowrap",
                }}
              >
                Assess →
              </button>
            </div>
          </div>

          {/* Prompt suggestions */}
          {phase === "home" && (
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                justifyContent: "center",
                gap: 8,
                marginTop: 20,
                maxWidth: 680,
                margin: "20px auto 0",
              }}
            >
              {PROMPTS.slice(0, 4).map((p, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setQuery(p);
                    handleSubmit(p);
                  }}
                  style={{
                    background: "#fff",
                    border: "1px solid #E4E4E7",
                    borderRadius: 10,
                    padding: "8px 14px",
                    fontSize: 12,
                    color: "#52525B",
                    cursor: "pointer",
                    fontFamily: "inherit",
                    transition: "all 0.2s",
                    fontWeight: 450,
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.borderColor =
                      "#0066FF";
                    (e.currentTarget as HTMLButtonElement).style.color =
                      "#0066FF";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.borderColor =
                      "#E4E4E7";
                    (e.currentTarget as HTMLButtonElement).style.color =
                      "#52525B";
                  }}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </section>

        {/* Framework pills */}
        {phase === "home" && (
          <section
            style={{
              display: "flex",
              justifyContent: "center",
              gap: 10,
              marginTop: 48,
              flexWrap: "wrap",
            }}
          >
            {FRAMEWORKS.map((f) => (
              <button
                key={f.key}
                onClick={() =>
                  setActiveFramework(activeFramework === f.key ? null : f.key)
                }
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  background: activeFramework === f.key ? f.color : "#fff",
                  color: activeFramework === f.key ? "#fff" : "#3F3F46",
                  border: `1px solid ${activeFramework === f.key ? f.color : "#E4E4E7"}`,
                  borderRadius: 12,
                  padding: "12px 20px",
                  cursor: "pointer",
                  transition: "all 0.25s",
                  fontFamily: "inherit",
                  fontSize: 13,
                  fontWeight: 500,
                }}
              >
                <span style={{ fontSize: 16, opacity: 0.7 }}>{f.icon}</span>
                <span
                  style={{
                    fontWeight: 700,
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 12,
                  }}
                >
                  {f.label}
                </span>
                <span style={{ opacity: 0.7 }}>{f.full}</span>
              </button>
            ))}
          </section>
        )}

        {/* LOADING STATE */}
        {phase === "assessing" && (
          <div style={{ textAlign: "center", padding: "60px 0" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                gap: 6,
                marginBottom: 24,
              }}
            >
              {[0, 1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: FRAMEWORKS[i].color,
                    animation: `pulse 1.2s ease-in-out ${i * 0.15}s infinite`,
                  }}
                />
              ))}
            </div>
            <p style={{ fontSize: 14, color: "#71717A", fontWeight: 500 }}>
              Running AEOS diagnostic across all five frameworks...
            </p>
            <p
              style={{
                fontSize: 12,
                color: "#A1A1AA",
                marginTop: 8,
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              CAITO → GSTI → RAI → RAIA → RAW
            </p>
          </div>
        )}

        {/* ── RESULTS ── */}
        {phase === "results" && (
          <div style={{ marginTop: 32 }}>
            {/* Answer card */}
            <div
              style={{
                background: "#fff",
                borderRadius: 16,
                border: "1px solid #E4E4E7",
                padding: 32,
                marginBottom: 24,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 16,
                }}
              >
                <div
                  style={{
                    width: 24,
                    height: 24,
                    borderRadius: 6,
                    background: "linear-gradient(135deg, #0066FF, #00C896)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <span
                    style={{ color: "#fff", fontSize: 11, fontWeight: 700 }}
                  >
                    F
                  </span>
                </div>
                <span
                  style={{ fontSize: 13, fontWeight: 600, color: "#71717A" }}
                >
                  AEOS Assessment
                </span>
                <span
                  style={{
                    marginLeft: "auto",
                    fontSize: 11,
                    color: "#A1A1AA",
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                >
                  5 frameworks analyzed
                </span>
              </div>
              <p
                style={{
                  fontSize: 15,
                  lineHeight: 1.7,
                  color: "#3F3F46",
                  margin: 0,
                }}
              >
                Based on your query{" "}
                <strong style={{ color: "#18181B" }}>"{query}"</strong>, here's
                a preliminary diagnostic. Your organization shows{" "}
                <strong style={{ color: "#0066FF" }}>
                  strong trust infrastructure
                </strong>{" "}
                (Trust Velocity at 84th percentile) but has room to grow in{" "}
                <strong style={{ color: "#8B5CF6" }}>
                  agentic orchestration
                </strong>
                . The coordination tax across teams is moderate at 31%,
                suggesting some process overhead in cross-functional AI
                initiatives. We recommend focusing on workflow automation as
                your highest-ROI next step.
              </p>
            </div>

            {/* Metric cards */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: 16,
                marginBottom: 24,
              }}
            >
              {SAMPLE_METRICS.map((m, i) => (
                <div
                  key={i}
                  style={{
                    background: "#fff",
                    borderRadius: 14,
                    border: "1px solid #E4E4E7",
                    padding: 24,
                    textAlign: "center",
                    opacity: showMetrics ? 1 : 0,
                    transform: showMetrics
                      ? "translateY(0)"
                      : "translateY(12px)",
                    transition: `all 0.5s cubic-bezier(.4,0,.2,1) ${i * 0.1}s`,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "center",
                      marginBottom: 12,
                    }}
                  >
                    <div style={{ position: "relative" }}>
                      <Gauge value={m.value} max={m.max} color={m.color} />
                      <div
                        style={{
                          position: "absolute",
                          inset: 0,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: 20,
                          fontWeight: 700,
                          fontFamily: "'JetBrains Mono', monospace",
                          color: m.color,
                        }}
                      >
                        <AnimNum target={m.value} />
                      </div>
                    </div>
                  </div>
                  <div
                    style={{
                      fontSize: 12,
                      fontWeight: 600,
                      color: "#52525B",
                      marginBottom: 4,
                    }}
                  >
                    {m.label}
                  </div>
                  <div
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      color: m.inverse
                        ? m.delta.startsWith("-")
                          ? "#00C896"
                          : "#F43F5E"
                        : m.delta.startsWith("+")
                          ? "#00C896"
                          : "#F43F5E",
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {m.delta} vs last quarter
                  </div>
                </div>
              ))}
            </div>

            {/* Benchmarks */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 16,
                marginBottom: 24,
              }}
            >
              <div
                style={{
                  background: "#fff",
                  borderRadius: 14,
                  border: "1px solid #E4E4E7",
                  padding: 28,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: 20,
                  }}
                >
                  <h3 style={{ fontSize: 14, fontWeight: 700, margin: 0 }}>
                    Industry Benchmark
                  </h3>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 12,
                      fontSize: 11,
                      color: "#A1A1AA",
                    }}
                  >
                    <span
                      style={{ display: "flex", alignItems: "center", gap: 4 }}
                    >
                      <span
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: 2,
                          background: "#0066FF",
                        }}
                      />{" "}
                      You
                    </span>
                    <span
                      style={{ display: "flex", alignItems: "center", gap: 4 }}
                    >
                      <span
                        style={{
                          width: 8,
                          height: 6,
                          borderRadius: 2,
                          background: "#D4D4D8",
                        }}
                      />{" "}
                      Industry Avg
                    </span>
                  </div>
                </div>
                <div
                  style={{ display: "flex", flexDirection: "column", gap: 16 }}
                >
                  {BENCHMARK_DATA.map((b, i) => (
                    <div key={i}>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          marginBottom: 6,
                          fontSize: 12,
                          color: "#52525B",
                        }}
                      >
                        <span style={{ fontWeight: 500 }}>{b.category}</span>
                        <span
                          style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontWeight: 500,
                            color: b.you > b.industry ? "#00C896" : "#F43F5E",
                          }}
                        >
                          {b.you > b.industry ? "+" : ""}
                          {b.you - b.industry}
                        </span>
                      </div>
                      <BenchBar
                        you={b.you}
                        industry={b.industry}
                        color="#0066FF"
                        delay={i * 150}
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Next steps */}
              <div
                style={{
                  background: "#fff",
                  borderRadius: 14,
                  border: "1px solid #E4E4E7",
                  padding: 28,
                }}
              >
                <h3
                  style={{ fontSize: 14, fontWeight: 700, margin: "0 0 20px" }}
                >
                  Recommended Next Steps
                </h3>
                {[
                  {
                    n: "01",
                    t: "Deploy GSTI trust framework scoring",
                    tag: "High Impact",
                    tagColor: "#00C896",
                  },
                  {
                    n: "02",
                    t: "Reduce coordination tax via DODAG cycle",
                    tag: "Quick Win",
                    tagColor: "#0066FF",
                  },
                  {
                    n: "03",
                    t: "Launch agentic workflow pilot (RAW)",
                    tag: "Strategic",
                    tagColor: "#8B5CF6",
                  },
                  {
                    n: "04",
                    t: "Establish Units of Potential baselines",
                    tag: "Foundation",
                    tagColor: "#F43F5E",
                  },
                ].map((s, i) => (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 14,
                      padding: "14px 0",
                      borderBottom: i < 3 ? "1px solid #F4F4F5" : "none",
                    }}
                  >
                    <span
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 11,
                        fontWeight: 600,
                        color: "#A1A1AA",
                        width: 24,
                      }}
                    >
                      {s.n}
                    </span>
                    <span
                      style={{
                        flex: 1,
                        fontSize: 13,
                        fontWeight: 500,
                        color: "#3F3F46",
                      }}
                    >
                      {s.t}
                    </span>
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 600,
                        padding: "3px 8px",
                        borderRadius: 6,
                        background: `${s.tagColor}10`,
                        color: s.tagColor,
                        fontFamily: "'JetBrains Mono', monospace",
                      }}
                    >
                      {s.tag}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Follow-up prompts */}
            <div
              style={{
                background: "#fff",
                borderRadius: 14,
                border: "1px solid #E4E4E7",
                padding: 20,
                marginBottom: 48,
              }}
            >
              <p
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  color: "#A1A1AA",
                  margin: "0 0 12px",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                }}
              >
                Go deeper
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {[
                  "Break down my CAITO score by dimension",
                  "Show trust velocity trend over 6 months",
                  "Compare my RAIA to top-quartile peers",
                  "Generate executive readiness report",
                  "What's driving my coordination tax?",
                  "Model ROI of deploying 10 AI agents",
                ].map((p, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setQuery(p);
                      setPhase("home");
                      setTimeout(() => handleSubmit(p), 100);
                    }}
                    style={{
                      background: "#FAFAFA",
                      border: "1px solid #E4E4E7",
                      borderRadius: 10,
                      padding: "8px 14px",
                      fontSize: 12,
                      color: "#52525B",
                      cursor: "pointer",
                      fontFamily: "inherit",
                      transition: "all 0.2s",
                      fontWeight: 450,
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = "#0066FF";
                      e.currentTarget.style.color = "#0066FF";
                      e.currentTarget.style.background = "#fff";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = "#E4E4E7";
                      e.currentTarget.style.color = "#52525B";
                      e.currentTarget.style.background = "#FAFAFA";
                    }}
                  >
                    {p} →
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer
          style={{
            textAlign: "center",
            padding: "32px 0 48px",
            borderTop: "1px solid #E4E4E7",
            marginTop: 24,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              gap: 8,
              marginBottom: 8,
            }}
          >
            <span
              style={{
                fontSize: 12,
                color: "#A1A1AA",
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              Built on FuzeBox AEOS™
            </span>
            <span style={{ color: "#D4D4D8" }}>·</span>
            <span
              style={{
                fontSize: 12,
                color: "#A1A1AA",
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              USPTO Patent Protected
            </span>
          </div>
          <div style={{ fontSize: 11, color: "#D4D4D8" }}>
            CAITO · GSTI · TUoP · HUoP · AUoP · RoP · TVI · Coordination Tax ·
            DODAG
          </div>
        </footer>
      </main>

      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%, 100% { transform: scale(1); opacity: 0.6; } 50% { transform: scale(1.5); opacity: 1; } }
        * { box-sizing: border-box; margin: 0; }
        ::placeholder { color: #A1A1AA; }
        button:hover { opacity: 0.92; }
        @media (max-width: 768px) {
          nav { padding: 0 16px !important; }
          main { padding: 0 16px !important; }
          h1 { font-size: 36px !important; }
          .metric-grid { grid-template-columns: repeat(2, 1fr) !important; }
        }
      `}</style>
    </div>
  );
}
