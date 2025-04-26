// src/components/NetworkChart.jsx

import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

export default function NetworkChart({ data }) {
  // backend uses measurement="network_activity"
  // and fields "sent_mb_s" / "recv_mb_s"
  const raw = data.filter((d) => d.measurement === "network_activity");
  const byTime = {};

  raw.forEach(({ time, field, value }) => {
    const t = new Date(time).toLocaleTimeString();
    byTime[t] = byTime[t] || { time: t };
    byTime[t][field] = Number(value.toFixed(2));
  });

  const series = Object.values(byTime);

  return (
    <>
      <h2>Network (MB/s)</h2>
      <AreaChart width={300} height={200} data={series}>
        <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Legend verticalAlign="top" height={24} />
        <Area
          type="monotone"
          dataKey="sent_mb_s"
          name="Sent"
          fill="#8884d8"
          stroke="#8884d8"
          dot={false}
        />
        <Area
          type="monotone"
          dataKey="recv_mb_s"
          name="Recv"
          fill="#82ca9d"
          stroke="#82ca9d"
          dot={false}
        />
      </AreaChart>
    </>
  );
}
