"use client";

interface ScoreGaugeProps {
  score: number;
  label: string;
  grade?: string;
  size?: number;
  color?: string;
  subtitle?: string;
}

export default function ScoreGauge({
  score, label, grade, size = 120, color = "#3B82F6", subtitle,
}: ScoreGaugeProps) {
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = circumference - score * circumference;

  const getColor = (s: number) => {
    if (color !== "#3B82F6") return color;
    if (s >= 0.8) return "#10B981";
    if (s >= 0.6) return "#3B82F6";
    if (s >= 0.4) return "#F59E0B";
    return "#F43F5E";
  };

  const strokeColor = getColor(score);

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#1F2937"
            strokeWidth="6"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth="6"
            strokeDasharray={circumference}
            strokeDashoffset={progress}
            strokeLinecap="round"
            className="animate-score-fill transition-all duration-1000"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-fuzebox-text">
            {(score * 100).toFixed(0)}
          </span>
          {grade && (
            <span
              className="text-xs font-bold px-1.5 py-0.5 rounded mt-0.5"
              style={{ backgroundColor: strokeColor + "30", color: strokeColor }}
            >
              {grade}
            </span>
          )}
        </div>
      </div>
      <span className="text-xs font-semibold text-fuzebox-dim uppercase tracking-wider">{label}</span>
      {subtitle && <span className="text-[10px] text-fuzebox-muted">{subtitle}</span>}
    </div>
  );
}
