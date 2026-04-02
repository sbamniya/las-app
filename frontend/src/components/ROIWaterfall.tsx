"use client";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";

interface ROIWaterfallProps {
  caitoScore: number;
  gstiScore: number;
  rawScore?: number;
}

export default function ROIWaterfall({ caitoScore, gstiScore, rawScore }: ROIWaterfallProps) {
  const data = [
    { name: "CAITO", value: Math.round(caitoScore * 100), color: "#3B82F6" },
    { name: "GSTI", value: Math.round(gstiScore * 100), color: "#06B6D4" },
    { name: "RAW", value: Math.round((rawScore || 0) * 100), color: "#10B981" },
    {
      name: "Total",
      value: Math.round(((caitoScore + gstiScore + (rawScore || 0)) / 3) * 100),
      color: "#8B5CF6",
    },
  ];

  return (
    <div className="w-full h-52">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="name"
            tick={{ fill: "#9CA3AF", fontSize: 12, fontWeight: 600 }}
            axisLine={{ stroke: "#374151" }}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: "#6B7280", fontSize: 10 }}
            axisLine={{ stroke: "#374151" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1F2937",
              border: "1px solid #374151",
              borderRadius: "8px",
              color: "#F9FAFB",
            }}
            formatter={(value: number) => [`${value}%`, "Score"]}
          />
          <ReferenceLine y={70} stroke="#F59E0B" strokeDasharray="4 4" label={{ value: "Target", fill: "#F59E0B", fontSize: 10 }} />
          <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={40}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
