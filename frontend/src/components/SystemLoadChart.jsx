import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine,
} from "recharts";

const CORES = 12; // Your system has 12 logical cores

export default function SystemLoadChart({ data }) {
  const raw = data.filter((d) => d.measurement === "system_load");

  const byTime = {};
  raw.forEach(({ time, field, value }) => {
    const t = new Date(time).toLocaleTimeString();
    byTime[t] = byTime[t] || { time: t };
    if (field === "load_1m") byTime[t].load1m = value;
    if (field === "load_5m") byTime[t].load5m = value;
    if (field === "load_15m") byTime[t].load15m = value;
  });

  const series = Object.values(byTime);

  return (
    <>
      <h2>System Load (processes)</h2>
      <small style={{ marginLeft: "8px", color: "#777" }}>
        {`1.0 per core is optimal — you have ${CORES} cores`}
      </small>

      <LineChart width={300} height={200} data={series}>
        <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
        <XAxis dataKey="time" hide />
        <YAxis />
        <Tooltip />
        <Legend verticalAlign="top" height={24} />
        <Line
          type="monotone"
          dataKey="load1m"
          name="1m"
          stroke="#8884d8"
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="load5m"
          name="5m"
          stroke="#82ca9d"
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="load15m"
          name="15m"
          stroke="#d88484"
          dot={false}
        />

        {/* Optional: add reference line at your total core count */}
        <ReferenceLine
          y={CORES}
          stroke="red"
          strokeDasharray="4 4"
          label="CPU Limit"
        />
      </LineChart>
    </>
  );
}
