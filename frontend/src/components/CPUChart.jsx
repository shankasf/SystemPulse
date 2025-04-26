import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function CPUChart({ data }) {
  const series = data
    .filter((d) => d.measurement === "cpu_usage" && d.field === "usage_pct")
    .map((d) => ({
      time: new Date(d.time).toLocaleTimeString(),
      usage_pct: d.value,
    }));

  return (
    <>
      <h2>CPU Usage (%)</h2>
      <LineChart width={300} height={200} data={series}>
        <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
        <XAxis dataKey="time" hide />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="usage_pct"
          stroke="#8884d8"
          dot={false}
        />
      </LineChart>
    </>
  );
}
