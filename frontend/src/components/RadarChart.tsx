"use client";
import {
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface RadarChartProps {
  data: { pillar: string; score: number; benchmark?: number }[];
}

export default function RadarChart({ data }: RadarChartProps) {
  const chartData = data.map((d) => ({
    subject: d.pillar.charAt(0).toUpperCase() + d.pillar.slice(1),
    score: Math.round(d.score * 100),
    benchmark: d.benchmark ? Math.round(d.benchmark * 100) : undefined,
    fullMark: 100,
  }));

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadar cx="50%" cy="50%" outerRadius="75%" data={chartData}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: "#9CA3AF", fontSize: 12, fontWeight: 600 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "#6B7280", fontSize: 10 }}
            tickCount={5}
          />
          {chartData[0]?.benchmark !== undefined && (
            <Radar
              name="Industry Benchmark"
              dataKey="benchmark"
              stroke="#F59E0B"
              fill="#F59E0B"
              fillOpacity={0.1}
              strokeDasharray="4 4"
            />
          )}
          <Radar
            name="Your Score"
            dataKey="score"
            stroke="#3B82F6"
            fill="#3B82F6"
            fillOpacity={0.25}
            strokeWidth={2}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1F2937",
              border: "1px solid #374151",
              borderRadius: "8px",
              color: "#F9FAFB",
            }}
          />
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
}
