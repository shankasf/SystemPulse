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
  const raw = data.filter((d) => d.measurement === "memory_usage");
  const byTime = {};
  raw.forEach(({ time, field, value }) => {
    const t = new Date(time).toLocaleTimeString();
    byTime[t] = byTime[t] || { time: t };
    if (field === "total_mb") byTime[t].total_mb = Number(value.toFixed(1));
    if (field === "used_mb") byTime[t].used_mb = Number(value.toFixed(1));
    if (field === "free_mb") byTime[t].free_mb = Number(value.toFixed(1));
    if (field === "swap_mb") byTime[t].swap_mb = Number(value.toFixed(1));
  });
  const series = Object.values(byTime);

  return (
    <>
      <h2>Memory (MB)</h2>
      <LineChart width={300} height={200} data={series}>
        <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
        <XAxis dataKey="time" hide />
        <YAxis />
        <Tooltip />
        <Legend verticalAlign="top" height={24} />
        <Line type="monotone" dataKey="used_mb" name="Used MB" dot={false} />
        <Line type="monotone" dataKey="free_mb" name="Free MB" dot={false} />
        <Line type="monotone" dataKey="swap_mb" name="Swap MB" dot={false} />
      </LineChart>
    </>
  );
}
