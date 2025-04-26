// src/components/MemoryChart.jsx

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

export default function MemoryChart({ data }) {
  // 1) Filter out only the memory_usage measurements
  const raw = data.filter((d) => d.measurement === "memory_usage");

  // 2) Group by timestamp (toLocaleTimeString) and collect total_mb & used_mb
  const byTime = {};
  raw.forEach(({ time, field, value }) => {
    const t = new Date(time).toLocaleTimeString();
    byTime[t] = byTime[t] || { time: t };
    if (field === "total_mb") {
      byTime[t].total_mb = Number(value.toFixed(1));
    } else if (field === "used_mb") {
      byTime[t].used_mb = Number(value.toFixed(1));
    }
  });

  // 3) Compute free_mb = total_mb - used_mb
  Object.values(byTime).forEach((pt) => {
    pt.free_mb = Number((pt.total_mb - pt.used_mb).toFixed(1));
  });

  // 4) Convert the map into an array for recharts
  const series = Object.values(byTime);

  return (
    <div>
      <h2>Memory (MB)</h2>
      <LineChart width={300} height={200} data={series}>
        <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
        <XAxis dataKey="time" hide />
        <YAxis />
        <Tooltip />
        <Legend verticalAlign="top" height={24} />
        <Line
          type="monotone"
          dataKey="used_mb"
          name="Used"
          stroke="#82ca9d"
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="free_mb"
          name="Free"
          stroke="#8884d8"
          dot={false}
        />
      </LineChart>
    </div>
  );
}
