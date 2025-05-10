// frontend/src/components/NetworkChart.jsx

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
  // pick out only your network_activity points
  const raw = data.filter((d) => d.measurement === "network_activity");

  // group by timestamp, collecting sent_mb_s & recv_mb_s
  const byTime = {};
  raw.forEach(({ time, field, value }) => {
    const t = new Date(time).toLocaleTimeString();
    byTime[t] = byTime[t] || { time: t, sent_mb_s: 0, recv_mb_s: 0 };
    if (field === "sent_mb_s") byTime[t].sent_mb_s = value;
    if (field === "recv_mb_s") byTime[t].recv_mb_s = value;
  });

  // convert to array, sorted by time if you like
  const series = Object.values(byTime);

  return (
    <>
      <h2>Network Activity</h2>
      <AreaChart width={300} height={200} data={series}>
        <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
        <XAxis dataKey="time" hide />
        <YAxis />
        <Tooltip />
        <Legend verticalAlign="top" height={24} />
        <Area
          type="monotone"
          dataKey="sent_mb_s"
          name="Sent MB/s"
          fill="#8884d8"
          stroke="#8884d8"
          dot={false}
        />
        <Area
          type="monotone"
          dataKey="recv_mb_s"
          name="Recv MB/s"
          fill="#82ca9d"
          stroke="#82ca9d"
          dot={false}
        />
      </AreaChart>
    </>
  );
}
